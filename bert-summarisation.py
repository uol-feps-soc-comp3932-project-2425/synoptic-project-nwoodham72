from transformers import BertTokenizer, BertModel
import torch
import numpy as np
import nltk
nltk.download('punkt')
from nltk.tokenize import sent_tokenize

# Load BERT tokenizer and model
tokenizer = BertTokenizer.from_pretrained('bert-base-uncased')
model = BertModel.from_pretrained('bert-base-uncased')

# Sample text (bug report or other input)
original_text = """Description
As a Manager User, when submitting a new bug report, multiple duplicate tickets are being created for the same issue instead of just one. This results in unnecessary clutter on the DevOps board and confusion for the team.

Steps to Reproduce (Given, When, Then Format)
Given I am logged in as a Manager user.
And I navigate to the Bug Submission Form.
When I fill in the required fields (Title, Description, Category, Labels, etc.).
And I click the ‘Submit’ button.
Then I expect a single bug ticket to be created in the system and integrated into DevOps.
But Instead, multiple identical tickets are generated in the DevOps board for the same issue.
Expected Behaviour
A single ticket should be created per bug report submission.
The system should prevent duplicate entries for the same request.
A confirmation message (e.g., "Bug successfully submitted") should be displayed.
The bug tracking system should synchronize correctly with DevOps.
Actual Behaviour
Multiple identical tickets are created for a single bug submission.
No error message appears, making it unclear why this happens.
The duplicates appear instantly after submission.
Refreshing the page sometimes leads to even more duplicate tickets."""

# Split text into sentences
sentences = sent_tokenize(original_text)

# Encode each sentence with BERT
sentence_embeddings = []
for sentence in sentences:
    inputs = tokenizer(sentence, return_tensors="pt", padding=True, truncation=True, max_length=512)
    with torch.no_grad():
        outputs = model(**inputs)
    sentence_embedding = outputs.last_hidden_state.mean(dim=1).squeeze().numpy()
    sentence_embeddings.append(sentence_embedding)

# Convert to numpy array for easier processing
sentence_embeddings = np.array(sentence_embeddings)

# Compute document-level embedding (average of all sentence embeddings)
doc_embedding = np.mean(sentence_embeddings, axis=0)

# Compute similarity scores (cosine similarity between each sentence and the document)
similarity_scores = np.dot(sentence_embeddings, doc_embedding) / (
    np.linalg.norm(sentence_embeddings, axis=1) * np.linalg.norm(doc_embedding)
)

# Rank sentences by similarity
top_n = min(3, len(sentences))  # Select top 3 sentences (adjustable)
top_sentence_indices = np.argsort(similarity_scores)[-top_n:]  # Get top-ranked sentences
top_sentence_indices.sort()  # Keep sentences in original order

# Extract summary
summary = " ".join([sentences[i] for i in top_sentence_indices])

print("Extractive Summary:\n", summary)