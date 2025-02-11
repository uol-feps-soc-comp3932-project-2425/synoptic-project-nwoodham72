""" PROTOTYPE: Azure DevOps Integration """

import logging
from azure.devops.connection import Connection
from msrest.authentication import BasicAuthentication
from azure.devops.v7_1.work_item_tracking.models import JsonPatchOperation

logging.basicConfig(level=logging.INFO)

# Board and work item configuration
ORGANISATION_URL = "https://dev.azure.com/comp3932-flik"
# PERSONAL_ACCESS_TOKEN can read/write/manage work items
PERSONAL_ACCESS_TOKEN = "9HIMqHnokwSl9nWZTFtT1mtPQnLl6G1PG6du6wUlKum7jXP5mLZ9JQQJ99BBACAAAAAAAAAAAAASAZDO1umy"
PROJECT_NAME = "Flik"
ISSUE_TYPE = "Issue"

# Establish connection to organisation
credentials = BasicAuthentication("", PERSONAL_ACCESS_TOKEN)
connection = Connection(base_url=ORGANISATION_URL, creds=credentials)

# Get WorkItemTrackingClient
client = connection.clients.get_work_item_tracking_client()

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
        raise ValueError("Assignee must not be empty or whitespace")  # and assignee must be in client's organisation
    if not tags and not tags.strip():
        raise ValueError("Tags must not be empty or whitespace")

# Format work item data
def prepare_work_item_data(title, description, priority, assignee, tags):
    return [
        JsonPatchOperation(op="add", path="/fields/System.Title", value=f"{title}"),
        JsonPatchOperation(
            op="add", path="/fields/System.Description", value=f"{description}"
        ),
        JsonPatchOperation(
            op="add", path="/fields/Microsoft.VSTS.Common.Priority", value=priority
        ),
        JsonPatchOperation(
            op="add", path="/fields/System.AssignedTo", value=f"{assignee}"
        ),
        JsonPatchOperation(op="add", path="/fields/System.Tags", value=f"{tags}"),
    ]

# Send work item to Azure DevOps
def create_work_item(project, title, description, priority, assignee, tags):
    try:
        validate_input(project, title, description, priority, assignee, tags)
        work_item_data = prepare_work_item_data(
            title, description, priority, assignee, tags
        )

        # Create work item
        work_item = client.create_work_item(
            document=work_item_data, project=project, type=ISSUE_TYPE
        )

        logging.info(f"Created work item: {work_item.id}")
        return work_item
    except Exception as e:
        logging.error(f"Failed to create work item: {e}")
        raise e

# Example usage
project_name = PROJECT_NAME
title = "Testing Title"
description = "Testing Description"
priority = 4  # Range: 1-4, 1 being highest priority
assignee = "nathanmw72@gmail.com"  # Will only accept names defined in Azure DevOps (name or email)
tags = "text, example"  # Comma-separated list of tags

ticket = create_work_item(project_name, title, description, priority, assignee, tags)

logging.info(f"Sent ticket ID: {ticket.id} to Azure DevOps")
