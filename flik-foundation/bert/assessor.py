from sentence_transformers import SentenceTransformer, util
import re

# Load model
model = SentenceTransformer('distilbert-base-nli-stsb-mean-tokens')

# todo: retrieve documentation from database


def assess_documentation(bug_description, bug_description_role):
    # Compute description embedding 
    bug_description_embedding = model.encode(bug_description, convert_to_tensor=True)

    # Similarity threshold 
    threshold = 0.6

    # Get documentation
    documentation = [
        {
            "title": "Update Module Details",
            "permitted_roles": ["manager"],
            "not_permitted_roles": ["developer", "client"],
            "action": (
                "I am a manager user. "
                "I am on the modules page. "
                "I can access the details of a module on the modules page. "
                "I can update the details of a module on the modules page, including the name, year running and cover picture. "
            )
        },
        {
            "title": "Reset Password",
            "permitted_roles": ["manager", "developer"],
            "not_permitted_roles": ["client"],
            "action": (
                "I am a manager/developer user. "
                "I am on the login page. "
                "Any user can reset their password through the 'Forgot your Password?' button on the login page. "
                "After accessing the link, the user is prompted to enter their email, where a new password reset link will be sent. "
                "A user can open the link in the sent email to reset their password. "
            )
        },
        {
            "title": "Reset Account Password",
            "permitted_roles": ["manager", "developer"],
            "not_permitted_roles": ["client"],
            "action": (
                "I am a manager/developer user. "
                "I am on the login page. "
                "Any user can reset their password through the 'Change password' button on the account page. "
                "After accessing the link, the user is prompted to enter their email, where a new password reset link will be sent. "
                "A user can open the link in the sent email to reset their password. "
            )
        }
    ]

    # Compare documentation entry with bug
    for entry in documentation:
        title = entry["title"]
        action = entry["action"]

        # Embed action 
        action_embedding = model.encode(action, convert_to_tensor=True)

        # Assess similarity between bug description and documentation entry 
        cosine_sim = util.pytorch_cos_sim(action_embedding, bug_description_embedding).item()

        print(f"Title: {title}")
        print(f"Cosine Similarity Score: {cosine_sim:.4f}")

        # Check similarity
        if cosine_sim >= threshold:
            print("Documentation and bug description match")
            # Check if role is permitted
            if bug_description_role.lower() in [r.lower() for r in entry["permitted_roles"]]:
                print("permitted role - likely a bug")
                return False, None  # Successful bug, no need to send documentation snippet to routes.py
            # Role is not permitted to perform action
            else:
                print("role is not permitted - likely a documentation error")
                # Clean entry
                cleaned_entry = re.sub(r"^I am a .*? page\.\s*", "", entry["action"])  # Remove first 2 sentences
                return True, {
                    "title": entry["title"],
                    "permitted_roles": entry["permitted_roles"],
                    "action": cleaned_entry
                }
    # No match found
    return False, None

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

                


