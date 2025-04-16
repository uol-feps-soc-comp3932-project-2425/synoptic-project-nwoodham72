from functools import wraps
from flask import abort
from flask_login import current_user
from flask import Blueprint, render_template, redirect, url_for, flash, request, abort
from flask_login import login_required, current_user
from .forms import RaiseBugForm
from azure_integration.client import create_work_item
from azure_integration.config import (
    PROJECT_NAME,
    ORGANISATION_URL,
    ORGANISATION,
    PERSONAL_ACCESS_TOKEN,
    RETRIEVAL_ACCESS_TOKEN,
)
from bert.summariser import extractive_summary
from bert.prioritiser import predict_priority
from bert.assigner import assign_developer
from bert.assessor import assess_documentation
from .models import FlikUser, Skill, ApplicationRole, Bug, db
import json

""" utils.py: Helper functions and decorators """

# Save new bug to database for ticket_officer
def save_bug(title, description, priority, role_id, page_id, assignee_id, author_id, skill_ids=None):
    new_bug = Bug(
        title=title,
        description=description,
        priority=priority,
        application_role=role_id,
        application_page=page_id,
        assignee=assignee_id,
        author=author_id,
    )

    if skill_ids:
        skills = Skill.query.filter(Skill.id.in_(skill_ids)).all()
        new_bug.skills = skills
    
    db.session.add(new_bug)
    db.session.commit()

    return new_bug

# Restrict user roles to a route
def roles_required(*role_names):
    def decorator(f):
        @wraps(f)
        def wrapped(*args, **kwargs):
            if not current_user.is_authenticated:
                abort(403)
            user_roles = {role.name for role in current_user.roles}
            if not any(role in user_roles for role in role_names):
                abort(403)
            return f(*args, **kwargs)
        return wrapped
    return decorator

# Run raise_bug without Flask for testing
def create_ticket_scheduled(bug):
    summary_input = (
        f"{bug['title']}.\n"
        f"I am a {bug['role']} user.\n"
        f"I am on the {bug['page']} page.\n"
        f"{bug['description']}.\n"
        f"{bug['expected']}.\n"
    )

    # Prepare the same comparison string as used in Flask route
    prep_documentation_comparison = (
        "I am a "
        + bug["role"].strip()
        + " user on the "
        + bug["page"].strip()
        + " page.\n"
        + bug["description"].strip()
        + ".\n"
    )

    match_found, _ = assess_documentation(prep_documentation_comparison, bug["role"].strip())

    summary = extractive_summary(summary_input)
    priority_label, priority_level = predict_priority(summary_input)
    priority_level = int(priority_level)
    assignee, tags = assign_developer(summary_input, ORGANISATION, PROJECT_NAME, RETRIEVAL_ACCESS_TOKEN)

    doc_tag = "Matches Documentation" if match_found else "Documentation Misalignment"
    tags.append(doc_tag)

    structured_tags = ", ".join(tags)
    description = (
        f"Summary:<br>{summary}<br><br>"
        f"Priority: {priority_label}<br><br>"
        f"--Steps to Reproduce--<br>"
        f"Background:<br>I am a {bug['role']} user on the {bug['page']} page.<br><br>"
        f"Problem Description:<br>{bug['description']}<br><br>"
        f"Expected Behaviour:<br>{bug['expected']}<br><br>"
    )

    work_item = create_work_item(
        PROJECT_NAME,
        bug["title"],
        description,
        priority_level,
        assignee,
        structured_tags,
    )

    return {"status": "success", "azure_id": int(work_item.id)}
