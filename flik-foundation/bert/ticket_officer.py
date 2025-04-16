from sentence_transformers import SentenceTransformer, util
import re
import logging
from app.models import ApplicationRule

# Load model
model = SentenceTransformer('distilbert-base-nli-stsb-mean-tokens')

# Compare bug description with ApplicationRule entries
def assess_documentation(action_comparison, bug_description_role):
    # Convert text to vector embedding
    bug_embedding = model.encode(action_comparison, convert_to_tensor=True)

    # Similarity threshold 
    threshold = 0.6

    # Store matching entries
    matches = []

    # Fetch complete rule entries
    documentation = [
        r for r in ApplicationRule.query.all()
        if r.page is not None and r.roles
    ]

    # Compare rules with bug description
    for rule in documentation:
        action = rule.description
        action_embedding = model.encode(action, convert_to_tensor=True)  # Convert text to vector embedding
        cosine_sim = util.pytorch_cos_sim(action_embedding, bug_embedding).item()  # Assess similarity between bug description and rule
        logging.info(f"[{rule.title}] Similarity: {cosine_sim:.4f}")
    
        if cosine_sim >= threshold:
            logging.info(f"Match - Similarity: {cosine_sim:.4f}")
            permitted_roles = [r.name for r in rule.roles]
            # Check if user's role is not permitted to perform the described action / bug description
            if bug_description_role.lower() not in [r.lower() for r in permitted_roles]:
                logging.info("User role not in permitted roles - Return documentation to user.")
                
                matches.append({
                    "title": rule.title,
                    "permitted_roles": permitted_roles,
                    "action": rule.description
                })
            # Role is permitted
            else:
                logging.info("User role is in permitted roles - Indicative of bug.")

    # No matches found 
    return (True, matches) if matches else (False, None)


                


