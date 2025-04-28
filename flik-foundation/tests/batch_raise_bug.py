import pytest
import json
from app import create_app
from app.models import FlikUser
from app.routes import create_ticket_scheduled

""" batch_raise_bug.py: Test the full ticket flow using a batch of 20 test tickets. """

@pytest.fixture
def app_context():
    app = create_app()
    app.config["TESTING"] = True
    with app.app_context():
        yield app

# Batch test 20 tickets following 'raise_bug' flow
def test_real_raise_bug_batch(app_context):
    developers = FlikUser.query.filter_by(role="Developer").all()
    assert developers, "No developers found."

    # Load bug tickets
    with open("tests/bug_tickets.json", "r") as f:
        bug_list = json.load(f)

    # Submit each ticket
    for i, bug in enumerate(bug_list, start=1):
        print(f"\n📨 Submitting ticket {i}: {bug['title']}")

        result = create_ticket_scheduled(bug)

        assert result["status"] == "success"
        assert "azure_id" in result and result["azure_id"] is not None

        print(f"✅ Created Azure DevOps ticket ID: {result['azure_id']}")
