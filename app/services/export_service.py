import os
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any
import pandas as pd

from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

from app.core.constants import EXPORTS_DIR
from app.database.repository import Repository
from app.logger import logger

class ExportService:
    @staticmethod
    def export_logs_to_csv(filepath: str = None) -> str:
        if not filepath:
            filename = f"tradepilot_logs_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
            filepath = str(EXPORTS_DIR / filename)

        logs = Repository.get_email_logs(limit=5000)
        data = [
            {
                "ID": l.id,
                "Campaign ID": l.campaign_id,
                "Recipient": l.recipient_email,
                "Status": l.status,
                "Level": l.log_level,
                "Details": l.details,
                "Timestamp": l.timestamp
            } for l in logs
        ]
        df = pd.DataFrame(data)
        df.to_csv(filepath, index=False)
        logger.info(f"Exported {len(logs)} logs to CSV: {filepath}")
        return filepath

    @staticmethod
    def export_campaign_report_excel(campaign_id: int, filepath: str = None) -> str:
        campaign = Repository.get_campaign_by_id(campaign_id)
        if not campaign:
            raise ValueError(f"Campaign with ID {campaign_id} not found.")

        if not filepath:
            filename = f"campaign_{campaign_id}_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
            filepath = str(EXPORTS_DIR / filename)

        recipients = Repository.get_pending_recipients(campaign_id)
        # Fetch all recipients (both sent & pending)
        with Repository.db_manager.get_connection() as conn:
            query = """
            SELECT cr.id, cr.status, cr.message_id, cr.sent_at, cr.error_reason, cr.retry_count,
                   c.company, c.contact_name, c.email, c.country
            FROM campaign_recipients cr
            JOIN contacts c ON cr.contact_id = c.id
            WHERE cr.campaign_id = ?
            """
            rows = conn.execute(query, (campaign_id,)).fetchall()
            rec_data = [dict(r) for r in rows]

        df_summary = pd.DataFrame([{
            "Campaign ID": campaign.id,
            "Campaign Name": campaign.name,
            "Status": campaign.status,
            "Total Recipients": campaign.total_recipients,
            "Sent Count": campaign.sent_count,
            "Failed Count": campaign.failed_count,
            "Is Dry Run": campaign.is_dry_run,
            "Created At": campaign.created_at
        }])

        df_recipients = pd.DataFrame(rec_data)

        with pd.ExcelWriter(filepath, engine="openpyxl") as writer:
            df_summary.to_excel(writer, sheet_name="Summary", index=False)
            df_recipients.to_excel(writer, sheet_name="Recipients", index=False)

        logger.info(f"Exported Campaign #{campaign_id} report to Excel: {filepath}")
        return filepath

    @staticmethod
    def export_campaign_report_pdf(campaign_id: int, filepath: str = None) -> str:
        campaign = Repository.get_campaign_by_id(campaign_id)
        if not campaign:
            raise ValueError(f"Campaign with ID {campaign_id} not found.")

        if not filepath:
            filename = f"campaign_{campaign_id}_summary.pdf"
            filepath = str(EXPORTS_DIR / filename)

        doc = SimpleDocTemplate(filepath, pagesize=letter)
        styles = getSampleStyleSheet()
        story = []

        title_style = ParagraphStyle(
            'TitleStyle',
            parent=styles['Heading1'],
            fontSize=22,
            textColor=colors.HexColor('#1E1E2E'),
            spaceAfter=12
        )

        story.append(Paragraph(f"TradePilot - Campaign Executive Summary", title_style))
        story.append(Paragraph(f"<b>Campaign Name:</b> {campaign.name} (ID #{campaign.id})", styles['Normal']))
        story.append(Paragraph(f"<b>Date Generated:</b> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", styles['Normal']))
        story.append(Spacer(1, 15))

        # Metrics Table
        data = [
            ["Metric", "Value"],
            ["Status", campaign.status],
            ["Total Recipients", str(campaign.total_recipients)],
            ["Successfully Sent", str(campaign.sent_count)],
            ["Failed", str(campaign.failed_count)],
            ["Dry Run Execution", "Yes" if campaign.is_dry_run else "No"],
            ["Min/Max Delay", f"{campaign.min_delay_sec}s - {campaign.max_delay_sec}s"]
        ]

        t = Table(data, colWidths=[200, 250])
        t.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (1, 0), colors.HexColor('#1E1E2E')),
            ('TEXTCOLOR', (0, 0), (1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
            ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#F5F5F7')),
            ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#DDDDDD')),
        ]))
        story.append(t)
        story.append(Spacer(1, 20))

        doc.build(story)
        logger.info(f"Generated Campaign PDF Report: {filepath}")
        return filepath
