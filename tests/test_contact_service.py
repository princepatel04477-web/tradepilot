import pytest
import pandas as pd
from pathlib import Path
from app.services.contact_service import ContactService
from app.services.validation_service import ValidationService

def test_email_validation():
    assert ValidationService.is_valid_email("test@example.com") is True
    assert ValidationService.is_valid_email("invalid_email") is False
    assert ValidationService.is_valid_email("") is False

def test_parse_import_file(tmp_path):
    # Create temp excel file
    excel_file = tmp_path / "contacts.xlsx"
    df = pd.DataFrame([
        {"Company": "Acme", "Contact Name": "Alice", "Email": "alice@acme.com", "Country": "USA"},
        {"Company": "Acme", "Contact Name": "Alice Duplicate", "Email": "alice@acme.com", "Country": "USA"},
        {"Company": "Beta", "Contact Name": "Bob", "Email": "bad_email", "Country": "UK"}
    ])
    df.to_excel(excel_file, index=False)

    contacts, errors = ContactService.parse_import_file(str(excel_file))
    assert len(contacts) == 1
    assert contacts[0].email == "alice@acme.com"
    assert len(errors) == 2
