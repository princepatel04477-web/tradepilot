from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QLabel, QTableWidget, QTableWidgetItem, QHeaderView
)
from PySide6.QtCore import Qt
from app.ui.components.stat_card import StatCard
from app.ui.components.progress_bar import CampaignProgressBar
from app.database.repository import Repository
from app.core.events import event_bus

class DashboardPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._init_ui()
        event_bus.campaign_progress.connect(self.on_progress)
        event_bus.email_sent.connect(self.refresh_stats)
        event_bus.email_failed.connect(self.refresh_stats)

    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(20)

        # Header Title
        title_lbl = QLabel("Dashboard Overview")
        title_lbl.setStyleSheet("font-size: 22px; font-weight: bold; color: #CDD6F4;")
        layout.addWidget(title_lbl)

        # Stat Cards Grid (8 counters)
        grid = QGridLayout()
        grid.setSpacing(14)

        self.card_contacts = StatCard("Total Contacts", "0", "#89B4FA")
        self.card_campaigns = StatCard("Campaigns", "0", "#B4BEFE")
        self.card_sent_today = StatCard("Sent Today", "0", "#A6E3A1")
        self.card_queued = StatCard("Queued", "0", "#F9E2AF")
        self.card_failed = StatCard("Failed", "0", "#F38BA8")
        self.card_rate = StatCard("Success Rate", "100%", "#94E2D5")
        self.card_remaining = StatCard("Remaining", "0", "#FAB387")
        self.card_est_time = StatCard("Estimated Time", "--", "#CBA6F7")

        grid.addWidget(self.card_contacts, 0, 0)
        grid.addWidget(self.card_campaigns, 0, 1)
        grid.addWidget(self.card_sent_today, 0, 2)
        grid.addWidget(self.card_queued, 0, 3)
        grid.addWidget(self.card_failed, 1, 0)
        grid.addWidget(self.card_rate, 1, 1)
        grid.addWidget(self.card_remaining, 1, 2)
        grid.addWidget(self.card_est_time, 1, 3)

        layout.addLayout(grid)

        # Live Progress Bar Section
        self.progress_bar = CampaignProgressBar()
        layout.addWidget(self.progress_bar)

        # Recent Activity Table
        layout.addWidget(QLabel("<b>Recent Activity Log</b>"))
        self.activity_table = QTableWidget()
        self.activity_table.setColumnCount(5)
        self.activity_table.setHorizontalHeaderLabels(["ID", "Recipient", "Status", "Level", "Timestamp"])
        self.activity_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        layout.addWidget(self.activity_table)

        self.refresh_stats()

    def refresh_stats(self):
        stats = Repository.get_dashboard_stats()
        self.card_contacts.set_value(str(stats["total_contacts"]))
        self.card_campaigns.set_value(str(stats["total_campaigns"]))
        self.card_sent_today.set_value(str(stats["sent_today"]))
        self.card_queued.set_value(str(stats["queued"]))
        self.card_failed.set_value(str(stats["failed"]))
        self.card_rate.set_value(f"{stats['success_rate']}%")
        self.card_remaining.set_value(str(stats["remaining"]))

        # Populate recent activity table
        logs = Repository.get_email_logs(limit=15)
        self.activity_table.setRowCount(len(logs))
        for row, l in enumerate(logs):
            self.activity_table.setItem(row, 0, QTableWidgetItem(str(l.id)))
            self.activity_table.setItem(row, 1, QTableWidgetItem(l.recipient_email))
            self.activity_table.setItem(row, 2, QTableWidgetItem(l.status))
            self.activity_table.setItem(row, 3, QTableWidgetItem(l.log_level))
            self.activity_table.setItem(row, 4, QTableWidgetItem(l.timestamp))

    def on_progress(self, data: dict):
        processed = data.get("processed", 0)
        total = data.get("total", 0)
        current = data.get("current_email", "")
        eta = data.get("eta_sec", 0)
        self.progress_bar.update_progress(processed, total, current, eta)
        
        mins, secs = divmod(eta, 60)
        self.card_est_time.set_value(f"{mins}m {secs}s")
        self.refresh_stats()
