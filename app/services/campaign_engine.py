import time
import random
from datetime import datetime
from typing import Optional, List
from PySide6.QtCore import QThread, Signal, QMutex, QMutexLocker
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

from app.models.campaign import Campaign
from app.models.contact import Contact
from app.database.repository import Repository
from app.gmail.auth import GmailOAuthManager
from app.gmail.client import GmailApiClient
from app.services.template_service import template_service
from app.core.events import event_bus
from app.logger import logger

class CampaignWorkerThread(QThread):
    """Background QThread executing campaign queue with exponential backoff and randomized delays."""

    progress_updated = Signal(dict)  # sent, failed, total, current_email, eta_sec
    finished_signal = Signal(int, str)  # campaign_id, status

    def __init__(self, campaign_id: int):
        super().__init__()
        self.campaign_id = campaign_id
        self._is_paused = False
        self._is_cancelled = False
        self._mutex = QMutex()

    def pause(self):
        with QMutexLocker(self._mutex):
            self._is_paused = True
            logger.info(f"Campaign #{self.campaign_id} worker requested PAUSE.")

    def resume(self):
        with QMutexLocker(self._mutex):
            self._is_paused = False
            logger.info(f"Campaign #{self.campaign_id} worker requested RESUME.")

    def cancel(self):
        with QMutexLocker(self._mutex):
            self._is_cancelled = True
            logger.info(f"Campaign #{self.campaign_id} worker requested CANCEL.")

    @retry(
        retry=retry_if_exception_type(Exception),
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        reraise=True
    )
    def _send_email_with_retry(self, client: GmailApiClient, to_email: str, subject: str, body: str, is_html: bool, attachments: list) -> dict:
        return client.send_email(
            to_email=to_email,
            subject=subject,
            body_content=body,
            is_html=is_html,
            attachments=attachments
        )

    def run(self):
        campaign = Repository.get_campaign_by_id(self.campaign_id)
        if not campaign:
            logger.error(f"Cannot start campaign #{self.campaign_id}: Not found.")
            self.finished_signal.emit(self.campaign_id, "FAILED")
            return

        Repository.update_campaign_status(self.campaign_id, "RUNNING")
        event_bus.campaign_status_changed.emit(self.campaign_id, "RUNNING")
        logger.info(f"Started campaign queue for '{campaign.name}' (Dry Run: {campaign.is_dry_run}).")

        # Load Template
        template = Repository.get_template_by_id(campaign.template_id) if campaign.template_id else None
        template_body = template.body_content if template else "Hello {{Contact}},\n\nRe: {{Company}}"
        subject_template = campaign.subject_override or (template.subject if template else "Outreach from TradePilot")
        is_html = template.is_html if template else True

        # Load Attachments
        attachments = Repository.get_attachments_by_ids(campaign.attachment_ids) if campaign.attachment_ids else []

        # Load Gmail Client if not dry run
        gmail_client = None
        if not campaign.is_dry_run:
            account = Repository.get_account_by_id(campaign.account_id) if campaign.account_id else None
            if not account or not account.refresh_token_encrypted:
                logger.error(f"Campaign #{self.campaign_id} requires active Gmail account.")
                Repository.update_campaign_status(self.campaign_id, "FAILED")
                self.finished_signal.emit(self.campaign_id, "FAILED")
                return

            creds = GmailOAuthManager.get_credentials_from_encrypted(account.refresh_token_encrypted)
            if not creds:
                logger.error("Failed to authenticate Gmail credentials.")
                Repository.update_campaign_status(self.campaign_id, "FAILED")
                self.finished_signal.emit(self.campaign_id, "FAILED")
                return
            gmail_client = GmailApiClient(creds)

        recipients = Repository.get_pending_recipients(self.campaign_id)
        total_recipients = len(recipients)
        processed = 0

        for rec in recipients:
            # Check for cancellation
            with QMutexLocker(self._mutex):
                if self._is_cancelled:
                    Repository.update_campaign_status(self.campaign_id, "CANCELLED")
                    event_bus.campaign_status_changed.emit(self.campaign_id, "CANCELLED")
                    logger.info(f"Campaign #{self.campaign_id} cancelled.")
                    self.finished_signal.emit(self.campaign_id, "CANCELLED")
                    return

            # Check for pause state loop
            while True:
                with QMutexLocker(self._mutex):
                    if self._is_cancelled:
                        Repository.update_campaign_status(self.campaign_id, "CANCELLED")
                        self.finished_signal.emit(self.campaign_id, "CANCELLED")
                        return
                    if not self._is_paused:
                        break
                time.sleep(1)

            # Build contact domain model
            contact = Contact(
                id=rec["contact_id"],
                company=rec.get("company", ""),
                contact_name=rec.get("contact_name", ""),
                email=rec["email"],
                country=rec.get("country", ""),
                city=rec.get("city", ""),
                phone=rec.get("phone", ""),
                custom_fields=rec.get("custom_fields_json", {})
            )

            # Render personalized content
            rendered_subject = template_service.render(subject_template, contact)
            rendered_body = template_service.render(template_body, contact)

            # Randomized Sending Delay
            delay_sec = random.uniform(campaign.min_delay_sec, campaign.max_delay_sec)
            logger.info(f"Preparing recipient '{contact.email}' (Random Delay: {round(delay_sec, 1)}s)...")

            sent_at = datetime.now().isoformat()
            try:
                if campaign.is_dry_run:
                    # Dry Run Simulation
                    time.sleep(min(delay_sec, 2.0))  # Capped short delay for dry run responsiveness
                    msg_id = f"DRY_RUN_{random.randint(10000,99999)}"
                    Repository.update_recipient_status(rec["recipient_id"], "SENT", message_id=msg_id, sent_at=sent_at)
                    Repository.log_email_activity(self.campaign_id, contact.email, "DRY_RUN_SUCCESS", "INFO", f"Simulated send to {contact.email}", sent_at)
                    event_bus.email_sent.emit({"email": contact.email, "status": "DRY_RUN"})
                else:
                    # Real Gmail API Dispatch
                    time.sleep(delay_sec)
                    res = self._send_email_with_retry(
                        gmail_client, contact.email, rendered_subject, rendered_body, is_html, attachments
                    )
                    msg_id = res.get("message_id")
                    Repository.update_recipient_status(rec["recipient_id"], "SENT", message_id=msg_id, sent_at=sent_at)
                    Repository.log_email_activity(self.campaign_id, contact.email, "SENT", "INFO", f"Successfully dispatched via Gmail API (Msg ID: {msg_id})", sent_at)
                    event_bus.email_sent.emit({"email": contact.email, "status": "SENT"})

            except Exception as e:
                err_msg = str(e)
                logger.error(f"Failed to send email to {contact.email}: {err_msg}")
                Repository.update_recipient_status(rec["recipient_id"], "FAILED", error_reason=err_msg, sent_at=sent_at)
                Repository.log_email_activity(self.campaign_id, contact.email, "FAILED", "ERROR", f"Failure: {err_msg}", sent_at)
                event_bus.email_failed.emit({"email": contact.email, "error": err_msg})

            processed += 1
            remaining = total_recipients - processed
            avg_delay = (campaign.min_delay_sec + campaign.max_delay_sec) / 2.0
            eta_sec = int(remaining * avg_delay)

            progress_data = {
                "campaign_id": self.campaign_id,
                "processed": processed,
                "total": total_recipients,
                "current_email": contact.email,
                "eta_sec": eta_sec
            }
            self.progress_updated.emit(progress_data)
            event_bus.campaign_progress.emit(progress_data)

        Repository.update_campaign_status(self.campaign_id, "COMPLETED")
        event_bus.campaign_status_changed.emit(self.campaign_id, "COMPLETED")
        logger.info(f"Campaign #{self.campaign_id} queue finished successfully.")
        self.finished_signal.emit(self.campaign_id, "COMPLETED")
