from sentence_transformers import SentenceTransformer, util
import re
import logging
from app.models import ApplicationRule

""" assessor.py: Compare incoming ticket with documentation to distinguish legitimacy """

# Load model
model = SentenceTransformer("distilbert-base-nli-stsb-mean-tokens")


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
        r for r in ApplicationRule.query.all() if r.page is not None and r.roles
    ]

    # Compare rules with bug description
    for rule in documentation:
        rule_embedding = model.encode(
            rule.description, convert_to_tensor=True
        )  # Convert rule to vector embedding
        cosine_sim = util.pytorch_cos_sim(
            rule_embedding, bug_embedding
        ).item()  # Assess similarity between bug description and rule

        if cosine_sim >= threshold:
            logging.info(f"assessor: Match with [{rule.title}] ({cosine_sim:.4f})")
            permitted_roles = [r.name for r in rule.roles]
            # Check if user's role is not permitted to perform the described action / bug description
            if bug_description_role.lower() not in [r.lower() for r in permitted_roles]:
                logging.info(
                    "User role not in permitted roles - Return documentation to user."
                )

                matches.append(
                    {
                        "title": rule.title,
                        "permitted_roles": permitted_roles,
                        "action": rule.description,
                    }
                )
            # Role is permitted
            else:
                logging.info("User role is in permitted roles - Indicative of bug.")

    # No matches found
    return (True, matches) if matches else (False, None)


# Example usage
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
