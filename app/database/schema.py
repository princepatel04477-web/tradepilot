from app.database.connection import db_manager
from app.logger import logger

SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS accounts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    email TEXT UNIQUE NOT NULL,
    display_name TEXT DEFAULT '',
    refresh_token_encrypted TEXT DEFAULT '',
    is_active INTEGER DEFAULT 1,
    sent_today_count INTEGER DEFAULT 0,
    created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS contacts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    company TEXT DEFAULT '',
    contact_name TEXT DEFAULT '',
    email TEXT UNIQUE NOT NULL,
    country TEXT DEFAULT '',
    city TEXT DEFAULT '',
    phone TEXT DEFAULT '',
    tags TEXT DEFAULT '',
    status TEXT DEFAULT 'Active',
    custom_fields_json TEXT DEFAULT '{}',
    created_at TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_contacts_email ON contacts(email);
CREATE INDEX IF NOT EXISTS idx_contacts_status ON contacts(status);

CREATE TABLE IF NOT EXISTS templates (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT UNIQUE NOT NULL,
    subject TEXT NOT NULL,
    body_content TEXT NOT NULL,
    is_html INTEGER DEFAULT 1,
    variables_json TEXT DEFAULT '[]',
    created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS attachments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    filename TEXT NOT NULL,
    filepath TEXT UNIQUE NOT NULL,
    file_size_bytes INTEGER DEFAULT 0,
    mime_type TEXT DEFAULT '',
    category TEXT DEFAULT 'General',
    created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS campaigns (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    account_id INTEGER,
    template_id INTEGER,
    status TEXT DEFAULT 'DRAFT',
    min_delay_sec REAL DEFAULT 30.0,
    max_delay_sec REAL DEFAULT 60.0,
    daily_limit INTEGER DEFAULT 500,
    is_dry_run INTEGER DEFAULT 1,
    subject_override TEXT,
    attachment_ids_json TEXT DEFAULT '[]',
    total_recipients INTEGER DEFAULT 0,
    sent_count INTEGER DEFAULT 0,
    failed_count INTEGER DEFAULT 0,
    created_at TEXT NOT NULL,
    FOREIGN KEY(account_id) REFERENCES accounts(id) ON DELETE SET NULL,
    FOREIGN KEY(template_id) REFERENCES templates(id) ON DELETE SET NULL
);

CREATE TABLE IF NOT EXISTS campaign_recipients (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    campaign_id INTEGER NOT NULL,
    contact_id INTEGER NOT NULL,
    status TEXT DEFAULT 'PENDING',
    message_id TEXT,
    sent_at TEXT,
    error_reason TEXT,
    retry_count INTEGER DEFAULT 0,
    FOREIGN KEY(campaign_id) REFERENCES campaigns(id) ON DELETE CASCADE,
    FOREIGN KEY(contact_id) REFERENCES contacts(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_cr_campaign_status ON campaign_recipients(campaign_id, status);

CREATE TABLE IF NOT EXISTS email_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    campaign_id INTEGER,
    recipient_email TEXT NOT NULL,
    status TEXT NOT NULL,
    log_level TEXT DEFAULT 'INFO',
    details TEXT DEFAULT '',
    timestamp TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_logs_campaign ON email_logs(campaign_id);
"""

def init_db():
    try:
        db_manager.execute_script(SCHEMA_SQL)
        logger.info("SQLite database schema initialized successfully.")
    except Exception as e:
        logger.error(f"Failed to initialize database schema: {e}")
        raise e
