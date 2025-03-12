""" PROTOTYPE: Azure DevOps Integration: Client """

"""
    Handles connection to Azure DevOps and creates the work items via the Azure DevOps API. 
"""

import logging
import azure_integration.logger_config
from azure.devops.connection import Connection
from msrest.authentication import BasicAuthentication
from azure_integration.config import ORGANISATION_URL, PERSONAL_ACCESS_TOKEN, ISSUE_TYPE
from azure_integration.data_preparation import prepare_work_item_data
from azure_integration.validation import validate_input

log = logging.getLogger(__name__)

# Establish connection to organisation
credentials = BasicAuthentication("", PERSONAL_ACCESS_TOKEN)
connection = Connection(base_url=ORGANISATION_URL, creds=credentials)

# Get WorkItemTrackingClient
client = connection.clients.get_work_item_tracking_client()


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

        log.info(f"Created work item: {work_item.id}")
        return work_item
    except Exception as e:
        log.error(f"Failed to create work item: {e}")
        raise e
