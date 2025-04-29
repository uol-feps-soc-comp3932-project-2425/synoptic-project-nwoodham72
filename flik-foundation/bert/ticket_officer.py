from sentence_transformers import SentenceTransformer, util
import re
import logging
from app.models import Bug

""" ticket_officer.py: Compare incoming ticket with previous tickets to identify duplicates """

# Load model
model = SentenceTransformer("distilbert-base-nli-stsb-mean-tokens")


# Compare bug description with ApplicationRule entries
def find_similar_tickets(incoming_description, tags):

    # Check for tags
    if not tags:
        return (False, None)

    # Convert text to vector embedding
    incoming_embedding = model.encode(incoming_description, convert_to_tensor=True)

    # Similarity threshold
    threshold = 0.7

    # Store matching tickets
    matches = []

    # Fetch related bugs
    for bug in Bug.query.all():
        # Check tags of incoming ticket and saved ticket are equal
        skills = set(s.name.lower() for s in bug.skills)
        if (set(t.lower() for t in tags)).issubset(skills):
            saved_embedding = model.encode(bug.description, convert_to_tensor=True)
            cosine_sim = util.pytorch_cos_sim(
                saved_embedding, incoming_embedding
            ).item()

            if cosine_sim >= threshold:
                logging.info(
                    f"ticket_officer: Match with [{bug.title}] ({cosine_sim:.4f})"
                )
                matches.append((bug.id, bug.title, cosine_sim))

    # Return three strongest matches
    matches.sort(key=lambda x: x[2], reverse=True)
    top_matches = [{"id": m[0], "title": m[1]} for m in matches[:3]]

    # No matches found
    return (True, top_matches) if top_matches else (False, None)
