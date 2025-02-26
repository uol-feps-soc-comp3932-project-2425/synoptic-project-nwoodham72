""" DistilBERT Attempt 2 """

from transformers import DistilBertTokenizer, DistilBertForSequenceClassification, pipeline

# Load model and tokeniser
tokeniser = DistilBertTokenizer.from_pretrained('distilbert-base-uncased')
model = DistilBertForSequenceClassification.from_pretrained('distilbert-base-uncased')

# Create summarisation pipeline
summariser = pipeline("summarization", model=model, tokenizer=tokeniser)

input_text = """
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

# Generate summary 
summary = summariser(input_text, max_length=150, min_length=30, do_sample=False)