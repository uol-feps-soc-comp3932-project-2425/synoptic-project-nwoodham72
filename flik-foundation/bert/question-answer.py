from transformers import pipeline

# Load model
qa = pipeline("question-answering", model="distilbert-base-cased-distilled-squad")

# Replace these with dynamic input from your app
context ="""
In the Student Portal, there are 2 user roles: lecturers and students.
Lecturers can upload lecture materials.
Students and lecturers can both read lecture materials.
"""
bug_report = """
I am a student user and I want to upload a lecture to the portal but I cannot. Why is this?"
"""

# context = "Albert Einstein was a theoretical physicist who developed the theory of relativity."
# bug_report = "Who developed the theory of relativity?"

# Use the QA model
qa_response = qa(question=bug_report, context=context)

# Extract model outputs
answer = qa_response['answer'].strip().lower()
score = qa_response['score']

# Log for transparency
print(f"🤖 Answer: {answer}")
print(f"📈 Confidence: {score:.2f}")

if score > 0.4 and answer not in ["", "i don't know", "unknown", "not applicable"]:
    print("ℹ️ This is likely a documentation misunderstanding.")
    print(f"🔍 Model Answer: {qa_response['answer']}")
    print("📘 Please refer to the documentation.")
else:
    print("🐞 Bug report flagged for the development team.")
    print(f"📝 Report: {bug_report}")
