from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QTableWidget,
    QTableWidgetItem, QHeaderView, QFileDialog, QMessageBox, QComboBox
)
from PySide6.QtCore import Qt
from app.database.repository import Repository
from app.services.contact_service import ContactService
from app.core.events import event_bus

class ContactsPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._init_ui()

    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(16)

        # Header Title & Action Buttons
        top_layout = QHBoxLayout()
        title_lbl = QLabel("Contact Management")
        title_lbl.setStyleSheet("font-size: 22px; font-weight: bold; color: #CDD6F4;")

        import_btn = QPushButton("📁 Import Excel / CSV")
        import_btn.clicked.connect(self.import_contacts)

        clear_btn = QPushButton("🗑 Clear All")
        clear_btn.setObjectName("DangerButton")
        clear_btn.clicked.connect(self.clear_contacts)

        top_layout.addWidget(title_lbl)
        top_layout.addStretch()
        top_layout.addWidget(import_btn)
        top_layout.addWidget(clear_btn)
        layout.addLayout(top_layout)

        # Search & Filter Controls
        filter_layout = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("🔍 Search by email, company, name, or country...")
        self.search_input.textChanged.connect(self.load_contacts)

        self.status_combo = QComboBox()
        self.status_combo.addItems(["All Statuses", "Active", "Unsubscribed"])
        self.status_combo.currentIndexChanged.connect(self.load_contacts)

        filter_layout.addWidget(self.search_input)
        filter_layout.addWidget(self.status_combo)
        layout.addLayout(filter_layout)

        # Contact Table
        self.table = QTableWidget()
        self.table.setColumnCount(8)
        self.table.setHorizontalHeaderLabels([
            "ID", "Company", "Contact Name", "Email", "Country", "City", "Phone", "Tags"
        ])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        layout.addWidget(self.table)

        self.load_contacts()

    def load_contacts(self):
        search_txt = self.search_input.text().strip()
        status_filter = self.status_combo.currentText()
        if status_filter == "All Statuses":
            status_filter = ""

        contacts = Repository.get_contacts(search=search_txt, status=status_filter)
        self.table.setRowCount(len(contacts))
        for r, c in enumerate(contacts):
            self.table.setItem(r, 0, QTableWidgetItem(str(c.id)))
            self.table.setItem(r, 1, QTableWidgetItem(c.company))
            self.table.setItem(r, 2, QTableWidgetItem(c.contact_name))
            self.table.setItem(r, 3, QTableWidgetItem(c.email))
            self.table.setItem(r, 4, QTableWidgetItem(c.country))
            self.table.setItem(r, 5, QTableWidgetItem(c.city))
            self.table.setItem(r, 6, QTableWidgetItem(c.phone))
            self.table.setItem(r, 7, QTableWidgetItem(c.tags))

    def import_contacts(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Select Contacts File", "", "Spreadsheets (*.xlsx *.xls *.csv)"
        )
        if file_path:
            try:
                res = ContactService.import_contacts_to_db(file_path)
                msg = f"Successfully imported {res['inserted']} new contacts.\n"
                if res['duplicates_skipped'] > 0:
                    msg += f"Skipped {res['duplicates_skipped']} duplicates.\n"
                if res['errors']:
                    msg += f"\nWarnings:\n" + "\n".join(res['errors'][:5])
                QMessageBox.information(self, "Import Complete", msg)
                self.load_contacts()
                event_bus.contacts_imported.emit(res['inserted'])
            except Exception as e:
                QMessageBox.critical(self, "Import Failed", f"Failed to import contacts file:\n{str(e)}")

    def clear_contacts(self):
        reply = QMessageBox.question(
            self, "Confirm Delete", "Are you sure you want to delete ALL contacts?",
            QMessageBox.Yes | QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            Repository.delete_all_contacts()
            self.load_contacts()
            event_bus.stats_updated.emit()
