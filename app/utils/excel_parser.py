from pathlib import Path
import pandas as pd
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet

def create_sample_files(target_dir: Path):
    target_dir.mkdir(parents=True, exist_ok=True)

    # 1. Sample Excel Contacts
    excel_path = target_dir / "sample_contacts.xlsx"
    if not excel_path.exists():
        data = [
            {
                "Company": "Global Trade Logistics Inc",
                "Contact Name": "Alexander Wright",
                "Email": "alexander@globaltradelogistics.com",
                "Country": "United States",
                "City": "New York",
                "Phone": "+1-212-555-0199",
                "Tags": "Wholesale, VIP",
                "Status": "Active"
            },
            {
                "Company": "Pacific Rim Exports Corp",
                "Contact Name": "Mei-Ling Chen",
                "Email": "chen@pacificrimexports.com",
                "Country": "Singapore",
                "City": "Singapore",
                "Phone": "+65-6789-0123",
                "Tags": "Distributor",
                "Status": "Active"
            },
            {
                "Company": "Bavaria Industrial GmbH",
                "Contact Name": "Lukas Weber",
                "Email": "weber@bavariaindustrial.de",
                "Country": "Germany",
                "City": "Munich",
                "Phone": "+49-89-1234567",
                "Tags": "Manufacturer, Lead",
                "Status": "Active"
            }
        ]
        df = pd.DataFrame(data)
        df.to_excel(excel_path, index=False)

    # 2. Sample HTML Template
    template_path = target_dir / "sample_template.html"
    if not template_path.exists():
        html_content = """<!DOCTYPE html>
<html>
<head>
    <style>
        body { font-family: Arial, sans-serif; line-height: 1.6; color: #333333; }
        .container { max-width: 600px; margin: 0 auto; padding: 20px; border: 1px solid #e0e0e0; border-radius: 8px; }
        .header { background-color: #1E1E2E; color: #ffffff; padding: 15px; text-align: center; border-radius: 6px 6px 0 0; }
        .footer { font-size: 12px; color: #777777; margin-top: 20px; border-top: 1px solid #eeeeee; padding-top: 10px; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h2>Trade Collaboration Inquiry</h2>
        </div>
        <p>Dear {{Contact}},</p>
        <p>I hope this email finds you well at <strong>{{Company}}</strong>.</p>
        <p>We are reaching out to introduce our premier export portfolio tailored for partners in {{Country}} (specifically in {{City}}).</p>
        <p>Please find attached our latest product catalogue and company profile for your review.</p>
        <p>Would you be available for a brief call next week to discuss potential synergy?</p>
        <br>
        <p>Best regards,<br><strong>TradePilot Outreach Team</strong></p>
        <div class="footer">
            <p>Sent securely via TradePilot AI-Powered Platform.</p>
        </div>
    </div>
</body>
</html>"""
        with open(template_path, "w", encoding="utf-8") as f:
            f.write(html_content)

    # 3. Sample PDF Profile
    pdf_path = target_dir / "sample_company_profile.pdf"
    if not pdf_path.exists():
        doc = SimpleDocTemplate(str(pdf_path), pagesize=letter)
        styles = getSampleStyleSheet()
        story = [
            Paragraph("<b>TradePilot Global Exports</b>", styles['Heading1']),
            Spacer(1, 10),
            Paragraph("Official Company Profile & Product Catalog 2026.", styles['Normal']),
            Spacer(1, 10),
            Paragraph("We specialize in high-efficiency global supply chain logistics, direct sourcing, and automated trade outreach solutions.", styles['Normal'])
        ]
        doc.build(story)
