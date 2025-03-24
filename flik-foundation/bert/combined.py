from sentence_transformers import SentenceTransformer, util
from transformers import pipeline, AutoTokenizer

# Load models
sbert_model = SentenceTransformer('distilbert-base-nli-stsb-mean-tokens')
qa_pipeline = pipeline("text2text-generation", model="google/flan-t5-large")
tokenizer = AutoTokenizer.from_pretrained("google/flan-t5-large")

# Bug report with no explicit role
bug_report_text = (
    "I am a manager user on the organisation screen."
    "I am trying to change the name of an organisation because it has a typo. "
    "I go to the organisation profile, but I don't see any option to edit the name."
)

# Role-aware documentation (no filtering)
runbook_entries = [
    {
        "title": "Update Developer Skills",
        "permitted_roles": ["manager"],
        "content": (
            "To update the skills of a developer, navigate to their profile and click 'Edit'. "
            "Only Manager users can do this. Admin, developers, and clients cannot."
        )
    },
    {
        "title": "Update Organisation Name",
        "permitted_roles": ["manager"],
        "content": (
            "To update an organisation's name, go to the organisation's profile and click 'Edit'. "
            "Edit the name and save. Only Manager users can do this."
        )
    },
    {
        "title": "Assign Assessments",
        "permitted_roles": ["manager"],
        "content": (
            "Managers can assign assessments via the dashboard. "
            "Only Manager users can do this."
        )
    },
    {
        "title": "Developer Dashboard View",
        "permitted_roles": ["developer"],
        "content": (
            "Developers can view their assigned tickets, profile, and activity log from the dashboard."
        )
    }
]

# Step 1: SBERT similarity matching
bug_embedding = sbert_model.encode(bug_report_text, convert_to_tensor=True)
threshold = 0.7
relevant_docs = []

for entry in runbook_entries:
    runbook_embedding = sbert_model.encode(entry["content"], convert_to_tensor=True)
    sim_score = util.pytorch_cos_sim(bug_embedding, runbook_embedding).item()
    if sim_score >= threshold:
        # Include permitted roles in the context
        relevant_docs.append(f"{entry['title']} (Permitted Roles: {', '.join(entry['permitted_roles'])}): {entry['content']}")

# Step 2: Truncate documentation
max_doc_tokens = 250
truncated_docs = []
total_tokens = 0

for doc in relevant_docs:
    tokens = tokenizer.tokenize(doc)
    if total_tokens + len(tokens) <= max_doc_tokens:
        truncated_docs.append(doc)
        total_tokens += len(tokens)
    else:
        break

doc_block = "\n".join(truncated_docs)

# Step 3: Few-shot prompt, updated for no user role
prompt_template = f"""
You are a software bug assessor. Your task is to distinguish between legitimate software defects and events where the author is confused about the system's functionality.

Instructions:
1. Review the documentation provided in doc_block and bug_report_text.
2. If bug_report_text indicates that the documentation is broken and the user's experience is a defect, return 'Bug'.
3. If bug_report_text indicates that the user has not read the documentation, and is confused on the system functionality, return 'Documentation Misunderstanding'. This may be that the user belives they have more permissions than what their role states, or believes there should be an action that is not possible.

Example 1
Bug Report:
I am a developer user and I cannot update the name of an organisation.

Documentation:
Update Organisation Name (Permitted Roles: manager): Only Manager users can rename an organisation.

Classification: Documentation Misunderstanding  
Reason: The user is a developer and does not have the necessary permissions to update the organisation name.

Example 2
Bug Report:
"I am a manager and I cannot update the skills of a developer, when I click 'Add Skill', I get a 403 error.

Documentation:
Update Developer Skills (Permitted Roles: manager): Only managers can update developer skills.

Classification: Bug  
Reason: The user is a manager and should be able to update the developer's skills, so this is a defect in the system functionality according to the documentation.

Now evaluate the following:

Bug Report:
"{bug_report_text}"

Documentation:
{doc_block}

Classification:"""

response = qa_pipeline(prompt_template, max_new_tokens=200)
print("\n📌 Classification:\n", response[0]['generated_text'])