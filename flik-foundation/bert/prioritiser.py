from transformers import DistilBertTokenizer, DistilBertForSequenceClassification, pipeline
import torch
import os

""" Handles bug ticket priority classification using the fine-tuned DistilBERT model. """

# Load fine-tuned model
local_directory = os.path.dirname(__file__)
MODEL_DIR = os.path.join(local_directory, "./models/fine_tuned_prioritiser")

# Load fine-tuned model and tokenizer
classification_tokeniser = DistilBertTokenizer.from_pretrained(MODEL_DIR)
classification_model = DistilBertForSequenceClassification.from_pretrained(MODEL_DIR)

# Create classifier pipeline
classifier = pipeline('text-classification', model=classification_model, tokenizer=classification_tokeniser)

# Predict priority of bug ticket
def predict_priority(description):
    priority = classifier(description)
    
    # Ensure correct priority mapping (your model has 3 labels: High, Medium, Low)
    priority_mapping = {
        "LABEL_0": ("High", 1), 
        "LABEL_1": ("Medium", 2), 
        "LABEL_2": ("Low", 3)
    }

    predicted_label = priority[0]['label']  # Get predicted label
    priority_label, priority_level = priority_mapping.get(predicted_label, ("Unknown", -1))
    
    return priority_label, priority_level

# # Example usage
# bug_description = "The login page crashes when submitting valid credentials."
# priority, priority_number = predict_priority(bug_description)
# print("Predicted priority:", priority, "(Priority level:", priority_number, ")")
