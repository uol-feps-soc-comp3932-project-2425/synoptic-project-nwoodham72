import os
import torch
import pandas as pd
from datasets import Dataset
from transformers import DistilBertTokenizer, DistilBertForSequenceClassification, Trainer, TrainingArguments

# Load tokenizer
tokenizer = DistilBertTokenizer.from_pretrained("distilbert-base-uncased")

# Load dataset
file_path = "C:\\Users\\User\\Desktop\\YEAR 4\\COMP3932 - Synoptic Project\\Datasets\\To Use\\customer-it-support\\priorities_clean.csv"
df = pd.read_csv(file_path)

# Drop rows where 'priority' or 'body' is missing
df = df.dropna(subset=["priority", "body"])  
df["body"] = df["body"].astype(str)  # Ensure all descriptions are strings

# Normalize priority values to lowercase
df["priority"] = df["priority"].astype(str).str.strip().str.lower()

# Ensure 'priority' values are valid
valid_priorities = {"high", "medium", "low"}  
df = df[df["priority"].isin(valid_priorities)]  # Keep only valid labels

# Print dataset size after filtering
print(f"Dataset size after filtering: {len(df)}")

if df.empty:
    raise ValueError("Filtered dataset is empty! Check priority values in CSV.")

# Convert text labels to numerical labels
priority_mapping = {"high": 0, "medium": 1, "low": 2}  
df["label_id"] = df["priority"].map(priority_mapping)

# Ensure no NaN values remain after mapping
df = df.dropna(subset=["label_id"])  

# Convert labels to integers
df["label_id"] = df["label_id"].astype(int)  

# Convert to Hugging Face Dataset
df.rename(columns={"label_id": "labels"}, inplace=True)
dataset = Dataset.from_pandas(df[['body', 'labels']])

# Print dataset size after conversion
print(f"Dataset size after conversion: {len(dataset)}")

# Split into training & evaluation sets (80% train, 20% eval)
train_size = int(0.8 * len(dataset))
if train_size == 0:
    raise ValueError("Training dataset is empty after splitting!")

train_dataset = dataset.select(range(train_size))
eval_dataset = dataset.select(range(train_size, len(dataset)))

# Print split sizes
print(f"Train dataset size: {len(train_dataset)}")
print(f"Eval dataset size: {len(eval_dataset)}")

# Tokenization function
def tokenize_function(examples):
    return tokenizer(examples["body"], padding="max_length", truncation=True)

# Apply tokenization
train_dataset = train_dataset.map(tokenize_function, batched=True)
eval_dataset = eval_dataset.map(tokenize_function, batched=True)

# Print final dataset sizes after tokenization
print(f"Train dataset size after tokenization: {len(train_dataset)}")
print(f"Eval dataset size after tokenization: {len(eval_dataset)}")

# Load model with correct number of labels
model = DistilBertForSequenceClassification.from_pretrained("distilbert-base-uncased", num_labels=len(priority_mapping))

# Training arguments with frequent saving
training_args = TrainingArguments(
    output_dir="./results", 
    evaluation_strategy="steps",  # Ensures evaluation happens during training
    save_strategy="steps",  # Saves more frequently
    save_steps=250,  # Saves progress every 250 steps
    num_train_epochs=3,  
    per_device_train_batch_size=8,  # Reduced to prevent crashes
    per_device_eval_batch_size=8,
    logging_dir="./logs",
    logging_steps=50,  # Logs every 50 steps
    save_total_limit=3,  # Keeps only the last 3 saved checkpoints
    load_best_model_at_end=True  # Loads the best model after training
)

# Check for latest checkpoint to resume training
checkpoint_dir = "./results"
checkpoints = [d for d in os.listdir(checkpoint_dir) if d.startswith("checkpoint-")]
if checkpoints:
    latest_checkpoint = os.path.join(checkpoint_dir, sorted(checkpoints, key=lambda x: int(x.split('-')[-1]))[-1])
    print(f"Resuming training from {latest_checkpoint}")
else:
    latest_checkpoint = None
    print("No previous checkpoints found. Starting fresh.")

# Trainer
trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=train_dataset,
    eval_dataset=eval_dataset,  # Providing eval dataset fixes Trainer errors
    tokenizer=tokenizer,
)

# Train model, resuming if possible
trainer.train(resume_from_checkpoint=latest_checkpoint)

# Save fine-tuned model
model.save_pretrained("./fine_tuned_prioritiser")
tokenizer.save_pretrained("./fine_tuned_prioritiser")

print("Fine-tuning complete. Model saved.")
