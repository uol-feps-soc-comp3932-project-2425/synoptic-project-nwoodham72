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
    As a user, I am struggling to update my profile picture. I go to my profile page, click on update photo, and then when i select a new picture for my photo and click 'add', nothing happens. I expect to see my new profile picture displayed on my profile page, but the old picture remains.
"""

summary = extractive_summary(bug_description)
predicted_priority = predict_priority(bug_description)

print("Summary:\n", summary)
print("\nPredicted Priority:", predicted_priority)