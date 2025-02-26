from datasets import load_dataset

from transformers import DistilBertTokenizer, DistilBertForSequenceClassification, Trainer, TrainingArguments, pipeline

dataset = load_dataset('cnn_dailymail', '3.0.0')


tokenizer = DistilBertTokenizer.from_pretrained('distilbert-base-uncased')

def preprocess_data(examples):
    inputs = [doc for doc in examples['article']]
    model_inputs = tokenizer(inputs, max_length=512, truncation=True, padding='max_length')

    # Setup the tokenizer for targets
    with tokenizer.as_target_tokenizer():
        labels = tokenizer(examples['highlights'], max_length=128, truncation=True, padding='max_length')

    model_inputs['labels'] = labels['input_ids']
    return model_inputs

tokenized_dataset = dataset.map(preprocess_data, batched=True)


model = DistilBertForSequenceClassification.from_pretrained('distilbert-base-uncased')

training_args = TrainingArguments(
    output_dir='./results',
    num_train_epochs=3,
    per_device_train_batch_size=16,
    per_device_eval_batch_size=16,
    warmup_steps=500,
    weight_decay=0.01,
    logging_dir='./logs',
)

trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=tokenized_dataset['train'],
    eval_dataset=tokenized_dataset['validation']
)

trainer.train()

summarizer = pipeline("summarization", model=model, tokenizer=tokenizer)

text = """
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

summary = summarizer(text, max_length=130, min_length=30, do_sample=False)
print(summary)