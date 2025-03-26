import os
import json
import random
from transformers import DistilBertTokenizer, DistilBertForSequenceClassification, pipeline
from workload import get_developer_workload

"""
new_assigner.py: Allocate developers to bug ticket based on pre-defined labels in fine_tuned_assigner/bug_themes.json.
"""

# Load fine-tuned model
local_directory = os.path.dirname(__file__)
MODEL_DIR = os.path.join(local_directory, "models/fine_tuned_assigner")

# Load tokenizer
tokeniser = DistilBertTokenizer.from_pretrained(MODEL_DIR)
model = DistilBertForSequenceClassification.from_pretrained(MODEL_DIR)

# Create classification pipeline 
classifier = pipeline("text-classification", model=model, tokenizer=tokeniser, top_k=None)  # top_k: Get highest matching themes

# Load bug_themes.json
label_names_file = os.path.join(local_directory, "models/fine_tuned_assigner", "bug_themes.json")
with open(label_names_file, "r") as f:
    label_names = json.load(f)

# Map labels to human-readable format in bug_themes.json
label_mapping = {f"LABEL_{i}": name for i, name in enumerate(label_names)}

# Fetch developers and skills
developers = {
    "nathanmw72@gmail.com": {"Information", "Feedback", "Sales", "Infrastructure", "IT"},
    "sc21nw@leeds.ac.uk": {"Login", "Feedback", "Sales"}
}

# Tag bug description with defined labels
def tag_bug(text, threshold=0.7):
    results = classifier(text)
    if not results:
        return []

    # Score label likelihood with ticket
    label_scores = results[0]
    predicted_tags = []
    for item in label_scores:
        label = item["label"]
        score = item["score"]
        if score >= threshold:
            # Convert model label to human-readable format
            user_friendly_label = label_mapping.get(label, label)
            predicted_tags.append(user_friendly_label)
    
    return predicted_tags[:3]  # Return top 3 matching tags

# Assign developer to bug based on bug themes and developer skillset
def assign_developer(predicted_tags, developers):
    best_overlap = 0
    best_assignees = {}
    predicted_tags_set = set(predicted_tags)
    
    # Iterate through developer skills
    for dev, skills in developers.items():
        overlap = predicted_tags_set & skills  # Matching skills
        if len(overlap) > best_overlap:
            best_overlap = len(overlap)
            best_assignees = {dev: overlap}  # Reset with current best
        elif len(overlap) == best_overlap and best_overlap > 0:
            best_assignees[dev] = overlap  # Add if equal to best_overlap
            
    return best_assignees  # Return developer(s) with highest overlap of skills and bug themes

# Filter best assignees to assigness with lowest workload and most skills
def select_developer_by_workload_and_skills(organisation, project, pat, assignments):
    # Append best developers with lowest workload and most skills
    candidates = []
    for dev, matching_skills in assignments.items():
        assignee_workload = get_developer_workload(organisation, project, pat, dev, ["To Do"])
        # Matching skills are already found 
        # if workload is the same, then send to dev with the highest general skillset
        developer_general_skill_count = len(developers.get(dev, [])) 
        # print(dev, assignee_workload)
        # print(dev, developer_general_skill_count)
        candidates.append((dev, assignee_workload, developer_general_skill_count))

    if not candidates:
        return None
    
    # Sort candidates by general skill count
    candidates.sort(key=lambda x: (x[1], -x[2]))
    lowest_workload = candidates[0][1]
    highest_general_skill_count = candidates[0][2]

    # Filter candidates with lowest workload and highest general skillcount
    best_candidates = [c for c in candidates if c[1] == lowest_workload and c[2] == highest_general_skill_count]

    # If multiple candidates have the same workload, randomly assign
    selected_candidate = random.choice(best_candidates) if len(best_candidates) > 1 else candidates[0]
        
    return selected_candidate[0]


# Example usage
if __name__ == '__main__':
    examples = [
        {
            "title": "Customer Support Inquiry",
            "text": (
                "Seeking information on digital strategies that can aid in brand growth "
                "and details on the available services. Looking forward to learning more "
                "to help our business grow. Thank you, and I look forward to hearing from you soon."
            )
        },
        {
            "title": "Data Analytics for Investment",
            "text": (
                "I am contacting you to request information on data analytics tools that "
                "can be utilized with the Eclipse IDE for enhancing investment optimization. "
                "I am seeking suggestions for tools that can aid in making data-driven decisions. "
                "Particularly, I am interested in tools that can manage large datasets and offer "
                "advanced analytics features. These tools should be compatible with the Eclipse IDE "
                "and can smoothly integrate into my workflow. Key features I am interested in include "
                "data visualization, predictive modeling, and machine learning capabilities. I would "
                "greatly appreciate any recommendations or advice on how to begin with data analytics "
                "for investment optimization using the Eclipse IDE."
            )
        },
        {
            "title": "Cannot log in",
            "text": (
                "I am a manager user on the login page. "
                "I am trying to log in with valid credentials into the Student portal. "
                "When I click login it says that my account is not recognised, and it seems that your reset password link is not working either."
                "I also get a 403 error and the system crashes"
            )
        }
    ]

    # Board and work item configuration
    ORGANISATION = "comp3932-flik"
    PROJECT_NAME = "Flik"
    PERSONAL_ACCESS_TOKEN = "TmwkawvRYbz2weeboOdSmkHFAPh0oo8clMu9ZsNiGuSyLA6pN62mJQQJ99BCACAAAAAAAAAAAAASAZDO2xCF"

    for example in examples:
        predicted_tags = tag_bug(example["text"], threshold=0.6)
        best_assignments = assign_developer(predicted_tags, developers)  # Developers with the highest skill overlap with bug themes in ticket
        
        print(f"--- {example['title']} ---")
        print(f"Predicted Tags: {predicted_tags}")
        if best_assignments:
            if len(best_assignments) > 1:
                assigned_to = select_developer_by_workload_and_skills(ORGANISATION, PROJECT_NAME, PERSONAL_ACCESS_TOKEN, best_assignments)
                print(f"AssignedTo: {assigned_to}")
            else:
                for dev, matching_skills in best_assignments.items():
                    print(f"AssignedTo: {dev}")
                    # print(f"AssignedTo: {dev} - Matching Skills: {list(matching_skills)}")
        # No developer matched on skill
        else:
            # Assign developer with lowest workload then largest no. of skills
            all_devs = {dev: set() for dev in developers}
            assigned_to = select_developer_by_workload_and_skills(ORGANISATION, PROJECT_NAME, PERSONAL_ACCESS_TOKEN, all_devs)
            print(f"AssignedTo: {assigned_to}")
            # print("no dev")
        print()