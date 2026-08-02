import os
import zipfile
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any

from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

from app.core.constants import EXPORTS_DIR
from app.models.contact import Contact
from app.models.template import EmailTemplate
from app.services.template_service import template_service
from app.database.repository import Repository
from app.logger import logger

class PerEmailExporter:
    """Generates individual .txt and .pdf files for every email in a campaign, and packages them into a ZIP archive."""

    @staticmethod
    def export_campaign_emails(campaign_id: int) -> Dict[str, Any]:
        campaign = Repository.get_campaign_by_id(campaign_id)
        if not campaign:
            raise ValueError(f"Campaign #{campaign_id} not found.")

        template = Repository.get_template_by_id(campaign.template_id) if campaign.template_id else None
        template_body = template.body_content if template else "Hello {{Contact}},\n\nRe: {{Company}}"
        subject_template = campaign.subject_override or (template.subject if template else "Outreach")

        recipients = Repository.get_pending_recipients(campaign_id)
        if not recipients:
            # If all are already sent, fetch all recipients for campaign
            from app.database.connection import db_manager
            with db_manager.get_connection() as conn:
                query = """
                SELECT cr.id as recipient_id, cr.campaign_id, cr.contact_id, cr.status, cr.retry_count,
                       c.company, c.contact_name, c.email, c.country, c.city, c.phone, c.custom_fields_json
                FROM campaign_recipients cr
                JOIN contacts c ON cr.contact_id = c.id
                WHERE cr.campaign_id = ?
                """
                rows = conn.execute(query, (campaign_id,)).fetchall()
                recipients = [dict(r) for r in rows]

        campaign_export_dir = EXPORTS_DIR / "emails" / f"campaign_{campaign_id}"
        txt_dir = campaign_export_dir / "txt"
        pdf_dir = campaign_export_dir / "pdf"

        txt_dir.mkdir(parents=True, exist_ok=True)
        pdf_dir.mkdir(parents=True, exist_ok=True)

        generated_files = []

        for idx, rec in enumerate(recipients, 1):
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

            rendered_subject = template_service.render(subject_template, contact)
            rendered_body = template_service.render(template_body, contact)

            clean_email = contact.email.replace("@", "_at_").replace(".", "_")
            base_filename = f"mail_{idx}_{clean_email}"

            # 1. Generate Individual TXT File
            txt_filepath = txt_dir / f"{base_filename}.txt"
            txt_content = (
                f"HEADER INFORMATION\n"
                f"==================================================\n"
                f"CAMPAIGN:   {campaign.name} (ID #{campaign_id})\n"
                f"RECIPIENT:  {contact.contact_name} <{contact.email}>\n"
                f"COMPANY:    {contact.company}\n"
                f"COUNTRY:    {contact.country}\n"
                f"SUBJECT:    {rendered_subject}\n"
                f"DATE:       {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
                f"==================================================\n\n"
                f"BODY CONTENT:\n\n"
                f"{rendered_body}\n"
            )
            with open(txt_filepath, "w", encoding="utf-8") as f:
                f.write(txt_content)

            # 2. Generate Individual PDF File
            pdf_filepath = pdf_dir / f"{base_filename}.pdf"
            PerEmailExporter._generate_single_email_pdf(
                pdf_filepath, campaign.name, contact, rendered_subject, rendered_body
            )

            generated_files.append({
                "index": idx,
                "email": contact.email,
                "txt": str(txt_filepath),
                "pdf": str(pdf_filepath)
            })

        # 3. Package all into ZIP bundle
        zip_filepath = EXPORTS_DIR / "emails" / f"campaign_{campaign_id}_emails_bundle.zip"
        with zipfile.ZipFile(zip_filepath, "w", zipfile.ZIP_DEFLATED) as zipf:
            for item in generated_files:
                p_txt = Path(item["txt"])
                p_pdf = Path(item["pdf"])
                zipf.write(p_txt, arcname=f"txt/{p_txt.name}")
                zipf.write(p_pdf, arcname=f"pdf/{p_pdf.name}")

        logger.info(f"Generated per-email TXT & PDF copies for {len(generated_files)} emails in Campaign #{campaign_id}. ZIP bundle: {zip_filepath}")
        return {
            "campaign_id": campaign_id,
            "total_emails": len(generated_files),
            "export_dir": str(campaign_export_dir),
            "zip_bundle": str(zip_filepath),
            "files": generated_files
        }

    @staticmethod
    def _generate_single_email_pdf(filepath: Path, campaign_name: str, contact: Contact, subject: str, body: str):
        doc = SimpleDocTemplate(str(filepath), pagesize=letter)
        styles = getSampleStyleSheet()
        story = []

        title_style = ParagraphStyle(
            'HeaderTitle',
            parent=styles['Heading2'],
            fontSize=16,
            textColor=colors.HexColor('#1E1E2E'),
            spaceAfter=10
        )

        body_style = ParagraphStyle(
            'EmailBody',
            parent=styles['Normal'],
            fontSize=11,
            leading=16,
            textColor=colors.HexColor('#222222')
        )

        story.append(Paragraph(f"TradePilot - Outgoing Email Document", title_style))
        story.append(Spacer(1, 8))

        header_data = [
            ["Campaign", campaign_name],
            ["To Recipient", f"{contact.contact_name} ({contact.email})"],
            ["Company / Country", f"{contact.company} | {contact.country}"],
            ["Subject", subject],
            ["Date Rendered", datetime.now().strftime("%Y-%m-%d %H:%M:%S")]
        ]

        t = Table(header_data, colWidths=[130, 350])
        t.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#F0F0F5')),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.HexColor('#333333')),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#DDDDDD')),
        ]))
        story.append(t)
        story.append(Spacer(1, 15))

        story.append(Paragraph("<b>Email Body Content:</b>", styles['Heading4']))
        story.append(Spacer(1, 6))

        # Convert line breaks to HTML breaks for reportlab
        formatted_body = body.replace("\n", "<br/>")
        story.append(Paragraph(formatted_body, body_style))

        doc.build(story)
