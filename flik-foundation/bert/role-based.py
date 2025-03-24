from sentence_transformers import SentenceTransformer, util

# Load the pre-trained model
model = SentenceTransformer('distilbert-base-nli-stsb-mean-tokens')

# Define multiple runbook entries with a title and content for each
runbook_entries = [
    {
        "title": "Update Developer Skills",
        "permitted_roles": ["manager"],
        "not_permitted_roles": ["developer", "client"],
        "content": (
            "Manager users can update the skills of developers. "  # Inclusion of 'only' increases likelihood of correct matching
            "To do this, they must first navigate to the developer's profile page. "
            "Once there, they can click the 'Edit' button to open the edit form. "
            "In the form, they can update the developer's skills and save the changes. "
            "After saving, the developer's skills will be updated across the platform, "
            "and Flik can automatically assign tickets of this nature to the developer."
            "Only managers can perform this action."
            # "Developers cannot update their own skills or the skills of another developer."  # Highlighting excluded users and restrictions increases likelihood of correct matching
        )
    },
    {
        "title": "Update Organisation Name",
        "permitted_roles": ["manager"],
        "not_permitted_roles": ["developer", "client"],
        "content": (
            "Manager users can update the name of an organisation. "
            "To do this, they must first navigate to the organisation's profile page. "
            "Once there, they can click the 'Edit' button to open the edit form. "
            "In the form, they can update the organisation's name and save the changes. "
            "After saving, the organisation's name will be updated across the platform."
        )
    },
    {
        "title": "Assesments",
        "permitted_roles": ["manager"],
        "not_permitted_roles": ["developer", "client"],
        "content": (
            "Assessments represent the regular legal activities that organisations must undertake. "
            "These include health and safety assessments, fire risk assessments, and more. "
            "Manager users can create new assessments, assign them to organisations, and track their completion. "
        )
    },
    # {
    #     "title": "Lectures",
    #     "permitted_roles": ["lecturer", "admin"],
    #     "not_permitted_roles": ["student"],
    #     "content": (
    #         "I am a lecturer/admin user role."
    #         "Lectureres can upload lectures via the 'Lectures' page."
    #         "Lectureres can delete lectures, but they cannot update them. They need to reupload a new lecture if there is a mistake."
    #         "Students and lecturers can view uploaded lectures."
    #     )
    # },
    {
        "title": "Create finding",
        "permitted_roles": ["developer", "manager"],
        "not_permitted_roles": ["client"],
        # include page
        # "content": ("""
        #             I am a manager user.
        #             I am on the findings page.
        #             Click 'Add finding' to create a new finding.
        #             A new finding can be made with a title and deadline.
        #     """
        # )
        "content": ("""
                    Only developer/manager users can create finding.
                    I am a developer/manager user.
                    I am on the findings page.
                    Action: Click 'Add finding' to create a new finding.
                    Expected Behaviour: A new finding can be made with a title and deadline.
            """
        )
    },
]

# Example bug report
# bug_report = (
#     "I am a admin user role."  # Explicitly adding the user's role to the model evaluation improves accuracy
#     "I am trying to upload a lecture to the lecture page, but when I try to upload a lecture I get a 403 error."
#     "I want to be able to share my notes with my friends."
# )
# bug_report_role = "admin"

# Example bug report
bug_report_role = "manager"
bug_report = (f"""
    Cannot create finding.
    I am a {bug_report_role} user.
    I am on the findings page.
    Action: I am trying to create a new finding. When I go to create a new finding, I get a 403 error and I cannot create one.
    Expected Behaviour: I should have been able to create a new finding.
    """
)


# Compute the embedding for the bug report once
bug_report_embedding = model.encode(bug_report, convert_to_tensor=True)

# Define a similarity threshold
threshold = 0.6

# Evaluate each runbook entry against the bug report
for entry in runbook_entries:
    title = entry["title"]
    content = entry["content"]
    
    # Compute the embedding for the current runbook entry
    runbook_embedding = model.encode(content, convert_to_tensor=True)
    
    # Calculate cosine similarity
    cosine_sim = util.pytorch_cos_sim(runbook_embedding, bug_report_embedding).item()
    
    # Output the title and similarity score
    print("-" * 80)
    print(f"Title: {title}")
    print(f"Cosine Similarity Score: {cosine_sim:.4f}")
    
    # If the similarity exceeds the threshold, output the runbook section
    if cosine_sim >= threshold:
        print("Flag: This runbook entry matches the bug report.")

        # Check if the user role matches the permitted roles
        if bug_report_role in entry["permitted_roles"]:
            print("Role is PERMITTED - indicates that this is a bug")
            print("Send to board")
        else:
            print("Role is NOT PERMITTED - indicates that this is a documentation misunderstanding")  
            # should the user have the option to send the ticket?
            # should the user be able to raise this as a change request instead? -> future work
            print(content)
    else:
        print("This runbook entry does not match the bug report.")
    print("-" * 80)