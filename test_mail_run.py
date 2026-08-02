import os
import sys
from pathlib import Path

# Ensure app directory is in path
sys.path.insert(0, str(Path(__file__).parent))

from app.database import init_db, Repository
from app.models.contact import Contact
from app.models.template import EmailTemplate
from app.models.campaign import Campaign
from app.models.account import GmailAccount
from app.services.template_service import template_service
from app.services.campaign_engine import CampaignWorkerThread
from app.logger import logger

def run_test():
    print("=" * 70)
    print("TradePilot - Email Campaign Test Execution")
    print("=" * 70)

    # 1. Initialize Database Schema
    init_db()

    # 2. Add / Verify Contact
    recipient_email = "enquiries@dibellacoffee.com"
    contact = Contact(
        company="Di Bella Coffee",
        contact_name="Procurement Team",
        email=recipient_email,
        country="Australia",
        city="Brisbane",
        tags="Test, Cold Prospect"
    )
    Repository.add_contacts_batch([contact])
    contacts = Repository.get_contacts(search=recipient_email)
    test_contact = contacts[0] if contacts else contact
    print(f"[+] Contact Registered: {test_contact.contact_name} ({test_contact.email}) - {test_contact.company}")

    # 3. Add / Verify Template from varunya_mail_template.md
    template_path = Path("varunya_mail_template.md")
    if template_path.exists():
        with open(template_path, "r", encoding="utf-8") as f:
            template_body = f.read()
    else:
        template_body = "Dear {{Contact}},\n\nI hope you are doing well."

    subject = "Frozen Shrimp Supply"
    template = EmailTemplate(
        name="Frozen Shrimp Supply Template",
        subject=subject,
        body_content=template_body,
        is_html=False,
        variables=template_service.extract_variables(template_body)
    )
    template_id = Repository.add_template(template)
    print(f"[+] Email Template Created: '{template.name}' (ID #{template_id})")

    # 4. Check Accounts
    accounts = Repository.get_accounts()
    account_id = None
    target_sender = "varunyainternational@gmail.com"

    for acc in accounts:
        if acc.email == target_sender:
            account_id = acc.id
            break

    if not account_id:
        acc = GmailAccount(
            email=target_sender,
            display_name="Varunya International Sales",
            is_active=True
        )
        account_id = Repository.add_account(acc)
        print(f"[+] Registered Account in DB: {target_sender} (ID #{account_id})")
    else:
        print(f"[+] Found Existing Account in DB: {target_sender} (ID #{account_id})")

    # 5. Render & Print Preview
    rendered_subject = template_service.render(subject, test_contact)
    rendered_body = template_service.render(template_body, test_contact)

    print("\n" + "-" * 70)
    print("EMAIL PREVIEW (Pre-Flight Check):")
    print("-" * 70)
    print(f"Sender:   {target_sender}")
    print(f"To:       {test_contact.email}")
    print(f"Subject:  {rendered_subject}")
    print("-" * 70)
    print(rendered_body)
    print("-" * 70 + "\n")

    # 6. Create & Execute Test Campaign
    campaign = Campaign(
        name="Frozen Shrimp Supply Test",
        account_id=account_id,
        template_id=template_id,
        status="QUEUED",
        min_delay_sec=1.0,
        max_delay_sec=2.0,
        is_dry_run=True,  # Set to Dry Run by default for immediate safe verification
        subject_override=subject,
        total_recipients=1
    )
    campaign_id = Repository.create_campaign(campaign, [test_contact.id])
    print(f"[+] Created Test Campaign #{campaign_id} (Dry Run Mode)")

    # Run campaign worker thread synchronously for test feedback
    worker = CampaignWorkerThread(campaign_id)
    print("Launch Campaign Queue Dispatcher...")
    worker.run()

    # 7. Check Results
    logs = Repository.get_email_logs(limit=5)
    print("\n" + "=" * 70)
    print("CAMPAIGN LOGS RESULT:")
    print("=" * 70)
    for l in logs:
        print(f"[{l.timestamp}] [{l.status}] {l.recipient_email} - {l.details}")
    print("=" * 70)

if __name__ == "__main__":
    run_test()
