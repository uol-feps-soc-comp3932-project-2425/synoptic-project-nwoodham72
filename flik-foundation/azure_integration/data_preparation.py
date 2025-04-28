""" PROTOTYPE: Azure DevOps Integration: Configuration: Data Preparation """

"""
    Prepares a JSON patch document to be sent to Azre DevOps.
"""

from azure.devops.v7_1.work_item_tracking.models import JsonPatchOperation


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
