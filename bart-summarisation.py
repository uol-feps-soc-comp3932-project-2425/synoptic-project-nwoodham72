from transformers import BartTokenizer, BartForConditionalGeneration
import torch

tokenizer = BartTokenizer.from_pretrained('facebook/bart-large-cnn')
model = BartForConditionalGeneration.from_pretrained('facebook/bart-large-cnn')

original_text = """Description
As a Manager User, when submitting a new bug report, multiple duplicate tickets are being created for the same issue instead of just one. This results in unnecessary clutter on the DevOps board and confusion for the team.

Steps to Reproduce (Given, When, Then Format)
Given I am logged in as a Manager user.
And I navigate to the Bug Submission Form.
When I fill in the required fields (Title, Description, Category, Labels, etc.).
And I click the ‘Submit’ button.
Then I expect a single bug ticket to be created in the system and integrated into DevOps.
But Instead, multiple identical tickets are generated in the DevOps board for the same issue.
Expected Behaviour
A single ticket should be created per bug report submission.
The system should prevent duplicate entries for the same request.
A confirmation message (e.g., "Bug successfully submitted") should be displayed.
The bug tracking system should synchronize correctly with DevOps.
Actual Behaviour
Multiple identical tickets are created for a single bug submission.
No error message appears, making it unclear why this happens.
The duplicates appear instantly after submission.
Refreshing the page sometimes leads to even more duplicate tickets."""
                        
inputs = tokenizer(original_text, return_tensors='pt', max_length=1024, truncation=True)
summary_ids = model.generate(inputs['input_ids'], num_beams=4, max_length=150, early_stopping=True)
summary = tokenizer.decode(summary_ids[0], skip_special_tokens=True)
print("Summary:", summary)