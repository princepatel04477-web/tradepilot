import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent

# Detect Vercel serverless read-only filesystem environment
IS_VERCEL = os.getenv("VERCEL") == "1" or os.getenv("VERCEL_ENV") is not None or not os.access(str(BASE_DIR), os.W_OK)

if IS_VERCEL:
    DATA_DIR = Path("/tmp")
else:
    DATA_DIR = BASE_DIR

CONFIG_DIR = DATA_DIR / "config" if IS_VERCEL else BASE_DIR / "config"
LOGS_DIR = DATA_DIR / "logs"
EXPORTS_DIR = DATA_DIR / "exports"
CAMPAIGNS_DIR = DATA_DIR / "campaigns"
ASSETS_DIR = BASE_DIR / "assets"
DEFAULT_CONFIG_PATH = CONFIG_DIR / "settings.yaml"
DEFAULT_DB_PATH = DATA_DIR / "tradepilot.db"

# Ensure runtime directories exist
for path in [CONFIG_DIR, LOGS_DIR, EXPORTS_DIR, CAMPAIGNS_DIR, ASSETS_DIR]:
    try:
        path.mkdir(parents=True, exist_ok=True)
    except Exception:
        pass

APP_NAME = "TradePilot"
APP_VERSION = "1.0.0"

GMAIL_SCOPES = ["https://www.googleapis.com/auth/gmail.send"]

# Campaign Status Constants
STATUS_DRAFT = "DRAFT"
STATUS_QUEUED = "QUEUED"
STATUS_RUNNING = "RUNNING"
STATUS_PAUSED = "PAUSED"
STATUS_COMPLETED = "COMPLETED"
STATUS_CANCELLED = "CANCELLED"

# Recipient Status Constants
RECIPIENT_PENDING = "PENDING"
RECIPIENT_SENT = "SENT"
RECIPIENT_FAILED = "FAILED"
RECIPIENT_SKIPPED = "SKIPPED"
