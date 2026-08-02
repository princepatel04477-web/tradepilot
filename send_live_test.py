import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from app.database import init_db, Repository, db_manager
from app.gmail.auth import GmailOAuthManager
from app.gmail.client import GmailApiClient
from app.services.template_service import template_service
from app.models.contact import Contact
from app.logger import logger

def run_live_send():
    print("=" * 70)
    print("TradePilot - Live Gmail API Email Test")
    print("=" * 70)

    # 1. Init DB
    init_db()

    # 2. Get Account #2 token (authorized token) and associate with varunyainternational@gmail.com
    acc2 = Repository.get_account_by_id(2)
    if not acc2 or not acc2.refresh_token_encrypted:
        print("[!] No active token found in database. Please authenticate first.")
        return

    # Update account #1 in DB with the valid token
    with db_manager.get_connection() as conn:
        conn.execute("UPDATE accounts SET refresh_token_encrypted = ?, email = 'varunyainternational@gmail.com' WHERE id = 1", (acc2.refresh_token_encrypted,))
        conn.commit()

    # Get valid credentials
    creds = GmailOAuthManager.get_credentials_from_encrypted(acc2.refresh_token_encrypted)
    if not creds:
        print("[!] Failed to obtain Google Credentials from token.")
        return

    gmail_client = GmailApiClient(creds)

    # 3. Target Email & Template
    to_email = "enquiries@dibellacoffee.com"
    subject = "Frozen Shrimp Supply"

    template_path = Path("varunya_mail_template.md")
    with open(template_path, "r", encoding="utf-8") as f:
        template_body = f.read()

    contact = Contact(
        company="Di Bella Coffee",
        contact_name="Procurement Team",
        email=to_email,
        country="Australia"
    )

    rendered_subject = template_service.render(subject, contact)
    rendered_body = template_service.render(template_body, contact)

    print(f"Sender:   varunyainternational@gmail.com")
    print(f"To:       {to_email}")
    print(f"Subject:  {rendered_subject}")
    print("-" * 70)
    print("Sending live email via Official Gmail API...")

    try:
        res = gmail_client.send_email(
            to_email=to_email,
            subject=rendered_subject,
            body_content=rendered_body,
            is_html=False,
            from_email="varunyainternational@gmail.com"
        )
        msg_id = res.get("message_id")
        thread_id = res.get("thread_id")
        print("\n" + "=" * 70)
        print("SUCCESS! EMAIL SENT LIVE VIA GMAIL API")
        print("=" * 70)
        print(f"Gmail Message ID: {msg_id}")
        print(f"Gmail Thread ID:  {thread_id}")
        print(f"Recipient:        {to_email}")
        print("=" * 70)

        from datetime import datetime
        Repository.log_email_activity(
            campaign_id=1,
            email=to_email,
            status="SENT",
            level="INFO",
            details=f"Live email dispatched via Gmail API (Message ID: {msg_id})",
            timestamp=datetime.now().isoformat()
        )
    except Exception as e:
        print(f"\n[!] Live send error: {e}")

if __name__ == "__main__":
    run_live_send()
