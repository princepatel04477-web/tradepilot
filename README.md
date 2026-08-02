# TradePilot — AI-Powered Email Outreach Platform

TradePilot is an enterprise-grade desktop application engineered for import/export businesses, global trade networks, and outreach managers. Built with Python 3.12, PySide6 (Qt6), SQLite, and the official Gmail API (OAuth 2.0), TradePilot enables personalized mass email campaigns, attachments management, real-time tracking, and modular AI extensibility.

---

## 🌟 Key Features

- **Modern Dark Interface**: Custom PySide6 Qt6 interface with Catppuccin / VS Code dark styling, responsive sidebar, and animated dashboard cards.
- **Official Gmail API OAuth 2.0**: Secure authentication via Google InstalledAppFlow. Tokens are encrypted using AES-128-CBC (`cryptography` Fernet). No SMTP passwords required.
- **Smart Contact Import**: High-performance Excel (`.xlsx`, `.xls`) and CSV parsing powered by `pandas` and `openpyxl`. Automatic email validation (`email-validator`), deduplication, custom fields, and search/filter.
- **Jinja2 Personalization Engine**: Render dynamic email templates with placeholders like `{{Contact}}`, `{{Company}}`, `{{Country}}`, `{{City}}`, `{{Email}}`, and `{{Custom.<field>}}`. Includes live pre-flight HTML preview modal.
- **Media & Document Catalog**: Attach multi-file catalogues, PDFs, DOCX files, and images with automatic Gmail 25 MB size validation and MIME detection.
- **Background Campaign Queue**: `QThread`-isolated dispatcher with non-deterministic randomized sending delays (e.g., 42s, 58s, 37s), `tenacity` exponential backoff retries, pause/resume/cancel controls, and a **Dry Run Mode** for zero-risk testing.
- **Real-Time Dashboard & ETA**: 8 metric counters, live activity log table, and progress bar calculating real-time ETA.
- **Reporting & Analytics**: Export campaign reports and logs to CSV, Excel, and executive summary PDF reports (`reportlab`).
- **Future-Ready AI Architecture**: Abstract `AIServiceInterface` for AI subject line generation, email rewriter, tone adjustment, and deliverability spam scoring.

---

## 📁 Repository Structure

```
TradePilot/
├── app/
│   ├── core/                  # Configuration, constants, PySide6 EventBus
│   ├── database/              # SQLite Connection pool, DDL schema, Repository
│   ├── gmail/                 # OAuth 2.0 auth flow, Fernet token encryption, Gmail API client
│   ├── models/                # Dataclasses (Contact, Template, Campaign, Account, Log)
│   ├── services/              # Contact import, Jinja2 rendering, attachments, campaign queue engine, reports
│   ├── ai/                    # Abstract AI extension interface
│   ├── logger/                # Loguru file sink & Qt Signal UI stream
│   ├── ui/                    # PySide6 UI views, dark theme QSS, sidebar, dashboard, modals
│   └── utils/                 # Regex validators, sample data generator
├── config/                    # YAML configuration settings
├── sample_data/               # Sample contacts Excel, HTML template, PDF catalog
├── tests/                     # pytest automated test suite
├── main.py                    # Application Entrypoint
└── requirements.txt           # Python dependencies
```

---

## 🛠 Quick Start & Installation

### 1. Prerequisites
- Python 3.12+ installed
- Google Cloud Project with Gmail API enabled (optional for Live sending, Dry Run works out of the box)

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Run Application
```bash
python main.py
```

### 4. Run Automated Tests
```bash
python -m pytest tests/ -v
```

---

## 🔑 Gmail OAuth 2.0 Setup (Live Sending)

1. Go to the [Google Cloud Console](https://console.cloud.google.com/).
2. Create a new project and enable the **Gmail API**.
3. Configure the **OAuth Consent Screen** (Desktop App).
4. Create **OAuth 2.0 Client Credentials** and download the `credentials.json` file.
5. In TradePilot, navigate to **Gmail Accounts** tab -> Click **Connect Gmail Account** -> Select `credentials.json`.
6. Authorize the application in your browser.

---

## 📦 Packaging Executable (PyInstaller)

To build a standalone single-file Windows executable:
```bash
pip install pyinstaller
pyinstaller --noconfirm --onedir --windowed --name "TradePilot" --add-data "config;config" --add-data "assets;assets" main.py
```
The compiled executable will be generated under `dist/TradePilot/TradePilot.exe`.

---

## 📜 License & Author

- Developed for commercial and enterprise outreach applications.
- Built following Clean Architecture & SOLID Principles.
