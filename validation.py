""" PROTOTYPE: Azure DevOps Integration: Validation """

"""
    Validates the input from the BERT model, performing presence checks and ensuring data is in the correct format.
"""

import logging
import logger_config

log = logging.getLogger(__name__)


# Validate input data
def validate_input(project, title, description, priority, assignee, tags):
    if not project or not project.strip():
        raise ValueError("Project name must not be empty or whitespace")
    if not title or not title.strip():
        raise ValueError("Title must not be empty or whitespace")
    if not description or not description.strip():
        raise ValueError("Description must not be empty or whitespace")
    if not priority:
        raise ValueError("Priority must not be empty or whitespace")
    if priority < 1 or priority > 4:
        raise ValueError("Priority must be between 1 and 4")
    if not assignee and not assignee.strip():
        raise ValueError(
            "Assignee must not be empty or whitespace"
        )  # and assignee must be in client's organisation
    if not tags and not tags.strip():
        raise ValueError("Tags must not be empty or whitespace")

    log.info("Input data validated successfully")
    return project, title, description, priority, assignee, tags
