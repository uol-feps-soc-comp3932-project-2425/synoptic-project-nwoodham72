""" Fine-Tuning DistilBERT for Extractive Summarization """

from datasets import load_dataset
from transformers import AutoTokenizer, AutoModelForSequenceClassification, Trainer, TrainingArguments
from torch.utils.data import Dataset
import torch
import nltk
import numpy as np

nltk.download('punkt')

# Load CNN/DailyMail dataset
dataset = load_dataset("cnn_dailymail", "3.0.0")

# Training set
train_articles = dataset["train"]["article"][:500]
train_summaries = dataset["train"]["highlights"][:500]

# Validation set
validation_articles = dataset["validation"]["article"][:100]
validation_summaries = dataset["validation"]["highlights"][:100]

# Test set
test_articles = dataset["test"]["article"][:100]
test_summaries = dataset["test"]["highlights"][:100]

# Sentence Tokenization
def split_into_sentences(text):
    return nltk.sent_tokenize(text)

# Define Dataset for Extractive Summarization
class SummarisationDataset(Dataset):
    def __init__(self, articles, summaries, tokenizer, max_length=512):
        self.articles = articles
        self.summaries = summaries
        self.tokenizer = tokenizer
        self.max_length = max_length

    def __len__(self):
        return len(self.articles)

    def __getitem__(self, idx):
        sentences = split_into_sentences(self.articles[idx])  # Split article into sentences

        # ✅ Tokenize the full article at once
        inputs = self.tokenizer(
            self.articles[idx],  
            truncation=True,
            padding="max_length",
            max_length=self.max_length,
            return_tensors="pt",
        )

        # ✅ Define labels: A binary label (1 if sentence appears in summary, else 0)
        labels = torch.tensor([
            1 if sentence in self.summaries[idx] else 0 for sentence in sentences
        ])

        return {
            "input_ids": inputs["input_ids"].squeeze(0),
            "attention_mask": inputs["attention_mask"].squeeze(0),
            "labels": labels[: inputs["input_ids"].shape[1]]  # Ensure correct sequence length
        }

# ✅ Load DistilBERT model as a classification model
model_name = "distilbert-base-uncased"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForSequenceClassification.from_pretrained(model_name, num_labels=2)

# Prepare dataset
train_dataset = SummarisationDataset(train_articles, train_summaries, tokenizer)
eval_dataset = SummarisationDataset(validation_articles, validation_summaries, tokenizer)
test_dataset = SummarisationDataset(test_articles, test_summaries, tokenizer)

# Set Up Training Arguments
training_args = TrainingArguments(
    output_dir="./saved_model",
    per_device_train_batch_size=4,  # ✅ Reduce batch size to avoid memory issues
    num_train_epochs=3,
    save_steps=500,
    save_total_limit=2,
    evaluation_strategy="epoch",
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

print("✅ Model training complete.")

# Extractive Summarization Function
def extract_summary(text, model, tokenizer, ratio=0.3):
    sentences = split_into_sentences(text)

    # ✅ Tokenizing full text at once
    inputs = tokenizer(
        text,  
        truncation=True,
        padding="max_length",
        max_length=512,
        return_tensors="pt",
    )

    with torch.no_grad():
        outputs = model(**inputs).logits  # ✅ Get classification scores
        sentence_scores = outputs[:, 1].cpu().numpy()  # ✅ Use probability of "important sentence"

    # ✅ Select top-ranked sentences
    ranked_sentences = [sentences[i] for i in np.argsort(sentence_scores)[-int(len(sentences) * ratio):][::-1]]

    return " ".join(ranked_sentences)

# Test trained model on first 5 test articles
for i, test_text in enumerate(test_articles[:5]):
    summary = extract_summary(test_text, model, tokenizer, ratio=0.3)
    print(f"\n🔹 Extractive Summary {i+1}:\n", summary)
