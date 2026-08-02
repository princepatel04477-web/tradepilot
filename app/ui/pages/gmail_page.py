from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QTableWidget,
    QTableWidgetItem, QHeaderView, QFileDialog, QMessageBox, QFrame
)
from app.models.account import GmailAccount
from app.database.repository import Repository
from app.gmail.auth import GmailOAuthManager
from app.core.events import event_bus

class GmailPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._init_ui()

    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(16)

        # Header Title
        top_layout = QHBoxLayout()
        title_lbl = QLabel("Gmail OAuth 2.0 Account Manager")
        title_lbl.setStyleSheet("font-size: 22px; font-weight: bold; color: #CDD6F4;")

        connect_btn = QPushButton("🔑 Connect Gmail Account")
        connect_btn.clicked.connect(self.connect_account)

        top_layout.addWidget(title_lbl)
        top_layout.addStretch()
        top_layout.addWidget(connect_btn)
        layout.addLayout(top_layout)

        # Instruction Card
        card = QFrame()
        card.setStyleSheet("background-color: #181825; border-radius: 8px; padding: 14px;")
        card_box = QVBoxLayout(card)
        info_txt = QLabel(
            "<b>Secure OAuth 2.0 Authentication:</b> TradePilot uses official Google OAuth 2.0 flow. "
            "Passcode and passwords are never stored. Refresh tokens are encrypted with AES-128-CBC."
        )
        info_txt.setWordWrap(True)
        card_box.addWidget(info_txt)
        layout.addWidget(card)

        # Accounts Table
        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels([
            "ID", "Email Address", "Status", "Sent Today", "Connected At"
        ])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        layout.addWidget(self.table)

        self.load_accounts()

    def load_accounts(self):
        accounts = Repository.get_accounts()
        self.table.setRowCount(len(accounts))
        for r, a in enumerate(accounts):
            self.table.setItem(r, 0, QTableWidgetItem(str(a.id)))
            self.table.setItem(r, 1, QTableWidgetItem(a.email))
            self.table.setItem(r, 2, QTableWidgetItem("Active Token" if a.is_active else "Expired"))
            self.table.setItem(r, 3, QTableWidgetItem(str(a.sent_today_count)))
            self.table.setItem(r, 4, QTableWidgetItem(a.created_at))

    def connect_account(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Select Google Client Secrets JSON", "", "JSON Files (*.json)"
        )
        if file_path:
            try:
                res = GmailOAuthManager.start_oauth_flow(file_path)
                if res:
                    acc = GmailAccount(
                        email=res["email"],
                        display_name=res["email"],
                        refresh_token_encrypted=res["encrypted_token"],
                        is_active=True
                    )
                    acc_id = Repository.add_account(acc)
                    self.load_accounts()
                    QMessageBox.information(self, "Success", f"Connected Gmail account: {res['email']}")
                    event_bus.account_added.emit({"id": acc_id, "email": res["email"]})
                else:
                    QMessageBox.warning(self, "OAuth Failed", "OAuth authorization was not completed.")
            except Exception as e:
                QMessageBox.critical(self, "OAuth Error", f"OAuth authentication failed:\n{str(e)}")
