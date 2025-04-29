import re
import logging
import azure_integration.logger_config

log = logging.getLogger(__name__)

""" validation.py: Validates the input from DistilBERT model, performing presence checks and ensuring data is in the correct format. """

# Regular expressions for validation
# SCRIPT_PATTERN = re.compile(r"<\s*script\b", re.IGNORECASE)  # Check for <script> tags
EMAIL_PATTERN = re.compile(r"^[\w\.-]+@[\w\.-]+\.\w+$")


# Search for dangerous input
# def sanitise_text(text: str) -> str:
#     if SCRIPT_PATTERN.search(text):
#         raise ValueError("Input contains potentially dangerous content.")
#     return text.strip()


# Validate input data
def validate_input(project, title, description, priority, assignee, tags):
    if not project or not project.strip():
        raise ValueError("Project name must not be empty or whitespace")
    # project = sanitise_text(project)

    if not title or not title.strip():
        raise ValueError("Title must not be empty or whitespace")
    # title = sanitise_text(title)

    if not description or not description.strip():
        raise ValueError("Description must not be empty or whitespace")
    # description = sanitise_text(description)

    if not priority:
        raise ValueError("Priority must not be empty or whitespace")
    if (priority < 1 or priority > 4) or not isinstance(priority, int):
        raise ValueError(
            f"Priority must be an integer between 1 and 4. Priority: {priority}"
        )

    if not assignee and not assignee.strip():
        raise ValueError(
            "Assignee must not be empty or whitespace"
        )  # and assignee must be in client's organisation
    # assignee = sanitise_text(assignee)
    if not EMAIL_PATTERN.match(assignee):
        raise ValueError(
            "Assignee must be a valid email address. Value provided: {assignee}"
        )

    if not tags and not tags.strip():
        raise ValueError("Tags must not be empty or whitespace")
    # tags = sanitise_text(tags)

    log.info("Input data validated successfully")
    return project, title, description, priority, assignee, tags
