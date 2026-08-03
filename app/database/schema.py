from datetime import datetime
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

DEFAULT_TEMPLATE_BODY = """Dear {{Contact}},

I hope you are doing well.

My name is ARYAN KANANI and I represent VARUNYA INTERNATIONAL an exporter of premium-quality frozen shrimp from India.

We specialize in supplying high-quality Vannamei processed in internationally certified facilities.

Our products comply with global food safety standards and are available in various sizes and specifications to meet your market requirements.

Our product range includes:
- Frozen Vannamei Shrimp (Head-On, Headless, Peeled, PD, PDTO, EZ Peel)
- IQF & Block Frozen
- Various counts and packaging options
- Custom private labelling available

Why work with us?
- Consistent premium quality
- Competitive pricing
- Timely shipments
- Flexible packaging according to buyer requirements

Please let me know your required specifications, destination port, and estimated order quantity so we can prepare our best offer.

Thank you for your time. I look forward to the possibility of working together.

Kind regards,

ARYAN KANANI
SALES MANAGING DIRECTOR
VARUNYA INTERNATIONAL
CONTACT: +91 8141888043
Email: varunyainternational@gmail.com
"""

def init_db():
    try:
        db_manager.execute_script(SCHEMA_SQL)
        logger.info("SQLite database schema initialized successfully.")

        now_str = datetime.now().isoformat()
        with db_manager.get_connection() as conn:
            cursor = conn.cursor()
            
            # Ensure default active sender account exists
            cursor.execute("SELECT COUNT(*) FROM accounts")
            if cursor.fetchone()[0] == 0:
                cursor.execute("""
                    INSERT INTO accounts (email, display_name, is_active, created_at)
                    VALUES (?, ?, 1, ?)
                """, ("varunyainternational@gmail.com", "Varunya International Sales", now_str))
            
            # Ensure default template exists
            cursor.execute("SELECT COUNT(*) FROM templates")
            if cursor.fetchone()[0] == 0:
                cursor.execute("""
                    INSERT INTO templates (name, subject, body_content, is_html, variables_json, created_at)
                    VALUES (?, ?, ?, 1, '["Contact", "Company"]', ?)
                """, ("Frozen Shrimp Supply", "Frozen Shrimp Supply", DEFAULT_TEMPLATE_BODY, now_str))
            
            # Ensure default contact exists
            cursor.execute("SELECT COUNT(*) FROM contacts")
            if cursor.fetchone()[0] == 0:
                cursor.execute("""
                    INSERT INTO contacts (company, contact_name, email, country, status, created_at)
                    VALUES (?, ?, ?, ?, 'Active', ?)
                """, ("Di Bella Coffee", "Procurement Team", "enquiries@dibellacoffee.com", "Australia", now_str))
                
            conn.commit()
    except Exception as e:
        logger.error(f"Failed to initialize database schema: {e}")
        raise e
