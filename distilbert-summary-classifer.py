""" DistilBERT Model """

import nltk
import torch
from summarizer import Summarizer
from transformers import DistilBertTokenizer, DistilBertForSequenceClassification, pipeline

nltk.download("punkt")

# Load summariser model
summariser = Summarizer(model="distilbert-base-uncased")

# Load classification model
classification_tokeniser = DistilBertTokenizer.from_pretrained('distilbert-base-uncased')
classification_model = DistilBertForSequenceClassification.from_pretrained('distilbert-base-uncased', num_labels=3)

# Create classifier pipeline
classifier = pipeline("text-classification", model=classification_model, tokenizer=classification_tokeniser)

# Generate extractive summary of bug ticket
def extractive_summary(description, ratio=0.3):  # :param text: The full bug description. :param ratio: Fraction of sentences to retain.
    summary = summariser(description, ratio=ratio)
    return summary

def predict_priority(description):
    priority = classifier(description)
    priority_labels = {"LABEL_0": "low", "LABEL_1": "medium", "LABEL_2": "high"}
    predicted_priority = priority_labels[priority[0]['label']]
    return predicted_priority

# Ticket description
bug_description = """
    As a Manager User, when attempting to update a team member’s skills, I can type in a new skill, but clicking ‘Add Skill’ does not update the developer’s profile. There is no confirmation message, error message, or indication that the action has been processed. 
    Steps to Reproduce (Given, When, Then Format) 
    Given I am logged in as a Manager user. 
    And I navigate to Team Management > Select a Team Member > Click Edit Skills. 
    When I type a new skill into the input field. 
    And I click the ‘Add Skill’ button. 
    Then I expect the new skill to be added to the team member’s profile. 
    And I expect to receive a confirmation message or visual feedback. 
    But Instead, the skill is not added, and no feedback is provided. 
    Expected Behaviour 
    The newly added skill should appear in the developer’s Skills section. 
    A confirmation message (e.g., "Skill successfully added") should be displayed. 
    The change should persist after reloading the page. 
    Actual Behaviour 
    The skill is not added to the developer’s profile. 
    No success or error message appears. 
    The page does not update to reflect the change. 
    After refreshing, the skill is still missing. 
"""

summary = extractive_summary(bug_description)
predicted_priority = predict_priority(bug_description)

print("Summary:\n", summary)
print("\nPredicted Priority:", predicted_priority)