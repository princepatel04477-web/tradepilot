from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QTextEdit, QPushButton,
    QTableWidget, QTableWidgetItem, QHeaderView, QCheckBox, QMessageBox, QFrame
)
from app.models.template import EmailTemplate
from app.models.contact import Contact
from app.database.repository import Repository
from app.services.template_service import template_service
from app.ui.components.preview_modal import EmailPreviewModal

class TemplatesPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.editing_id = None
        self._init_ui()

    def _init_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(20)

        # Left Panel: Template List
        left_box = QVBoxLayout()
        left_lbl = QLabel("Templates Library")
        left_lbl.setStyleSheet("font-size: 18px; font-weight: bold; color: #CDD6F4;")

        self.table = QTableWidget()
        self.table.setColumnCount(3)
        self.table.setHorizontalHeaderLabels(["ID", "Name", "Subject"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.cellClicked.connect(self.on_template_selected)

        new_btn = QPushButton("+ Create New Template")
        new_btn.clicked.connect(self.reset_form)

        left_box.addWidget(left_lbl)
        left_box.addWidget(new_btn)
        left_box.addWidget(self.table)
        layout.addLayout(left_box, stretch=1)

        # Right Panel: Template Editor
        right_frame = QFrame()
        right_frame.setStyleSheet("background-color: #181825; border-radius: 8px; padding: 16px;")
        right_box = QVBoxLayout(right_frame)

        editor_lbl = QLabel("Template Editor")
        editor_lbl.setStyleSheet("font-size: 18px; font-weight: bold; color: #89B4FA;")

        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Template Name (e.g., Cold Outreach V1)")

        self.subject_input = QLineEdit()
        self.subject_input.setPlaceholderText("Subject Line (e.g., Exclusive Import Opportunity for {{Company}})")

        self.is_html_cb = QCheckBox("Format as HTML Email")
        self.is_html_cb.setChecked(True)

        # Variable Helper Toolbar
        vars_layout = QHBoxLayout()
        vars_lbl = QLabel("Insert Variable:")
        vars_layout.addWidget(vars_lbl)

        var_buttons = ["{{Company}}", "{{Contact}}", "{{Country}}", "{{City}}", "{{Email}}"]
        for v in var_buttons:
            btn = QPushButton(v)
            btn.setObjectName("SecondaryButton")
            btn.clicked.connect(lambda _, var=v: self.insert_variable(var))
            vars_layout.addWidget(btn)
        vars_layout.addStretch()

        self.body_input = QTextEdit()
        self.body_input.setPlaceholderText("Write your email body here...\nUse Jinja2 tags like {{Contact}} and {{Company}}.")

        btn_layout = QHBoxLayout()
        preview_btn = QPushButton("👁 Preview Email")
        preview_btn.setObjectName("SecondaryButton")
        preview_btn.clicked.connect(self.preview_template)

        save_btn = QPushButton("💾 Save Template")
        save_btn.clicked.connect(self.save_template)

        delete_btn = QPushButton("🗑 Delete")
        delete_btn.setObjectName("DangerButton")
        delete_btn.clicked.connect(self.delete_template)

        btn_layout.addWidget(preview_btn)
        btn_layout.addStretch()
        btn_layout.addWidget(delete_btn)
        btn_layout.addWidget(save_btn)

        right_box.addWidget(editor_lbl)
        right_box.addWidget(QLabel("Name:"))
        right_box.addWidget(self.name_input)
        right_box.addWidget(QLabel("Subject:"))
        right_box.addWidget(self.subject_input)
        right_box.addWidget(self.is_html_cb)
        right_box.addLayout(vars_layout)
        right_box.addWidget(QLabel("Email Body Content:"))
        right_box.addWidget(self.body_input)
        right_box.addLayout(btn_layout)

        layout.addWidget(right_frame, stretch=2)
        self.load_templates()

    def insert_variable(self, var_text: str):
        self.body_input.insertPlainText(var_text)

    def load_templates(self):
        templates = Repository.get_templates()
        self.table.setRowCount(len(templates))
        for r, t in enumerate(templates):
            self.table.setItem(r, 0, QTableWidgetItem(str(t.id)))
            self.table.setItem(r, 1, QTableWidgetItem(t.name))
            self.table.setItem(r, 2, QTableWidgetItem(t.subject))

    def on_template_selected(self, row: int, col: int):
        template_id = int(self.table.item(row, 0).text())
        t = Repository.get_template_by_id(template_id)
        if t:
            self.editing_id = t.id
            self.name_input.setText(t.name)
            self.subject_input.setText(t.subject)
            self.body_input.setText(t.body_content)
            self.is_html_cb.setChecked(t.is_html)

    def reset_form(self):
        self.editing_id = None
        self.name_input.clear()
        self.subject_input.clear()
        self.body_input.clear()
        self.is_html_cb.setChecked(True)

    def save_template(self):
        name = self.name_input.text().strip()
        subject = self.subject_input.text().strip()
        body = self.body_input.toPlainText().strip()
        is_html = self.is_html_cb.isChecked()

        if not name or not subject or not body:
            QMessageBox.warning(self, "Validation Error", "Template name, subject, and body are required.")
            return

        valid, err = template_service.validate_template_syntax(body)
        if not valid:
            QMessageBox.critical(self, "Template Syntax Error", f"Jinja2 Syntax Error:\n{err}")
            return

        vars_list = template_service.extract_variables(body)
        template = EmailTemplate(
            id=self.editing_id,
            name=name,
            subject=subject,
            body_content=body,
            is_html=is_html,
            variables=vars_list
        )

        if self.editing_id:
            Repository.update_template(template)
            QMessageBox.information(self, "Success", "Template updated successfully.")
        else:
            Repository.add_template(template)
            QMessageBox.information(self, "Success", "New template saved.")

        self.load_templates()
        self.reset_form()

    def delete_template(self):
        if not self.editing_id:
            return
        reply = QMessageBox.question(self, "Confirm Delete", "Delete this template?", QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            Repository.delete_template(self.editing_id)
            self.load_templates()
            self.reset_form()

    def preview_template(self):
        body = self.body_input.toPlainText().strip()
        subject = self.subject_input.text().strip() or "Sample Subject"
        is_html = self.is_html_cb.isChecked()

        sample_contact = Contact(
            company="Acme Global Logistics",
            contact_name="John Doe",
            email="johndoe@acmelogistics.com",
            country="Germany",
            city="Hamburg"
        )

        rendered_subject = template_service.render(subject, sample_contact)
        rendered_body = template_service.render(body, sample_contact)

        modal = EmailPreviewModal(
            recipient_email=sample_contact.email,
            subject=rendered_subject,
            body_content=rendered_body,
            is_html=is_html,
            attachments=[],
            parent=self
        )
        modal.exec()
