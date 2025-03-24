from sentence_transformers import SentenceTransformer, util
import torch

# Load the SBERT model
model = SentenceTransformer('multi-qa-MiniLM-L6-cos-v1')

# Documentation
documentation = [
    """Lectureres can upload lectures via the 'Module' page."
        "Lectureres can delete lectures, but they cannot update them. They need to reupload a new lecture if there is a mistake."
        "Students and lectureres can view uploaded lectures."""
]

# Bug ticket input
bug_ticket = """I am a student user on the 'Module' page." 
                "I am trying to upload a lecture to the 'Module' page, but when I try to upload a lecture I get a 403 error."
                "I should have been able to add a new lecture and find it on the 'Module' page."""

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
