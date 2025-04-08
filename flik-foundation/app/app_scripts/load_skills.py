import json
from app import create_app, db
from app.models import Skill
import os

""" load_skills.py: Scripts to insert the 338 bug_themes to 'Skill' table """

app = create_app()
app.app_context().push()

path = os.path.join(os.path.dirname(__file__), "bug_themes.json")

with open(path) as f:
    themes = json.load(f)

# Ensure no duplicates
existing = {s.name for s in Skill.query.all()}
new_skills = [Skill(name=label) for label in themes if label not in existing]

db.session.add_all(new_skills)
db.session.commit()
print(f"✅ Added {len(new_skills)} new skills.")
