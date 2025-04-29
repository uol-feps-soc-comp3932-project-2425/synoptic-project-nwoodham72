import logging
import azure_integration.logger_config
from azure_integration.config import PROJECT_NAME
from azure_integration.client import create_work_item

log = logging.getLogger(__name__)

""" main.py: Run the AD component independently. """


# Create work item
def main():
    project_name = PROJECT_NAME
    title = 'MVP-1 Integration Test'
    description = "Testing Description without any malicious content."
    priority = 4  # Priority range: 1 (highest) to 4.
    assignee = "nathanmw72@gmail.com"  # Must be valid in Azure DevOps.
    tags = "text, example"  # Comma-separated list of tags.

    # Send work item to Azure DevOps
    try:
        ticket = create_work_item(
            project_name, title, description, priority, assignee, tags
        )
        log.info(f"Sent ticket ID: {ticket.id} to Azure DevOps")
    except Exception as e:
        log.error("Failed to send ticket: %s to Azure DevOps", e, exc_info=True)


if __name__ == "__main__":
    main()
