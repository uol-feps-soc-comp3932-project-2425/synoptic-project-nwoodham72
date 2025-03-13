from sentence_transformers import SentenceTransformer, util

# Load a pre-trained DistilBERT model fine-tuned for semantic similarity tasks
model = SentenceTransformer('distilbert-base-nli-stsb-mean-tokens')

# Hardcoded runbook text (training guide section)
runbook_text = """"
Manager users can update the skills of developers.
To do this, they must first navigate to the developer's profile page.
Once there, they can click the 'Edit' button to open the edit form.
In the form, they can update the developer's skills and save the changes.
After saving, the developer's skills will be updated across the platform, and Flik can automatically assign tickets of this nature to the developer.
"""

# Example bug report
bug_report = """"
I am a developer user and I cannot update the skill of a developer.
I navigate to the developer's profile page and click the 'Edit' button.
But then the site tells me that I do not have permission to edit the developer's skills.
"""

# Compute embeddings for both texts
runbook_embedding = model.encode(runbook_text, convert_to_tensor=True)
bug_report_embedding = model.encode(bug_report, convert_to_tensor=True)

# Calculate cosine similarity between the two embeddings
cosine_sim = util.pytorch_cos_sim(runbook_embedding, bug_report_embedding)

print("Cosine similarity:", cosine_sim.item())

# Define a similarity threshold (you can adjust this value based on your experiments)
threshold = 0.7

if cosine_sim.item() >= threshold:
    print("Flag: The bug report is semantically similar to the runbook. Consider showing the runbook to the user.")
else:
    print("The bug report does not closely match the runbook content.")
