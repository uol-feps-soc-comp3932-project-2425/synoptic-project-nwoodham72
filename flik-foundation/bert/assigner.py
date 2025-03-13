from transformers import DistilBertTokenizer, DistilBertForSequenceClassification, pipeline

""" Handles developer assignment using the Hugging Face DistilBERT model. """

# Todo: Implement workload

# Load classification model
classification_tokeniser = DistilBertTokenizer.from_pretrained('distilbert-base-uncased')
classification_model = DistilBertForSequenceClassification.from_pretrained('distilbert-base-uncased')

# Create classifier pipeline
classifier = pipeline('text-classification', model=classification_model, tokenizer=classification_tokeniser)

# Azure DevOps developers
# todo: Pull developers and skills from database 
developers = {
    "nathanmw72@gmail.com": {"front-end", "user accounts", "organisations"},
    "sc21nw@leeds.ac.uk": {"back-end", "team members", "team member's skills"}
}

# Map DistilBERT classification labels to developer skills
all_skills = set(skill for skillset in developers.values() for skill in skillset)
label_to_skill_mapping = {f"LABEL_{i}": skill for i, skill in enumerate(all_skills)}

# Assign developer
def assign_developer(developers, description, threshold=0.5):
    results = classifier(description)
    
    # Extract relevant skills from classification results
    detected_labels = {result['label']: result['score'] for result in results if result['score'] > threshold}
    
    # Map detected labels dynamically to meaningful words from the description
    detected_skills = set()
    for label in detected_labels.keys():
        words = description.split()  # Basic tokenization
        for word in words:
            if word.lower() in all_skills:
                detected_skills.add(word.lower())

    # Ensure detected skills are mapped correctly
    relevant_skills = detected_skills if detected_skills else detected_labels.keys()

    # Find the best matching developer
    best_match = None
    best_skill_overlap = 0
    best_matching_skills = set()

    for dev, skills in developers.items():
        overlap = relevant_skills & skills
        if len(overlap) > best_skill_overlap:
            best_match = dev
            best_skill_overlap = len(overlap)
            best_matching_skills = overlap
    
    # If no skills match, assign the developer with the closest skill set
    if best_match is None:
        best_match = max(developers.keys(), key=lambda dev: len(developers[dev]))
        best_matching_skills = set()
    
    # return best_match, developers[best_match], list(best_matching_skills)
    return best_match


## Ticket description
# bug_description = """
#     As a Manager User, when attempting to update a team member’s skills, I can type in a new skill, but clicking ‘Add Skill’ does not update the developer’s profile. There is no confirmation message, error message, or indication that the action has been processed. 
#     Steps to Reproduce (Given, When, Then Format) 
#     Given I am logged in as a Manager user. 
#     And I navigate to Team Management > Select a Team Member > Click Edit Skills. 
#     When I type a new skill into the input field. 
#     And I click the ‘Add Skill’ button. 
#     Then I expect the new skill to be added to the team member’s profile. 
#     And I expect to receive a confirmation message or visual feedback. 
#     But Instead, the skill is not added, and no feedback is provided. 
#     Expected Behaviour 
#     The newly added skill should appear in the developer’s Skills section. 
#     A confirmation message (e.g., "Skill successfully added") should be displayed. 
#     The change should persist after reloading the page. 
#     Actual Behaviour 
#     The skill is not added to the developer’s profile. 
#     No success or error message appears. 
#     The page does not update to reflect the change. 
#     After refreshing, the skill is still missing. 
# """

# # Assign a developer
# assigned_developer, developer_skills, skills_required = assign_developer(developers, bug_description)

# print(f"Assigned Developer: {assigned_developer}")
# print(f"Developer's Skills: {developer_skills}")
# print(f"Required Skills from Bug (Themes that match developer's skills): {skills_required}")
