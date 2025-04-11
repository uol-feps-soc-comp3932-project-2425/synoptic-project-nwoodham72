from sentence_transformers import SentenceTransformer, util
import re
import logging
from app.models import ApplicationRule

# Load model
model = SentenceTransformer('distilbert-base-nli-stsb-mean-tokens')

# todo: retrieve documentation from database


def assess_documentation(bug_description, bug_description_role):
    # Convert text to vector embedding
    bug_description_embedding = model.encode(bug_description, convert_to_tensor=True)

    # Similarity threshold 
    threshold = 0.6

    # Store matching entries
    matches = []

    documentation = ApplicationRule.query.all()

    # Compare rules with bug description
    for rule in documentation:
        action = rule.description
        action_embedding = model.encode(action, convert_to_tensor=True)  # Convert text to vector embedding
        cosine_sim = util.pytorch_cos_sim(action_embedding, bug_description_embedding).item()  # Assess similarity between bug description and rule
        logging.info(f"Similarity: {cosine_sim:.4f}")

        if cosine_sim >= threshold:
            logging.info(f"Match - Similarity: {cosine_sim:.4f}")
            permitted_roles = [r.name for r in rule.roles]
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


                


    # # Compare documentation entry with bug
    # if documentation:
    #     for entry in documentation:
    #         action = entry["action"]

    #         # Embed action 
    #         action_embedding = model.encode(action, convert_to_tensor=True)

    #         # Assess similarity between bug description and documentation entry 
    #         cosine_sim = util.pytorch_cos_sim(action_embedding, bug_description_embedding).item()
    #         logging.info(f"Cosine Similarity: {cosine_sim:.4f}")

    #         # Check similarity
    #         if cosine_sim >= threshold:
    #             logging.info(f"Threshold met: {cosine_sim:.4f}")
    #             # Check if role is permitted
    #             if bug_description_role.lower() not in [r.lower() for r in entry["permitted_roles"]]:                
    #                 logging.info("User role not in permitted roles - Return documentation to user.")
    #                 # Clean entry
    #                 cleaned_entry = re.sub(r"^I am a .*? page\.\s*", "", entry["action"])  # Remove "I am a <user> user on the <page> page" sentence from documentation entry output
    #                 matches.append({
    #                     "title": entry["title"],
    #                     "permitted_roles": entry["permitted_roles"],
    #                     "action": cleaned_entry,
    #                     "sim_score": round(cosine_sim, 2)
    #                 })
    #     # Return documentation matches
    #     if matches:
    #         return True, matches

    #     # No match found
    #     return False, None

    # # No documentation found
    # return False, None

# # Example usage
# if __name__ == "__main__":
#     # bug_description = """
#     # I am a client user on the modules page.
#     # I am trying to update the name of a module. I can update other details such as the cover image, but when I go to update the name and click save, I get a message saying the 'name is not valid'.
#     # I should have been able to update the name of the module.    
#     # """
#     # bug_description_role = "manager"
#     bug_description = """
#     I am a client user on the login page.
#     I am trying to update my password via the 'Forgot password' button on the login page. When I click on the link it says that the page does not exist.
#     The reset password page should be available. 
#     """
#     bug_description_role = "client"
    
#     assess_documentation(bug_description, bug_description_role)


                


