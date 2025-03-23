import pandas as pd
import torch
from datasets import Dataset
from sklearn.preprocessing import MultiLabelBinarizer
from transformers import (
    DistilBertTokenizer,
    DistilBertForSequenceClassification,
    TrainingArguments,
    Trainer
)

# Load dataset
file_path = "C:\\Users\\User\\Desktop\\YEAR 4\\COMP3932 - Synoptic Project\\Datasets\\To Use\\customer-it-support\\classifications_clean_tagged.csv"
df = pd.read_csv(file_path)

# Combine subject and body into one input text
df["text"] = df["subject"].fillna('') + " " + df["body"].fillna('')

# Ensure tags are parsed as lists (if they're strings like "['A', 'B']")
df["tags"] = df["tags"].apply(eval) if isinstance(df["tags"].iloc[0], str) else df["tags"]

# Get all unique tags for binarization
mlb = MultiLabelBinarizer()
binary_labels = mlb.fit_transform(df["tags"])
label_names = mlb.classes_

# Add one-hot encoded labels
for idx, label in enumerate(label_names):
    df[label] = binary_labels[:, idx]

# Prepare Hugging Face Dataset
label_columns = list(label_names)
df["labels"] = df[label_columns].astype(float).values.tolist()
dataset = Dataset.from_pandas(df[["text", "labels"]])

# Tokenize
tokenizer = DistilBertTokenizer.from_pretrained("distilbert-base-uncased")
def tokenize(batch):
    return tokenizer(batch["text"], padding="max_length", truncation=True)

dataset = dataset.map(tokenize, batched=True)

# Split into train/eval (80/20 split)
split_idx = int(0.8 * len(dataset))
train_dataset = dataset.select(range(split_idx))
eval_dataset = dataset.select(range(split_idx, len(dataset)))

# Define model
model = DistilBertForSequenceClassification.from_pretrained(
    "distilbert-base-uncased", 
    num_labels=len(label_names),
    problem_type="multi_label_classification"
)

# Define trainer
training_args = TrainingArguments(
    output_dir="./results",
    evaluation_strategy="steps",  # Save checkpoints every 250 steps 
    save_strategy="steps",
    save_steps=250,
    num_train_epochs=3,
    per_device_train_batch_size=8,
    per_device_eval_batch_size=8,
    logging_dir="./logs",
    logging_steps=50,
    save_total_limit=3,
    load_best_model_at_end=True,
    metric_for_best_model="eval_loss"
)

trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=train_dataset,
    eval_dataset=eval_dataset,
    tokenizer=tokenizer
)

# Train
trainer.train()

# Save final model and label mappings
model.save_pretrained("./fine_tuned_assigner")
tokenizer.save_pretrained("./fine_tuned_assigner")

# Save label names for future use
import json
with open("label_names.json", "w") as f:
    json.dump(label_names.tolist(), f)

print("✅ Model trained and saved!")
