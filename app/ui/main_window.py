from PySide6.QtWidgets import QMainWindow, QWidget, QHBoxLayout, QStackedWidget
from app.ui.components.sidebar import Sidebar
from app.ui.pages.dashboard_page import DashboardPage
from app.ui.pages.campaigns_page import CampaignsPage
from app.ui.pages.contacts_page import ContactsPage
from app.ui.pages.templates_page import TemplatesPage
from app.ui.pages.attachments_page import AttachmentsPage
from app.ui.pages.gmail_page import GmailPage
from app.ui.pages.logs_page import LogsPage
from app.ui.pages.settings_page import SettingsPage
from app.ui.theme import DARK_THEME_QSS

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("TradePilot - AI-Powered Email Outreach Platform")
        self.resize(1280, 800)
        self.setStyleSheet(DARK_THEME_QSS)
        self._init_ui()

    def _init_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Sidebar
        self.sidebar = Sidebar()
        main_layout.addWidget(self.sidebar)

        # Stacked Pages
        self.stacked_widget = QStackedWidget()
        
        self.page_dashboard = DashboardPage()
        self.page_campaigns = CampaignsPage()
        self.page_contacts = ContactsPage()
        self.page_templates = TemplatesPage()
        self.page_attachments = AttachmentsPage()
        self.page_gmail = GmailPage()
        self.page_logs = LogsPage()
        self.page_settings = SettingsPage()

        self.stacked_widget.addWidget(self.page_dashboard)
        self.stacked_widget.addWidget(self.page_campaigns)
        self.stacked_widget.addWidget(self.page_contacts)
        self.stacked_widget.addWidget(self.page_templates)
        self.stacked_widget.addWidget(self.page_attachments)
        self.stacked_widget.addWidget(self.page_gmail)
        self.stacked_widget.addWidget(self.page_logs)
        self.stacked_widget.addWidget(self.page_settings)

        main_layout.addWidget(self.stacked_widget)

        self.sidebar.page_changed.connect(self.switch_page)

    def switch_page(self, index: int):
        self.stacked_widget.setCurrentIndex(index)
        # Refresh dropdowns / lists when switching tabs
        if index == 0:
            self.page_dashboard.refresh_stats()
        elif index == 1:
            self.page_campaigns.load_dropdowns()
            self.page_campaigns.load_campaigns()
        elif index == 2:
            self.page_contacts.load_contacts()
        elif index == 3:
            self.page_templates.load_templates()
        elif index == 4:
            self.page_attachments.load_attachments()
        elif index == 5:
            self.page_gmail.load_accounts()
