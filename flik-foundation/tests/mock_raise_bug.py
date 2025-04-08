import pytest
from unittest.mock import patch
from app import create_app, db
from app.routes import create_ticket_scheduled
from app.models import FlikUser


@pytest.fixture
def app_context():
    app = create_app()
    app.config["TESTING"] = True
    with app.app_context():
        yield app


def test_scheduled_ticket_creation_using_existing_devs(app_context):
    """Tests scheduled ticket creation using saved developer data in the database."""

    # Ensure devs exist
    developers = FlikUser.query.filter_by(role="Developer").all()
    assert developers, "⚠️ No developers found in DB — required for test."

    bug = {
        "title": "MOCK TEST: Settings page loads with a white screen and no content",
        "role": "Student",
        "page": "Student Registration - Test",
        "description": "The settings page loads with a white screen and no content after clicking the settings icon. The settings page loads with a white screen and no content after clicking the settings icon. The settings page loads with a white screen and no content after clicking the settings icon.",
        "expected": "The user should see editable settings fields like name, email, and password update."
    }

    summary_input = (
        f"{bug['title']}.\n"
        f"I am a {bug['role']} user.\n"
        f"I am on the {bug['page']} page.\n"
        f"{bug['description']}.\n"
        f"{bug['expected']}.\n"
    )

    with patch("bert.summariser.extractive_summary") as mock_summary, \
        patch("bert.prioritiser.predict_priority") as mock_priority, \
        patch("bert.assigner.assign_developer") as mock_assign:
        
        mock_summary.return_value = "Settings page does not display content."
        mock_priority.return_value = ("Medium", 2)
        mock_assign.return_value = ("sc21nw@leeds.ac.uk", ["Settings", "Infrastructure"])

        result = create_ticket_scheduled(bug)

        assert result["status"] == "success"
        assert "azure_id" in result

        mock_summary.assert_called_once_with(summary_input)
        mock_priority.assert_called_once_with(summary_input)
        mock_assign.assert_called_once()
