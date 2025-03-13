from transformers import DistilBertTokenizer, DistilBertForSequenceClassification, pipeline

""" Handles bug ticket priority classification using the Hugging Face DistilBERT model. """

# Load classification model
classification_tokeniser = DistilBertTokenizer.from_pretrained('distilbert-base-uncased')
classification_model = DistilBertForSequenceClassification.from_pretrained('distilbert-base-uncased', num_labels=4)

# Create classifier pipeline
classifier = pipeline('text-classification', model=classification_model, tokenizer=classification_tokeniser)

# Predict priority of bug ticket
def predict_priority(description):
    priority = classifier(description)
    priority_mapping = {"LABEL_0": ("Immediate", 1), "LABEL_1": ("High", 2), "LABEL_2": ("Medium", 3), "LABEL_3": ("Low", 4)}
    priority_label, priority_level = priority_mapping[priority[0]['label']]
    return priority_label, priority_level

# # Ticket description
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

# Predict and output priority
# priority, priority_number = predict_priority(bug_description)
# print("Predicted priority:", priority, "(Priority level:", priority_number, ")")