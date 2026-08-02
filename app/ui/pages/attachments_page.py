from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QTableWidget,
    QTableWidgetItem, QHeaderView, QFileDialog, QMessageBox, QComboBox
)
from app.database.repository import Repository
from app.services.attachment_service import AttachmentService

class AttachmentsPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._init_ui()

    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(16)

        # Header Title & Buttons
        top_layout = QHBoxLayout()
        title_lbl = QLabel("Attachment Media Library")
        title_lbl.setStyleSheet("font-size: 22px; font-weight: bold; color: #CDD6F4;")

        add_btn = QPushButton("📎 Add Attachment File")
        add_btn.clicked.connect(self.add_attachment)

        top_layout.addWidget(title_lbl)
        top_layout.addStretch()
        top_layout.addWidget(add_btn)
        layout.addLayout(top_layout)

        # Attachments Table
        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels([
            "ID", "Filename", "File Path", "Size (KB)", "MIME Type", "Category"
        ])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        layout.addWidget(self.table)

        self.load_attachments()

    def load_attachments(self):
        atts = AttachmentService.get_all_attachments()
        self.table.setRowCount(len(atts))
        for r, a in enumerate(atts):
            self.table.setItem(r, 0, QTableWidgetItem(str(a.id)))
            self.table.setItem(r, 1, QTableWidgetItem(a.filename))
            self.table.setItem(r, 2, QTableWidgetItem(a.filepath))
            self.table.setItem(r, 3, QTableWidgetItem(str(round(a.file_size_bytes / 1024, 1))))
            self.table.setItem(r, 4, QTableWidgetItem(a.mime_type))
            self.table.setItem(r, 5, QTableWidgetItem(a.category))

    def add_attachment(self):
        filepath, _ = QFileDialog.getOpenFileName(
            self, "Select Document or Attachment", "",
            "All Files (*.pdf *.docx *.doc *.png *.jpg *.jpeg *.xlsx *.zip)"
        )
        if filepath:
            try:
                AttachmentService.register_attachment(filepath, category="General")
                self.load_attachments()
                QMessageBox.information(self, "Success", "Attachment registered in library.")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to register attachment:\n{str(e)}")
