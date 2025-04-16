from sentence_transformers import SentenceTransformer, util
import re
import logging
from app.models import Bug

# Load model
model = SentenceTransformer('distilbert-base-nli-stsb-mean-tokens')

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
    tag_matches = []

    # Fetch related bugs
    for bug in Bug.query.all():
        skills = set(s.name.lower() for s in bug.skills)
        if (set(t.lower() for t in tags)).issubset(skills):
            tag_matches.append(bug)
    
    for bug in tag_matches:
        saved_description = bug.description
        saved_embedding = model.encode(saved_description, convert_to_tensor=True)
        cosine_sim = util.pytorch_cos_sim(saved_embedding, incoming_embedding).item()
        logging.info(f"ticket_officer: [{bug.title}] Similarity: {cosine_sim:.4f}")

        if cosine_sim >= threshold:
            logging.info(f"Match - Similarity: {cosine_sim:.4f}")
            matches.append({
                "title": bug.title
            })

    # No matches found
    return (True, matches) if matches else (False, None)
            


                


