from transformers import DistilBertTokenizer, DistilBertForSequenceClassification, pipeline
import torch
import os

""" prioritiser.py: Handles bug ticket priority classification using the fine-tuned DistilBERT model. """

# Load fine-tuned model
local_directory = os.path.dirname(__file__)
MODEL_DIR = os.path.join(local_directory, "./models/fine_tuned_prioritiser")

# Load fine-tuned model and tokenizer
classification_tokeniser = DistilBertTokenizer.from_pretrained(MODEL_DIR)
classification_model = DistilBertForSequenceClassification.from_pretrained(MODEL_DIR)
classification_model.eval()

# Ensure correct priority mapping (your model has 3 labels: High, Medium, Low)
priority_mapping = {
    "LABEL_0": ("High", 1), 
    "LABEL_1": ("Medium", 2), 
    "LABEL_2": ("Low", 3)
}


# Predict priority of bug ticket
def predict_priority(description, use_thresholding: bool = True):
    inputs = classification_tokeniser(description, return_tensors="pt", truncation=True, padding=True, max_length=512)
    with torch.no_grad():
        outputs = classification_model(**inputs)
        probs = torch.softmax(outputs.logits, dim=1).squeeze()  # Fetch probabilities of eah label and convert probabilities into 1D vector

    # Apply post-softmax thresholding to avoid weak predictions and overprediction of 'medium' label
    if use_thresholding:
        if probs[1] >= 0.60:
            pred_idx = 1  # Medium
        elif probs[2] > 0.40 and probs[1] < 0.50:
            pred_idx = 2  # Low
        elif (probs[1] - probs[0]) < 0.10:
            pred_idx = 0  # Return 'High' priority if unsure between 'High' and 'Medium'
        else:
            pred_idx = torch.argmax(probs).item()
    else:
        pred_idx = torch.argmax(probs).item()

    return priority_mapping[pred_idx]

# # Example usage
# bug_description = "The login page crashes when submitting valid credentials."
# priority, priority_number = predict_priority(bug_description)
# print("Predicted priority:", priority, "(Priority level:", priority_number, ")")
