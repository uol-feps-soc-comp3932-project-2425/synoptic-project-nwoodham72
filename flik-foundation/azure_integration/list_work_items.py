import requests
import json

# Fetch total number of work items
def get_all_tickets(org, project, pat):
    query = {
        "query": "select [System.Id] from WorkItems where [System.BoardColumn] in ('To Do')"  # ('To do', 'Doing') - Track multiple columns
    }
    
    query_url = f"https://dev.azure.com/{org}/{project}/_apis/wit/wiql?api-version=7.1"
    headers = {"Content-Type": "application/json"}

    response = requests.post(query_url, json=query, headers=headers, auth=("", pat))
    response.raise_for_status()
    
    # Print status code and response text for debugging
    # print("Status Code:", response.status_code)
    # print("Response Text:", response.text)
    
    # Count number of tickets in specific column(s)
    try:
        work_item_count = response.json()
    except json.decoder.JSONDecodeError as e:
        print("Error decoding JSON. Response may not be in JSON format.")
        raise e

    return work_item_count

# Fetch number of work items for a specific user 
def get_user_tickets(org, project, pat, developer):
    query = {
        "query": f"select [System.Id] from WorkItems where [System.BoardColumn] in ('Doing') and [System.AssignedTo] contains '{developer}'" 
    }

    query_url = f"https://dev.azure.com/{org}/{project}/_apis/wit/wiql?api-version=7.1"
    headers = {"Content-Type": "application/json"}

    response = requests.post(query_url, json=query, headers=headers, auth=("", pat))
    response.raise_for_status()

    # Count number of tickets in specific column(s) for specific user
    try:
        work_item_count = response.json()
    except json.decoder.JSONDecodeError as e:
        print("Error decoding JSON. Response may not be in JSON format.")
        raise e
    
    return work_item_count

# Example usage
if __name__ == "__main__":
    ORGANISATION = "comp3932-flik"
    PROJECT_NAME = "Flik"
    PERSONAL_ACCESS_TOKEN = "TmwkawvRYbz2weeboOdSmkHFAPh0oo8clMu9ZsNiGuSyLA6pN62mJQQJ99BCACAAAAAAAAAAAAASAZDO2xCF" 

    ticket_data = get_user_tickets(ORGANISATION, PROJECT_NAME, PERSONAL_ACCESS_TOKEN, 'nathanmw72@gmail.com')  # Pass in developer email
    work_items = ticket_data.get("workItems", [])
    print(f"Total number of tickets: {len(work_items)}")
