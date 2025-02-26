import pandas as pd
import torch
from transformers import DistilBertTokenizer, DistilBertForSequenceClassification, Trainer, TrainingArguments
from torch.utils.data import Dataset

# Load dataset
df = pd.read_csv('trial.csv')

# Concatenate subject and body to create description
df['description'] = df['subject'].fillna('') + ' ' + df['body']

# Map priority labels to integers
label_map = {'low': 0, 'medium': 1, 'high': 2}
df['label'] = df['priority'].map(label_map)

# Define custom dataset
class BugReportDataset(Dataset):
    def __init__(self, descriptions, labels, tokenizer, max_length=512):
        self.descriptions = descriptions
        self.labels = labels
        self.tokenizer = tokenizer
        self.max_length = max_length

    def __len__(self):
        return len(self.descriptions)

    def __getitem__(self, idx):
        inputs = self.tokenizer(
            self.descriptions[idx],
            truncation=True,
            padding="max_length",
            max_length=self.max_length,
            return_tensors="pt",
        )
        inputs = {k: v.squeeze() for k, v in inputs.items()}
        inputs['labels'] = torch.tensor(self.labels[idx], dtype=torch.long)
        return inputs

# Load tokenizer and model
tokenizer = DistilBertTokenizer.from_pretrained('distilbert-base-uncased')
model = DistilBertForSequenceClassification.from_pretrained('distilbert-base-uncased', num_labels=3)

# Prepare dataset
train_dataset = BugReportDataset(df['description'].tolist(), df['label'].tolist(), tokenizer)

# Set up training arguments
training_args = TrainingArguments(
    output_dir='./results',
    num_train_epochs=3,
    per_device_train_batch_size=8,
    per_device_eval_batch_size=8,
    warmup_steps=500,
    weight_decay=0.01,
    logging_dir='./logs',
    logging_steps=10,
)

# Initialize Trainer
trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=train_dataset,
)

# Train the model
trainer.train()

# Save the fine-tuned model
model.save_pretrained('./fine-tuned-model')
tokenizer.save_pretrained('./fine-tuned-model')

print("Model fine-tuning complete.")