import os
import shutil
from pathlib import Path
from typing import Optional, List
from fastapi import FastAPI, File, UploadFile, Form, HTTPException, BackgroundTasks
from fastapi.responses import HTMLResponse, FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

from app.database import init_db, Repository
from app.models.contact import Contact
from app.models.template import EmailTemplate
from app.models.campaign import Campaign
from app.services.contact_service import ContactService
from app.services.template_service import template_service
from app.services.email_exporter import PerEmailExporter
from app.services.export_service import ExportService
from app.services.campaign_engine import CampaignWorkerThread
from app.logger import logger

# Initialize database schema on startup
init_db()

app = FastAPI(
    title="TradePilot - AI Outreach Platform",
    version="1.0.0",
    description="Remote Web Interface and API for TradePilot Outreach Engine"
)

BASE_DIR = Path(__file__).resolve().parent.parent
WEB_DIR = BASE_DIR / "app" / "web"
STATIC_DIR = WEB_DIR / "static"
TEMPLATES_DIR = WEB_DIR / "templates"

if STATIC_DIR.exists():
    app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

@app.get("/", response_class=HTMLResponse)
def read_root():
    index_file = TEMPLATES_DIR / "index.html"
    if index_file.exists():
        with open(index_file, "r", encoding="utf-8") as f:
            return f.read()
    return "<h1>TradePilot Web Server Running</h1><p>Visit /docs for API documentation.</p>"

@app.get("/api/stats")
def get_stats():
    return Repository.get_dashboard_stats()

@app.get("/api/contacts")
def get_contacts(search: str = "", status: str = ""):
    contacts = Repository.get_contacts(search=search, status=status)
    return [
        {
            "id": c.id, "company": c.company, "contact_name": c.contact_name,
            "email": c.email, "country": c.country, "city": c.city,
            "phone": c.phone, "tags": c.tags, "status": c.status
        } for c in contacts
    ]

@app.post("/api/contacts/upload")
async def upload_contacts(file: UploadFile = File(...)):
    temp_dir = BASE_DIR / "exports" / "uploads"
    temp_dir.mkdir(parents=True, exist_ok=True)
    temp_path = temp_dir / file.filename

    with open(temp_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    res = ContactService.import_contacts_to_db(str(temp_path))
    return res

@app.get("/api/templates")
def get_templates():
    templates = Repository.get_templates()
    return [
        {
            "id": t.id, "name": t.name, "subject": t.subject,
            "body_content": t.body_content, "is_html": t.is_html,
            "variables": t.variables
        } for t in templates
    ]

@app.post("/api/templates")
def create_template(name: str = Form(...), subject: str = Form(...), body_content: str = Form(...), is_html: bool = Form(True)):
    valid, err = template_service.validate_template_syntax(body_content)
    if not valid:
        raise HTTPException(status_code=400, detail=f"Syntax Error: {err}")

    vars_list = template_service.extract_variables(body_content)
    template = EmailTemplate(
        name=name, subject=subject, body_content=body_content,
        is_html=is_html, variables=vars_list
    )
    t_id = Repository.add_template(template)
    return {"id": t_id, "status": "created"}

@app.get("/api/campaigns")
def get_campaigns():
    campaigns = Repository.get_campaigns()
    return [
        {
            "id": c.id, "name": c.name, "status": c.status,
            "total_recipients": c.total_recipients, "sent_count": c.sent_count,
            "failed_count": c.failed_count, "is_dry_run": c.is_dry_run,
            "created_at": c.created_at
        } for c in campaigns
    ]

@app.post("/api/campaigns/create")
def create_campaign(
    name: str = Form(...),
    template_id: int = Form(...),
    subject_override: Optional[str] = Form(None),
    min_delay: float = Form(30.0),
    max_delay: float = Form(60.0),
    is_dry_run: bool = Form(True)
):
    contacts = Repository.get_contacts(status="Active")
    if not contacts:
        raise HTTPException(status_code=400, detail="No active contacts found in database.")

    contact_ids = [c.id for c in contacts]
    account = Repository.get_accounts()
    account_id = account[0].id if account else None

    campaign = Campaign(
        name=name,
        account_id=account_id,
        template_id=template_id,
        status="QUEUED",
        min_delay_sec=min_delay,
        max_delay_sec=max_delay,
        is_dry_run=is_dry_run,
        subject_override=subject_override,
        total_recipients=len(contact_ids)
    )

    campaign_id = Repository.create_campaign(campaign, contact_ids)
    
    # Automatically generate per-email PDF & TXT export bundle
    export_res = PerEmailExporter.export_campaign_emails(campaign_id)

    return {
        "campaign_id": campaign_id,
        "status": "created",
        "total_recipients": len(contact_ids),
        "pdf_txt_export": export_res
    }

@app.get("/api/campaigns/{campaign_id}/export-bundle")
def download_export_bundle(campaign_id: int):
    export_res = PerEmailExporter.export_campaign_emails(campaign_id)
    zip_path = Path(export_res["zip_bundle"])
    if not zip_path.exists():
        raise HTTPException(status_code=404, detail="Export bundle ZIP file not found.")
    return FileResponse(
        path=str(zip_path),
        filename=f"campaign_{campaign_id}_pdf_txt_bundle.zip",
        media_type="application/zip"
    )

@app.get("/api/logs")
def get_logs(limit: int = 100):
    logs = Repository.get_email_logs(limit=limit)
    return [
        {
            "id": l.id, "email": l.recipient_email, "status": l.status,
            "level": l.log_level, "details": l.details, "timestamp": l.timestamp
        } for l in logs
    ]
