""" Training and Fine-Tuning for DistilBERT model """

from datasets import load_dataset
from summarizer import Summarizer
from transformers import AutoTokenizer, Trainer, TrainingArguments

from torch.utils.data import Dataset
import torch

# Load CNN/DailyMail dataset
dataset = load_dataset("cnn_dailymail", "3.0.0")

# Training set
train_articles = dataset["train"]["article"][:500]  # Train on first 500 articles
train_summaries = dataset["train"]["highlights"][:500]  # Train on first 500 summaries

# Validation set
validation_articles = dataset["validation"]["article"][
    :100
]  # Validate on first 100 articles
validation_summaries = dataset["validation"]["highlights"][
    :100
]  # Validate on first 100 summaries

# Test set
test_articles = dataset["test"]["article"][:100]  # Test on first 100 articles
test_summaries = dataset["test"]["highlights"][:100]  # Test on first 100 summaries


# Define custom dataset
class SummarisationDataset(Dataset):
    def __init__(self, articles, summaries, tokenizer, max_length=512):
        self.articles = articles
        self.summaries = summaries
        self.tokenizer = tokenizer
        self.max_length = max_length

    def __len__(self):
        return len(self.articles)

    def __getitem__(self, idx):
        inputs = self.tokenizer(
            self.articles[idx],
            truncation=True,
            padding="max_length",
            max_length=self.max_length,
            return_tensors="pt",
        )
        labels = self.tokenizer(
            self.summaries[idx],
            truncation=True,
            padding="max_length",
            max_length=self.max_length,
            return_tensors="pt",
        )["input_ids"]
        return {**inputs, "labels": labels}


# Load DistilBERT model and tokenizer
model_name = "distilbert-base-uncased"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = Summarizer(model_name)

# Prepare model for training
train_dataset = SummarisationDataset(train_articles, train_summaries, tokenizer)
eval_dataset = SummarisationDataset(
    validation_articles, validation_summaries, tokenizer
)
test_dataset = SummarisationDataset(test_articles, test_summaries, tokenizer)

# Set Up Training Arguments
training_args = TrainingArguments(
    output_dir="./saved_model",
    per_device_train_batch_size=8,
    num_train_epochs=3,
    save_steps=500,
    save_total_limit=2,
    eval_strategy="epoch",
    logging_dir="./logs",
)

# Train the Model
trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=train_dataset,
    eval_dataset=eval_dataset,
)

trainer.train()

# Save trained model
model.save_pretrained("./saved_model")
tokenizer.save_pretrained("./saved_model")

print("Model training complete.")

# Test trained model
results = trainer.evaluate(test_dataset)
print("Test set results:", results)
