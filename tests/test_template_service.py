import pytest
from app.models.contact import Contact
from app.services.template_service import template_service

def test_template_rendering():
    template_str = "Hello {{Contact}} from {{Company}} in {{Country}}!"
    contact = Contact(contact_name="Sarah", company="Starlight Inc", email="sarah@starlight.com", country="Canada")

    rendered = template_service.render(template_str, contact)
    assert rendered == "Hello Sarah from Starlight Inc in Canada!"

def test_variable_extraction():
    template_str = "Dear {{Contact}}, welcome to {{Company}} in {{City}}."
    vars_list = template_service.extract_variables(template_str)
    assert set(vars_list) == {"Contact", "Company", "City"}

def test_template_syntax_validation():
    valid_template = "Hello {{Contact}}"
    invalid_template = "Hello {{Contact"

    ok, _ = template_service.validate_template_syntax(valid_template)
    assert ok is True

    ok_bad, err = template_service.validate_template_syntax(invalid_template)
    assert ok_bad is False
