from transformers import BertTokenizer, BertModel, BertForSequenceClassification
import torch
import torch.nn.functional as F
import numpy as np
import nltk
from nltk.tokenize import sent_tokenize

# Download required NLTK data
nltk.download('punkt')

# =======================================================
# Define your candidate categories for ticket classification.
# You can update this list with the labels relevant to your project.
candidate_categories = [
    "User Profiles",
    "Front-end",
    "Back-end",
    "Team members",
    "Organisation Configuration",
    "Clients"
]
# =======================================================

# ----------------------------
# Part 1: Extractive Summarisation using BERT
# ----------------------------

# Load the BERT tokenizer and model for encoding sentences
tokenizer = BertTokenizer.from_pretrained('bert-base-uncased')
bert_model = BertModel.from_pretrained('bert-base-uncased')

# Sample bug report text
original_text = """ 
The login page is broken. """

# Split text into sentences
sentences = sent_tokenize(original_text)

# Compute BERT embeddings for each sentence
sentence_embeddings = []
for sentence in sentences:
    inputs = tokenizer(sentence, return_tensors="pt", padding=True, truncation=True, max_length=512)
    with torch.no_grad():
        outputs = bert_model(**inputs)
    # Mean pooling over token embeddings to get a sentence-level representation
    sentence_embedding = outputs.last_hidden_state.mean(dim=1).squeeze().numpy()
    sentence_embeddings.append(sentence_embedding)

# Convert to numpy array and compute a document-level embedding (average of sentence embeddings)
sentence_embeddings = np.array(sentence_embeddings)
doc_embedding = np.mean(sentence_embeddings, axis=0)

# Compute cosine similarity between each sentence embedding and the document embedding
similarity_scores = np.dot(sentence_embeddings, doc_embedding) / (
    np.linalg.norm(sentence_embeddings, axis=1) * np.linalg.norm(doc_embedding)
)

# Select top N sentences for the summary (using top 3 sentences)
top_n = min(3, len(sentences))
top_sentence_indices = np.argsort(similarity_scores)[-top_n:]
top_sentence_indices.sort()  # preserve original sentence order

# Generate the extractive summary
summary = " ".join([sentences[i] for i in top_sentence_indices])
print("Extractive Summary:\n", summary)

# ----------------------------
# Part 2: Supervised Classification using BERT for Sequence Classification
# ----------------------------

# Define the number of labels based on your candidate categories
num_labels = len(candidate_categories)

# Load a BERT model for sequence classification.
# Note: This model is not fine-tuned on your domain-specific data, so for meaningful predictions, you must fine-tune it on a labeled dataset.
classification_model = BertForSequenceClassification.from_pretrained('bert-base-uncased', num_labels=num_labels)

# Tokenize the entire bug report text for classification
inputs = tokenizer(original_text, return_tensors="pt", padding=True, truncation=True, max_length=512)
with torch.no_grad():
    outputs = classification_model(**inputs)

# Apply softmax to get probabilities over each category
logits = outputs.logits
probs = F.softmax(logits, dim=-1)
predicted_label_index = torch.argmax(probs, dim=-1).item()
predicted_category = candidate_categories[predicted_label_index]

print("\nPredicted Ticket Category:", predicted_category)
