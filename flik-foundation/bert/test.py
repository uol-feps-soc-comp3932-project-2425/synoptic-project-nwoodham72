from transformers import pipeline

# Load model
model_id = "google/flan-t5-large"
qa_pipeline = pipeline("text2text-generation", model=model_id)

# 🔹 Bug report to evaluate
bug_report = (
    "I am a manager user and I am trying to change the name of an organisation because it has a typo. "
    # "I am a manager user and I cannot update the skill of a developer. I navigate to the developer's profile page and click the 'Edit' button. when I try to click on the add skill field, the field is greyed out and I cannot add any skills. ",
)

# 🔹 Documentation 
documentation = [
    "Organisations - Manager user can create, edit and delete organisations. All other users can view organisations and inspect their details.",
    """Developer Skills - Manager users can update the skills of developers.  
            To do this, they must first navigate to the developer's profile page. 
            Once there, they can click the 'Edit' button to open the edit form. 
            In the form, they can update the developer's skills and save the changes. 
            After saving, the developer's skills will be updated across the platform
            Only Manager users can perform this action. Admin, developers and clients cannot perform this action.
    """
]

# 🔹 Build documentation string for prompt
doc_block = "\n".join(f"{i+1}. {doc}" for i, doc in enumerate(documentation))

# 🔹 Prompt template
prompt_template = f"""
You are tasked with identifying whether a user's bug report describes a legitimate software bug or a misunderstanding of a software system.

You must:
1. Check what actions the user's role is allowed to perform in the documentation.
2. If the role is allowed to do the action, but the action is failing, classify the report as 'Bug'.
3. If the role is *not* allowed to perform the action, and they are expecting to be able to, classify it as 'Documentation Misunderstanding'.

---

Example 1
Bug Report:
"I am a developer user and I am trying to change the name of an organisation because it has a typo."

Documentation:
"Organisations - Manager users can create, edit and delete organisations. All other users can view organisations and inspect their details."

Classification: Documentation Misunderstanding  
Reason: Developer users do not have permission to edit organisation details, so the user is misunderstanding their role.

---

Example 2  
Bug Report:
"I am a manager user and I cannot update the skill of a developer. I go to the developer's profile, click 'Edit', but the skill field is greyed out."

Documentation:
"Manager users can update the skills of developers by navigating to the developer's profile and clicking 'Edit'. Only Manager users can perform this action."

Classification: Bug  
Reason: The manager user should be able to edit skills, so this likely indicates a bug in the interface or permissions.

---

Now evaluate the following:

Bug Report:
"{bug_report}"

Documentation:
{doc_block}

Classification:"""


# Get response
response = qa_pipeline(prompt_template, max_new_tokens=200)
print(response[0]['generated_text'])
