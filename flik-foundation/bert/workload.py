import requests
import json

""" workload.py: Fetch the workload of a specific developer in specified board columns  """


# Fetch number of work items for a specific user
def get_developer_workload(org, project, pat, developer, columns):

    # Convert column(s) to list
    if isinstance(columns, str):
        columns = [columns]

    # Format columns
    columns_list_str = ", ".join(f"'{col}'" for col in columns)

    query = {
        "query": f"select [System.Id] from WorkItems where [System.BoardColumn] in ({columns_list_str}) and [System.AssignedTo] = '{developer}'"
    }

    query_url = f"https://dev.azure.com/{org}/{project}/_apis/wit/wiql?api-version=7.1"
    headers = {"Content-Type": "application/json"}

    response = requests.post(query_url, json=query, headers=headers, auth=("", pat))
    response.raise_for_status()

    # Count number of tickets in specific column(s) for specific user
    try:
        work_items = response.json()
        work_item_count = len(work_items.get("workItems", []))
        print(developer, work_item_count)
        print(columns)
    except json.decoder.JSONDecodeError as e:
        print("Error decoding JSON. Response may not be in JSON format.")
        raise e

    return work_item_count


# Example usage
if __name__ == "__main__":
    ORGANISATION = "comp3932-flik"
    PROJECT_NAME = "Flik"
    PERSONAL_ACCESS_TOKEN = "TmwkawvRYbz2weeboOdSmkHFAPh0oo8clMu9ZsNiGuSyLA6pN62mJQQJ99BCACAAAAAAAAAAAAASAZDO2xCF"
    DEVELOPER_EMAIL = "nathanmw72@gmail.com"
    # DEVELOPER_EMAIL = "sc21nw@leeds.ac.uk"
    COLUMNS = ["To Do", "Blocked"]

    work_item_count = get_developer_workload(
        ORGANISATION, PROJECT_NAME, PERSONAL_ACCESS_TOKEN, DEVELOPER_EMAIL, COLUMNS
    )
    print(f"{work_item_count} tickets for {DEVELOPER_EMAIL} in columns: {COLUMNS}")
