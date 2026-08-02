import json
import sqlite3
from typing import List, Optional, Dict, Any
from app.database.connection import db_manager
from app.models.account import GmailAccount
from app.models.contact import Contact
from app.models.template import EmailTemplate, AttachmentItem
from app.models.campaign import Campaign, CampaignRecipient
from app.models.log_entry import LogEntry
from app.logger import logger

class Repository:
    # --- ACCOUNT REPOSITORY ---
    @staticmethod
    def add_account(account: GmailAccount) -> int:
        with db_manager.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO accounts (email, display_name, refresh_token_encrypted, is_active, sent_today_count, created_at) "
                "VALUES (?, ?, ?, ?, ?, ?)",
                (account.email, account.display_name, account.refresh_token_encrypted,
                 1 if account.is_active else 0, account.sent_today_count, account.created_at)
            )
            conn.commit()
            return cursor.lastrowid

    @staticmethod
    def get_accounts() -> List[GmailAccount]:
        with db_manager.get_connection() as conn:
            rows = conn.execute("SELECT * FROM accounts ORDER BY id DESC").fetchall()
            return [
                GmailAccount(
                    id=row["id"], email=row["email"], display_name=row["display_name"],
                    refresh_token_encrypted=row["refresh_token_encrypted"],
                    is_active=bool(row["is_active"]), sent_today_count=row["sent_today_count"],
                    created_at=row["created_at"]
                ) for row in rows
            ]

    @staticmethod
    def get_account_by_id(account_id: int) -> Optional[GmailAccount]:
        with db_manager.get_connection() as conn:
            row = conn.execute("SELECT * FROM accounts WHERE id = ?", (account_id,)).fetchone()
            if row:
                return GmailAccount(
                    id=row["id"], email=row["email"], display_name=row["display_name"],
                    refresh_token_encrypted=row["refresh_token_encrypted"],
                    is_active=bool(row["is_active"]), sent_today_count=row["sent_today_count"],
                    created_at=row["created_at"]
                )
            return None

    @staticmethod
    def delete_account(account_id: int):
        with db_manager.get_connection() as conn:
            conn.execute("DELETE FROM accounts WHERE id = ?", (account_id,))
            conn.commit()

    # --- CONTACT REPOSITORY ---
    @staticmethod
    def add_contacts_batch(contacts: List[Contact]) -> int:
        inserted = 0
        with db_manager.get_connection() as conn:
            cursor = conn.cursor()
            for c in contacts:
                try:
                    cursor.execute(
                        "INSERT OR IGNORE INTO contacts (company, contact_name, email, country, city, phone, tags, status, custom_fields_json, created_at) "
                        "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                        (c.company, c.contact_name, c.email, c.country, c.city, c.phone, c.tags, c.status, c.custom_fields_json, c.created_at)
                    )
                    if cursor.rowcount > 0:
                        inserted += 1
                except sqlite3.IntegrityError:
                    continue
            conn.commit()
        return inserted

    @staticmethod
    def get_contacts(search: str = "", tag: str = "", status: str = "") -> List[Contact]:
        query = "SELECT * FROM contacts WHERE 1=1"
        params = []
        if search:
            query += " AND (email LIKE ? OR company LIKE ? OR contact_name LIKE ? OR country LIKE ?)"
            s_param = f"%{search}%"
            params.extend([s_param, s_param, s_param, s_param])
        if tag:
            query += " AND tags LIKE ?"
            params.append(f"%{tag}%")
        if status:
            query += " AND status = ?"
            params.append(status)

        query += " ORDER BY id DESC"

        with db_manager.get_connection() as conn:
            rows = conn.execute(query, params).fetchall()
            return [Contact.from_dict(dict(row)) for row in rows]

    @staticmethod
    def get_total_contacts_count() -> int:
        with db_manager.get_connection() as conn:
            row = conn.execute("SELECT COUNT(*) as count FROM contacts").fetchone()
            return row["count"] if row else 0

    @staticmethod
    def delete_all_contacts():
        with db_manager.get_connection() as conn:
            conn.execute("DELETE FROM contacts")
            conn.commit()

    # --- TEMPLATE REPOSITORY ---
    @staticmethod
    def add_template(template: EmailTemplate) -> int:
        with db_manager.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO templates (name, subject, body_content, is_html, variables_json, created_at) "
                "VALUES (?, ?, ?, ?, ?, ?)",
                (template.name, template.subject, template.body_content,
                 1 if template.is_html else 0, template.variables_json, template.created_at)
            )
            conn.commit()
            return cursor.lastrowid

    @staticmethod
    def update_template(template: EmailTemplate):
        with db_manager.get_connection() as conn:
            conn.execute(
                "UPDATE templates SET name=?, subject=?, body_content=?, is_html=?, variables_json=? WHERE id=?",
                (template.name, template.subject, template.body_content,
                 1 if template.is_html else 0, template.variables_json, template.id)
            )
            conn.commit()

    @staticmethod
    def get_templates() -> List[EmailTemplate]:
        with db_manager.get_connection() as conn:
            rows = conn.execute("SELECT * FROM templates ORDER BY id DESC").fetchall()
            result = []
            for r in rows:
                vars_list = json.loads(r["variables_json"]) if r["variables_json"] else []
                result.append(EmailTemplate(
                    id=r["id"], name=r["name"], subject=r["subject"], body_content=r["body_content"],
                    is_html=bool(r["is_html"]), variables=vars_list, created_at=r["created_at"]
                ))
            return result

    @staticmethod
    def get_template_by_id(template_id: int) -> Optional[EmailTemplate]:
        with db_manager.get_connection() as conn:
            row = conn.execute("SELECT * FROM templates WHERE id = ?", (template_id,)).fetchone()
            if row:
                vars_list = json.loads(row["variables_json"]) if row["variables_json"] else []
                return EmailTemplate(
                    id=row["id"], name=row["name"], subject=row["subject"], body_content=row["body_content"],
                    is_html=bool(row["is_html"]), variables=vars_list, created_at=row["created_at"]
                )
            return None

    @staticmethod
    def delete_template(template_id: int):
        with db_manager.get_connection() as conn:
            conn.execute("DELETE FROM templates WHERE id = ?", (template_id,))
            conn.commit()

    # --- ATTACHMENT REPOSITORY ---
    @staticmethod
    def add_attachment(att: AttachmentItem) -> int:
        with db_manager.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT OR REPLACE INTO attachments (filename, filepath, file_size_bytes, mime_type, category, created_at) "
                "VALUES (?, ?, ?, ?, ?, ?)",
                (att.filename, att.filepath, att.file_size_bytes, att.mime_type, att.category, att.created_at)
            )
            conn.commit()
            return cursor.lastrowid

    @staticmethod
    def get_attachments() -> List[AttachmentItem]:
        with db_manager.get_connection() as conn:
            rows = conn.execute("SELECT * FROM attachments ORDER BY id DESC").fetchall()
            return [
                AttachmentItem(
                    id=r["id"], filename=r["filename"], filepath=r["filepath"],
                    file_size_bytes=r["file_size_bytes"], mime_type=r["mime_type"],
                    category=r["category"], created_at=r["created_at"]
                ) for r in rows
            ]

    @staticmethod
    def get_attachments_by_ids(att_ids: List[int]) -> List[AttachmentItem]:
        if not att_ids:
            return []
        placeholders = ",".join("?" for _ in att_ids)
        with db_manager.get_connection() as conn:
            rows = conn.execute(f"SELECT * FROM attachments WHERE id IN ({placeholders})", att_ids).fetchall()
            return [
                AttachmentItem(
                    id=r["id"], filename=r["filename"], filepath=r["filepath"],
                    file_size_bytes=r["file_size_bytes"], mime_type=r["mime_type"],
                    category=r["category"], created_at=r["created_at"]
                ) for r in rows
            ]

    @staticmethod
    def delete_attachment(att_id: int):
        with db_manager.get_connection() as conn:
            conn.execute("DELETE FROM attachments WHERE id = ?", (att_id,))
            conn.commit()

    # --- CAMPAIGN REPOSITORY ---
    @staticmethod
    def create_campaign(campaign: Campaign, contact_ids: List[int]) -> int:
        with db_manager.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO campaigns (name, account_id, template_id, status, min_delay_sec, max_delay_sec, "
                "daily_limit, is_dry_run, subject_override, attachment_ids_json, total_recipients, sent_count, failed_count, created_at) "
                "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (campaign.name, campaign.account_id, campaign.template_id, campaign.status,
                 campaign.min_delay_sec, campaign.max_delay_sec, campaign.daily_limit,
                 1 if campaign.is_dry_run else 0, campaign.subject_override,
                 json.dumps(campaign.attachment_ids), len(contact_ids), 0, 0, campaign.created_at)
            )
            campaign_id = cursor.lastrowid

            recipients_data = [(campaign_id, c_id, "PENDING", 0) for c_id in contact_ids]
            cursor.executemany(
                "INSERT INTO campaign_recipients (campaign_id, contact_id, status, retry_count) VALUES (?, ?, ?, ?)",
                recipients_data
            )
            conn.commit()
            return campaign_id

    @staticmethod
    def update_campaign_status(campaign_id: int, status: str):
        with db_manager.get_connection() as conn:
            conn.execute("UPDATE campaigns SET status = ? WHERE id = ?", (status, campaign_id))
            conn.commit()

    @staticmethod
    def get_campaigns() -> List[Campaign]:
        with db_manager.get_connection() as conn:
            rows = conn.execute("SELECT * FROM campaigns ORDER BY id DESC").fetchall()
            result = []
            for r in rows:
                att_ids = json.loads(r["attachment_ids_json"]) if r["attachment_ids_json"] else []
                result.append(Campaign(
                    id=r["id"], name=r["name"], account_id=r["account_id"], template_id=r["template_id"],
                    status=r["status"], min_delay_sec=r["min_delay_sec"], max_delay_sec=r["max_delay_sec"],
                    daily_limit=r["daily_limit"], is_dry_run=bool(r["is_dry_run"]),
                    subject_override=r["subject_override"], attachment_ids=att_ids,
                    total_recipients=r["total_recipients"], sent_count=r["sent_count"],
                    failed_count=r["failed_count"], created_at=r["created_at"]
                ))
            return result

    @staticmethod
    def get_campaign_by_id(campaign_id: int) -> Optional[Campaign]:
        with db_manager.get_connection() as conn:
            r = conn.execute("SELECT * FROM campaigns WHERE id = ?", (campaign_id,)).fetchone()
            if r:
                att_ids = json.loads(r["attachment_ids_json"]) if r["attachment_ids_json"] else []
                return Campaign(
                    id=r["id"], name=r["name"], account_id=r["account_id"], template_id=r["template_id"],
                    status=r["status"], min_delay_sec=r["min_delay_sec"], max_delay_sec=r["max_delay_sec"],
                    daily_limit=r["daily_limit"], is_dry_run=bool(r["is_dry_run"]),
                    subject_override=r["subject_override"], attachment_ids=att_ids,
                    total_recipients=r["total_recipients"], sent_count=r["sent_count"],
                    failed_count=r["failed_count"], created_at=r["created_at"]
                )
            return None

    @staticmethod
    def get_pending_recipients(campaign_id: int) -> List[Dict[str, Any]]:
        with db_manager.get_connection() as conn:
            query = """
            SELECT cr.id as recipient_id, cr.campaign_id, cr.contact_id, cr.status, cr.retry_count,
                   c.company, c.contact_name, c.email, c.country, c.city, c.phone, c.custom_fields_json
            FROM campaign_recipients cr
            JOIN contacts c ON cr.contact_id = c.id
            WHERE cr.campaign_id = ? AND cr.status IN ('PENDING', 'FAILED')
            ORDER BY cr.id ASC
            """
            rows = conn.execute(query, (campaign_id,)).fetchall()
            return [dict(r) for r in rows]

    @staticmethod
    def update_recipient_status(recipient_id: int, status: str, message_id: str = None, error_reason: str = None, sent_at: str = None):
        with db_manager.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE campaign_recipients SET status=?, message_id=?, error_reason=?, sent_at=?, retry_count = retry_count + 1 WHERE id=?",
                (status, message_id, error_reason, sent_at, recipient_id)
            )
            # Update campaign counters
            row = conn.execute("SELECT campaign_id FROM campaign_recipients WHERE id=?", (recipient_id,)).fetchone()
            if row:
                c_id = row["campaign_id"]
                if status == "SENT":
                    conn.execute("UPDATE campaigns SET sent_count = sent_count + 1 WHERE id=?", (c_id,))
                elif status == "FAILED":
                    conn.execute("UPDATE campaigns SET failed_count = failed_count + 1 WHERE id=?", (c_id,))
            conn.commit()

    # --- LOGS & STATS REPOSITORY ---
    @staticmethod
    def log_email_activity(campaign_id: Optional[int], email: str, status: str, level: str, details: str, timestamp: str):
        with db_manager.get_connection() as conn:
            conn.execute(
                "INSERT INTO email_logs (campaign_id, recipient_email, status, log_level, details, timestamp) "
                "VALUES (?, ?, ?, ?, ?, ?)",
                (campaign_id, email, status, level, details, timestamp)
            )
            conn.commit()

    @staticmethod
    def get_email_logs(limit: int = 200) -> List[LogEntry]:
        with db_manager.get_connection() as conn:
            rows = conn.execute("SELECT * FROM email_logs ORDER BY id DESC LIMIT ?", (limit,)).fetchall()
            return [
                LogEntry(
                    id=r["id"], campaign_id=r["campaign_id"], recipient_email=r["recipient_email"],
                    status=r["status"], log_level=r["log_level"], details=r["details"], timestamp=r["timestamp"]
                ) for r in rows
            ]

    @staticmethod
    def get_dashboard_stats() -> Dict[str, Any]:
        with db_manager.get_connection() as conn:
            total_contacts = conn.execute("SELECT COUNT(*) as c FROM contacts").fetchone()["c"]
            total_campaigns = conn.execute("SELECT COUNT(*) as c FROM campaigns").fetchone()["c"]
            sent_today = conn.execute("SELECT COUNT(*) as c FROM campaign_recipients WHERE status='SENT' AND date(sent_at) = date('now')").fetchone()["c"]
            queued = conn.execute("SELECT COUNT(*) as c FROM campaign_recipients WHERE status='PENDING'").fetchone()["c"]
            failed = conn.execute("SELECT COUNT(*) as c FROM campaign_recipients WHERE status='FAILED'").fetchone()["c"]
            sent_total = conn.execute("SELECT COUNT(*) as c FROM campaign_recipients WHERE status='SENT'").fetchone()["c"]

            total_processed = sent_total + failed
            success_rate = (sent_total / total_processed * 100.0) if total_processed > 0 else 100.0

            return {
                "total_contacts": total_contacts,
                "total_campaigns": total_campaigns,
                "sent_today": sent_today,
                "queued": queued,
                "failed": failed,
                "success_rate": round(success_rate, 1),
                "remaining": queued
            }
