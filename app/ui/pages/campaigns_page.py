from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QTableWidget,
    QTableWidgetItem, QHeaderView, QComboBox, QSpinBox, QDoubleSpinBox, QCheckBox,
    QMessageBox, QFrame, QListWidget, QAbstractItemView
)
from app.models.campaign import Campaign
from app.database.repository import Repository
from app.services.campaign_engine import CampaignWorkerThread
from app.services.export_service import ExportService
from app.core.events import event_bus

class CampaignsPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_worker: CampaignWorkerThread = None
        self._init_ui()

    def _init_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(20)

        # Left Panel: Existing Campaigns List
        left_box = QVBoxLayout()
        left_lbl = QLabel("Campaigns Overview")
        left_lbl.setStyleSheet("font-size: 18px; font-weight: bold; color: #CDD6F4;")

        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["ID", "Name", "Status", "Sent / Total", "Mode"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.cellClicked.connect(self.on_campaign_selected)

        export_btn = QPushButton("📊 Export Selected PDF Report")
        export_btn.setObjectName("SecondaryButton")
        export_btn.clicked.connect(self.export_report)

        left_box.addWidget(left_lbl)
        left_box.addWidget(self.table)
        left_box.addWidget(export_btn)
        layout.addLayout(left_box, stretch=1)

        # Right Panel: Campaign Builder & Controls
        right_frame = QFrame()
        right_frame.setStyleSheet("background-color: #181825; border-radius: 8px; padding: 16px;")
        right_box = QVBoxLayout(right_frame)

        builder_lbl = QLabel("Campaign Builder & Execution Control")
        builder_lbl.setStyleSheet("font-size: 18px; font-weight: bold; color: #89B4FA;")

        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Campaign Name (e.g., Q3 Import Prospecting)")

        self.account_combo = QComboBox()
        self.template_combo = QComboBox()

        self.subject_input = QLineEdit()
        self.subject_input.setPlaceholderText("Subject Override (Optional - overrides template subject)")

        # Delay Settings
        delay_layout = QHBoxLayout()
        delay_layout.addWidget(QLabel("Min Delay (s):"))
        self.min_delay_sp = QDoubleSpinBox()
        self.min_delay_sp.setRange(1, 600)
        self.min_delay_sp.setValue(30)
        delay_layout.addWidget(self.min_delay_sp)

        delay_layout.addWidget(QLabel("Max Delay (s):"))
        self.max_delay_sp = QDoubleSpinBox()
        self.max_delay_sp.setRange(1, 600)
        self.max_delay_sp.setValue(60)
        delay_layout.addWidget(self.max_delay_sp)

        # Daily limit & Dry run
        opts_layout = QHBoxLayout()
        opts_layout.addWidget(QLabel("Daily Limit:"))
        self.daily_limit_sp = QSpinBox()
        self.daily_limit_sp.setRange(1, 10000)
        self.daily_limit_sp.setValue(500)
        opts_layout.addWidget(self.daily_limit_sp)

        self.dry_run_cb = QCheckBox("Dry Run Mode (Simulate without sending real emails)")
        self.dry_run_cb.setChecked(True)
        opts_layout.addWidget(self.dry_run_cb)

        # Control Action Buttons
        ctrl_layout = QHBoxLayout()
        self.start_btn = QPushButton("🚀 Start Campaign")
        self.start_btn.clicked.connect(self.start_campaign)

        self.pause_btn = QPushButton("⏸ Pause")
        self.pause_btn.setObjectName("SecondaryButton")
        self.pause_btn.setEnabled(False)
        self.pause_btn.clicked.connect(self.pause_campaign)

        self.resume_btn = QPushButton("▶ Resume")
        self.resume_btn.setObjectName("SecondaryButton")
        self.resume_btn.setEnabled(False)
        self.resume_btn.clicked.connect(self.resume_campaign)

        self.cancel_btn = QPushButton("🛑 Cancel")
        self.cancel_btn.setObjectName("DangerButton")
        self.cancel_btn.setEnabled(False)
        self.cancel_btn.clicked.connect(self.cancel_campaign)

        ctrl_layout.addWidget(self.start_btn)
        ctrl_layout.addWidget(self.pause_btn)
        ctrl_layout.addWidget(self.resume_btn)
        ctrl_layout.addWidget(self.cancel_btn)

        right_box.addWidget(builder_lbl)
        right_box.addWidget(QLabel("Campaign Name:"))
        right_box.addWidget(self.name_input)
        right_box.addWidget(QLabel("Sender Gmail Account:"))
        right_box.addWidget(self.account_combo)
        right_box.addWidget(QLabel("Email Template:"))
        right_box.addWidget(self.template_combo)
        right_box.addWidget(QLabel("Subject Line Override:"))
        right_box.addWidget(self.subject_input)
        right_box.addLayout(delay_layout)
        right_box.addLayout(opts_layout)
        right_box.addStretch()
        right_box.addLayout(ctrl_layout)

        layout.addWidget(right_frame, stretch=2)

        self.load_dropdowns()
        self.load_campaigns()

    def load_dropdowns(self):
        self.account_combo.clear()
        accounts = Repository.get_accounts()
        if not accounts:
            self.account_combo.addItem("No Connected Gmail Account (Dry Run Only)", None)
        for a in accounts:
            self.account_combo.addItem(f"{a.email} (ID #{a.id})", a.id)

        self.template_combo.clear()
        templates = Repository.get_templates()
        if not templates:
            self.template_combo.addItem("No Templates Available", None)
        for t in templates:
            self.template_combo.addItem(f"{t.name} (Subject: {t.subject})", t.id)

    def load_campaigns(self):
        campaigns = Repository.get_campaigns()
        self.table.setRowCount(len(campaigns))
        for r, c in enumerate(campaigns):
            self.table.setItem(r, 0, QTableWidgetItem(str(c.id)))
            self.table.setItem(r, 1, QTableWidgetItem(c.name))
            self.table.setItem(r, 2, QTableWidgetItem(c.status))
            self.table.setItem(r, 3, QTableWidgetItem(f"{c.sent_count} / {c.total_recipients}"))
            self.table.setItem(r, 4, QTableWidgetItem("DRY RUN" if c.is_dry_run else "LIVE"))

    def start_campaign(self):
        name = self.name_input.text().strip()
        if not name:
            QMessageBox.warning(self, "Validation Error", "Please provide a campaign name.")
            return

        template_id = self.template_combo.currentData()
        if not template_id:
            QMessageBox.warning(self, "Validation Error", "Please select an email template.")
            return

        account_id = self.account_combo.currentData()
        is_dry_run = self.dry_run_cb.isChecked()

        if not is_dry_run and not account_id:
            QMessageBox.warning(self, "Validation Error", "Live email sending requires a connected Gmail Account.")
            return

        contacts = Repository.get_contacts(status="Active")
        if not contacts:
            QMessageBox.warning(self, "No Contacts", "No active contacts found. Please import contacts first.")
            return

        contact_ids = [c.id for c in contacts]

        campaign = Campaign(
            name=name,
            account_id=account_id,
            template_id=template_id,
            status="QUEUED",
            min_delay_sec=self.min_delay_sp.value(),
            max_delay_sec=self.max_delay_sp.value(),
            daily_limit=self.daily_limit_sp.value(),
            is_dry_run=is_dry_run,
            subject_override=self.subject_input.text().strip() or None,
            total_recipients=len(contact_ids)
        )

        campaign_id = Repository.create_campaign(campaign, contact_ids)
        self.load_campaigns()

        # Launch Worker Thread
        self.current_worker = CampaignWorkerThread(campaign_id)
        self.current_worker.finished_signal.connect(self.on_worker_finished)
        self.current_worker.start()

        self.start_btn.setEnabled(False)
        self.pause_btn.setEnabled(True)
        self.cancel_btn.setEnabled(True)
        QMessageBox.information(self, "Campaign Launched", f"Campaign #{campaign_id} started successfully!")

    def pause_campaign(self):
        if self.current_worker:
            self.current_worker.pause()
            self.pause_btn.setEnabled(False)
            self.resume_btn.setEnabled(True)

    def resume_campaign(self):
        if self.current_worker:
            self.current_worker.resume()
            self.pause_btn.setEnabled(True)
            self.resume_btn.setEnabled(False)

    def cancel_campaign(self):
        if self.current_worker:
            self.current_worker.cancel()
            self.start_btn.setEnabled(True)
            self.pause_btn.setEnabled(False)
            self.resume_btn.setEnabled(False)
            self.cancel_btn.setEnabled(False)

    def on_worker_finished(self, campaign_id: int, status: str):
        self.start_btn.setEnabled(True)
        self.pause_btn.setEnabled(False)
        self.resume_btn.setEnabled(False)
        self.cancel_btn.setEnabled(False)
        self.load_campaigns()

    def on_campaign_selected(self, row: int, col: int):
        pass

    def export_report(self):
        curr_row = self.table.currentRow()
        if curr_row < 0:
            QMessageBox.warning(self, "Selection Required", "Please select a campaign from the table first.")
            return
        campaign_id = int(self.table.item(curr_row, 0).text())
        try:
            pdf_path = ExportService.export_campaign_report_pdf(campaign_id)
            QMessageBox.information(self, "Report Exported", f"PDF Executive Summary generated:\n{pdf_path}")
        except Exception as e:
            QMessageBox.critical(self, "Export Failed", str(e))
