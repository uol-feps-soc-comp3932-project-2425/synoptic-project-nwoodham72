""" PROTOTYPE: Azure DevOps Integration """

from azure.devops.connection import Connection
from msrest.authentication import BasicAuthentication
from azure.devops.v7_1.work_item_tracking.models import JsonPatchOperation

# Board and work item configuration
ORGANISATION_URL = "https://dev.azure.com/comp3932-flik"
# PERSONAL_ACCESS_TOKEN can read/write/manage work items
PERSONAL_ACCESS_TOKEN = "9HIMqHnokwSl9nWZTFtT1mtPQnLl6G1PG6du6wUlKum7jXP5mLZ9JQQJ99BBACAAAAAAAAAAAAASAZDO1umy"
PROJECT_NAME = "Flik"
ISSUE = "Issue"

# Establish connection to organisation
credentials = BasicAuthentication("", PERSONAL_ACCESS_TOKEN)
connection = Connection(base_url=ORGANISATION_URL, creds=credentials)

# Get WorkItemTrackingClient
client = connection.clients.get_work_item_tracking_client()

# Validate input data
def validate_input(project, title, description, priority):
    if not project or not project.strip():
        raise ValueError("Project name is required")
    if not title or not title.strip():
        raise ValueError("Title is required")
    if not description or not description.strip():
        raise ValueError("Description is required")
    if not priority:
        raise ValueError("Priority is required")
    if priority < 1 or priority > 4:
        raise ValueError("Priority must be between 1 and 4")

# Format work item data
def prepare_work_item_data(title, description, priority):
    return [
        JsonPatchOperation(op="add", path="/fields/System.Title", value=f"{title}"),
        JsonPatchOperation(
            op="add", path="/fields/System.Description", value=f"{description}"
        ),
        JsonPatchOperation(
            op="add", path="/fields/Microsoft.VSTS.Common.Priority", value=priority
        ),
        JsonPatchOperation(op="add", path="/fields/System.WorkItemType", value="Issue"),
    ]

# Send work item to Azure DevOps
def create_work_item(project, title, description, priority):
    validate_input(project, title, description, priority)
    work_item_data = prepare_work_item_data(title, description, priority)

    # Create work item
    work_item = client.create_work_item(
        document=work_item_data, project=project, type=ISSUE
    )

    return work_item

# Example usage
project_name = PROJECT_NAME
title = "Testing Title"
description = "Testing Description"
priority = 4  # Range: 1-4, 1 being highest priority

issue = create_work_item(project_name, title, description, priority)

print("Created issue. ID: ", issue.id)
