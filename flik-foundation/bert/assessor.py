from sentence_transformers import SentenceTransformer, util

# Load the pre-trained model
model = SentenceTransformer('distilbert-base-nli-stsb-mean-tokens')

# Define multiple runbook entries with a title and content for each
runbook_entries = [
    {
        "title": "Update Developer Skills",
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
        "content": (
            "Assessments represent the regular legal activities that organisations must undertake. "
            "These include health and safety assessments, fire risk assessments, and more. "
            "Manager users can create new assessments, assign them to organisations, and track their completion. "
        )
    },
]

# Example bug report
bug_report = (
    "I am a manager user and I cannot update the skill of a developer. "  # Manager > developer will return a higher accuracy, but the user could still send the ticket off 
    "I navigate to the developer's profile page and click the 'Edit' button. "
    "when I try to click on the add skill field, the field is greyed out and I cannot add any skills. "
)

# Compute the embedding for the bug report once
bug_report_embedding = model.encode(bug_report, convert_to_tensor=True)

# Define a similarity threshold
threshold = 0.7

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
    print(f"Cosine Similarity Score: {cosine_sim:.2f}")
    
    # If the similarity exceeds the threshold, output the runbook section
    if cosine_sim >= threshold:
        print("Flag: This runbook entry matches the bug report. Runbook content:")
        print(content)
    else:
        print("This runbook entry does not match the bug report.")
    print("-" * 80)