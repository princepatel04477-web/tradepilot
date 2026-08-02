import pytest
from app.database import init_db, db_manager, Repository
from app.models.contact import Contact
from app.models.template import EmailTemplate

def test_database_crud(tmp_path):
    test_db = tmp_path / "test_tradepilot.db"
    db_manager.db_path = str(test_db)
    init_db()

    # Add Contact
    c = Contact(company="Test Corp", contact_name="Alice", email="alice@test.com", country="UK")
    count = Repository.add_contacts_batch([c])
    assert count == 1

    contacts = Repository.get_contacts()
    assert len(contacts) == 1
    assert contacts[0].company == "Test Corp"

    # Add Template
    t = EmailTemplate(name="Test Temp", subject="Hi {{Contact}}", body_content="Hello {{Company}}")
    t_id = Repository.add_template(t)
    assert t_id > 0

    fetched_t = Repository.get_template_by_id(t_id)
    assert fetched_t is not None
    assert fetched_t.name == "Test Temp"
