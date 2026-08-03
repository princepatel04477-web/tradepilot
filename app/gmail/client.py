import base64
import mimetypes
import smtplib
import time
from pathlib import Path
from typing import List, Optional, Dict, Any
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders

from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials

from app.logger import logger
from app.models.template import AttachmentItem

class GmailApiClient:
    """Official Gmail API client for constructing RFC 2822 messages and sending via API or SMTP."""

    def __init__(self, credentials: Credentials):
        self.credentials = credentials
        self._service = build("gmail", "v1", credentials=credentials)

    def create_message(
        self,
        to_email: str,
        subject: str,
        body_content: str,
        is_html: bool = True,
        attachments: Optional[List[AttachmentItem]] = None,
        from_email: Optional[str] = None
    ) -> dict:
        """Constructs an RFC 2822 MIME message and returns base64url encoded dict for Gmail API."""
        message = MIMEMultipart("mixed") if attachments else MIMEMultipart("alternative")
        message["to"] = to_email
        message["subject"] = subject
        if from_email:
            message["from"] = from_email

        # Email body part
        if is_html:
            body_part = MIMEText(body_content, "html", "utf-8")
        else:
            body_part = MIMEText(body_content, "plain", "utf-8")
            
        message.attach(body_part)

        # Attachments
        if attachments:
            for att in attachments:
                file_path = Path(att.filepath)
                if not file_path.exists():
                    logger.warning(f"Attachment file not found: {file_path}")
                    continue

                content_type, encoding = mimetypes.guess_type(str(file_path))
                if content_type is None or encoding is not None:
                    content_type = "application/octet-stream"

                main_type, sub_type = content_type.split("/", 1)
                
                with open(file_path, "rb") as fp:
                    part = MIMEBase(main_type, sub_type)
                    part.set_payload(fp.read())
                
                encoders.encode_base64(part)
                filename = att.filename or file_path.name
                part.add_header("Content-Disposition", "attachment", filename=filename)
                message.attach(part)

        raw_bytes = message.as_bytes()
        encoded_message = base64.urlsafe_b64encode(raw_bytes).decode("utf-8")
        return {"raw": encoded_message}

    def send_email(
        self,
        to_email: str,
        subject: str,
        body_content: str,
        is_html: bool = True,
        attachments: Optional[List[AttachmentItem]] = None,
        from_email: Optional[str] = None
    ) -> Dict[str, Any]:
        """Sends an email via official Gmail API users().messages().send()."""
        raw_msg = self.create_message(to_email, subject, body_content, is_html, attachments, from_email)
        res = self._service.users().messages().send(userId="me", body=raw_msg).execute()
        return {
            "message_id": res.get("id"),
            "thread_id": res.get("threadId"),
            "status": "SENT"
        }

    @staticmethod
    def send_email_smtp(
        from_email: str,
        app_password: str,
        to_email: str,
        subject: str,
        body_content: str,
        is_html: bool = True
    ) -> Dict[str, Any]:
        """Dispatches real live email via Gmail SMTP (smtp.gmail.com:587 TLS) using a 16-character App Password."""
        msg = MIMEMultipart("alternative")
        msg["From"] = f"Varunya International Sales <{from_email}>"
        msg["To"] = to_email
        msg["Subject"] = subject

        mime_type = "html" if is_html else "plain"
        msg.attach(MIMEText(body_content, mime_type, "utf-8"))

        clean_pwd = app_password.replace(" ", "").strip()
        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()
            server.login(from_email, clean_pwd)
            server.send_message(msg)

        msg_id = f"SMTP_{int(time.time()*1000)}"
        logger.info(f"Dispatched live SMTP email to {to_email} via Gmail (Msg ID: {msg_id})")
        return {"message_id": msg_id, "status": "SENT"}
