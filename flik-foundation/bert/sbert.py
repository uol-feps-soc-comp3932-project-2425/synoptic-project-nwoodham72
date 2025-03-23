from sentence_transformers import SentenceTransformer, util
import torch

# Load the SBERT model
model = SentenceTransformer('multi-qa-MiniLM-L6-cos-v1')

# Documentation snippets
documentation = [
    "Organisations - Manager user can create, edit and delete organisations. All other users can view organisations and inspect their details."
]

# Bug ticket input
bug_ticket = "I am a developer user and I am trying to change the name of an organisation because it has a typo. When I go to look at the organisation details, I cannot see an option to update the details of the organisation."

# Get embeddings for ticket and docs
doc_embeddings = model.encode(documentation, convert_to_tensor=True)
ticket_embedding = model.encode(bug_ticket, convert_to_tensor=True)

# Compute cosine similarities
cosine_scores = util.pytorch_cos_sim(ticket_embedding, doc_embeddings)[0]

# Sort and print results
results = list(zip(documentation, cosine_scores))
results.sort(key=lambda x: x[1], reverse=True)

print("\n🔍 Top matching documentation:\n")
for doc, score in results:
    print(f"Score: {score.item():.4f} — {doc}")
