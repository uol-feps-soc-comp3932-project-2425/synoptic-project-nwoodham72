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
from bert.ticket_officer import find_similar_tickets
from .models import FlikUser, Skill, ApplicationRole, ApplicationPage, Bug, db
from .utils import roles_required, save_bug, get_or_create_config
import logging

main = Blueprint("main", __name__)


# Redirect 403 (permission) errors to 403.html
@main.errorhandler(403)
def forbidden(e):
    return render_template("403.html"), 403

@main.route("/", methods=["GET"])
def index():
    return redirect(url_for("main.raise_bug"))


# List user accounts for testing
@main.route("/users")
def list_users():
    users = FlikUser.query.all()
    return "<br>".join([f"{u.id} | {u.email} | {u.role}" for u in users])
@main.route("/bugs")
def list_bugs():
    bugs = Bug.query.all()
    return "<br>".join([
        f"{b.id} | {b.title} | {b.description} | {b.priority} | "
        f"Assignee: {b.assignee} | Author: {b.author} | "
        f"Page: {b.application_page} | Role: {b.application_role} | "
        f"Skills: {', '.join([s.name for s in b.skills]) if b.skills else 'None'}"
        for b in bugs
    ])


""" Flik Configuration"""


@main.route("/teamsheet", methods=["GET", "POST"])
@login_required
@roles_required("Developer", "Manager")
def teamsheet():

    user_roles = [r.name for r in current_user.roles]
    is_manager = "Manager" in user_roles

    # Update skills
    if request.method == "POST":
        user_id = int(request.form.get("user_id"))

        # Block developers updating other developer profiles
        if not is_manager and current_user.id != user_id:
            abort(403)

        selected_skills = request.form.getlist("skills")
        user = FlikUser.query.get(user_id)
        new_skills = Skill.query.filter(Skill.id.in_(selected_skills)).all()

        # Compare new and current skills
        if set(user.skills) != set(new_skills):
            user.skills = new_skills
            db.session.commit()
            flash("Your skills were successfully updated!", "success")
        else:
            flash("No changes made to your skills", "info")

        return redirect(url_for("main.teamsheet"))

    # Display developers
    developers = FlikUser.query.filter(FlikUser.role.in_(["Developer", "Manager"])).all()
    developers.sort(key=lambda d: d.id != current_user.id)  # Display current user first
    skills = Skill.query.order_by(Skill.name).all()
    return render_template("teamsheet.html", developers=developers, skills=skills, is_manager=is_manager)


""" Raise bug workflow """
@main.route("/raise_bug", methods=["GET", "POST"])
@login_required
def raise_bug():
    form = RaiseBugForm()
    bug_details = None
    additional_comments = None
    matching_docs = None
    tags = []
    author = FlikUser.query.get(current_user.id).email

    # Fetch database values and check for database entries
    application_roles = ApplicationRole.query.order_by(ApplicationRole.name).all()
    application_pages = ApplicationPage.query.order_by(ApplicationPage.name).all()

    if current_user.role == "Client":
        if not application_roles and not application_pages:
            flash(
                "No application roles or pages available. You will not be able to submit a ticket until the development team have added at least one user role and page.",
                "danger",
            )
        elif not application_roles:
            flash(
                "No application roles available. You will not be able to submit a ticket until the development team have added at least one user role.",
                "danger",
            )

        elif not application_pages:
            flash(
                "No application pages available. You will not be able to submit a ticket until the development team have added at least one page.",
                "danger",
            )

    # Developer view
    else:
        if not application_roles and not application_pages:
            flash(
                "No application roles or pages available. Please define an application page and role in the 'Documentation' tab. Users will not be able to submit tickets until this is done.",
                "danger",
            )
        elif not application_roles:
            flash(
                "No application roles available. Please define an application role in the 'Documentation' tab. Users will not be able to submit tickets until this is done.",
                "danger",
            )

        elif not application_pages:
            flash(
                "No application pages available. Please define an application page in the 'Documentation' tab. Users will not be able to submit tickets until this is done.",
                "danger",
            )

    if form.validate_on_submit():
        # Check for additional comments from documentation match modal
        additional_comments = request.form.get("additional_comments", "").strip()

        # Get form details
        bug_details = {
            "title": form.title.data,
            "role": form.role.data,
            "page": form.page.data,
            "description": form.description.data,
            "expected": form.expected.data,
        }

        # If no additional comments, check for documentation match
        if not additional_comments:
            # Generate documentation similarity
            action_comparison = bug_details["description"].strip() + "." + "\n" + bug_details["expected"].strip() + "."
            # Return matching documentation
            match, matching_docs = assess_documentation(
                action_comparison, bug_details["role"].name
            )
            # Display matching documentation
            if match and matching_docs:
                return render_template(
                    "raise_bug.html",
                    form=form,
                    bug_details=None,
                    matching_docs=matching_docs,
                )

        # Generate extractive summary of bug ticket
        prep_summary_data = (
            bug_details["description"].strip()
            + ".\n"
            + bug_details["expected"].strip()
            + ".\n"
        )

        # Prepare data for prioritiser and assigner
        prep_classification_data = (
            bug_details["title"].strip()
            + ".\n"
            + bug_details["description"].strip()
            + ".\n"
        )

        summary = extractive_summary(prep_summary_data)
        priority_label, priority_level = predict_priority(prep_classification_data, use_thresholding = True)

        # Send ticket to Azure in html format
        description = (
            f"<p><b>Summary</b>: As a <i>{bug_details['role'].name}</i> on the <i>{bug_details['page'].name}</i> page, {summary}<br>"
            f"<b>Priority</b>: {priority_label}</p>"
            f"<b>Author</b>: <i>{author}</i></p>"
            f"<hr>"
            f"<p><b>Background</b><br> <ul><li><i>User Role</i>: {bug_details['role'].name}</li><li><i>Application Page</i>: {bug_details['page'].name}</li></ul><p>"
            f"<p><b>Problem Description</b><br>{bug_details['description']}</p>"
            f"<p><b>Expected Behaviour</b><br>{bug_details['expected']}</p>"
        )

        # Append additional comments from documentation match modal
        if additional_comments:
            description += (
                f"<hr><p><b>Documentation Misalignment</b><br>"
                f"This bug flagged a documentation issue. The author overrided the flag and provided additional comments:<br><i>{additional_comments}</i></p>"
            )
        
        # Extract labels and assign developer
        assigned_to, extracted_tags = assign_developer(
            prep_classification_data,
            ORGANISATION,
            PROJECT_NAME,
            RETRIEVAL_ACCESS_TOKEN,
        )

        # Fetch related tickets
        related_match, related_tickets = find_similar_tickets(bug_details["description"], extracted_tags)
        if related_match and related_tickets:
            description += "<hr><p><b>Potential Duplicate Tickets</b><br>The following tickets may provide some insight to resolving this issue.<ul>"
            for ticket in related_tickets:
                description += f"<li>#{ticket['id']} – {ticket['title']}</li>"
            description += "</ul></p>"

        # Add 'Flik' tag to tags 
        tags = ["Flik"] + (extracted_tags if extracted_tags else [])

        # No tags extracted from ticket 
        if len(tags) == 1:
            tags.append("Miscellaneous")

        if additional_comments:
            tags.append("Documentation Misalignment")

        tags = [t.strip() for t in tags if t.strip()]  # Remove empty tags
        structured_tags = ", ".join(tags)

        try:
            work_item = create_work_item(
                PROJECT_NAME,
                bug_details["title"],
                description,
                priority_level,
                assigned_to,
                structured_tags,
            )

            # Successful output
            if additional_comments:  # Success message on documentation override
                flash(  # Bug Logo: Bootstrap 5.2 images (https://icons.getbootstrap.com/)
                    """
                    <div class='text-center'>
                        <img src='/static/images/bug.png' alt='Bug Logo' class='img-fluid mb-2' style='max-width: 50px;'>
                        <h5 class='alert-heading'>It's a bug!</h5>
                        <p>
                        Your bug has been sent to the development team to be resolved. The development team have been flagged of the documentation issues and will investigate this further.
                        Please note that the development team may reach out to you for further details if required.
                        </p>
                    </div>
                    """,
                    "success",
                )
            # Standard success message
            else:
                flash(  # Bug Logo: Bootstrap 5.2 images (https://icons.getbootstrap.com/)
                    """
                    <div class='text-center'>
                        <img src='/static/images/bug.png' alt='Bug Logo' class='img-fluid mb-2' style='max-width: 50px;'> 
                        <h5 class='alert-heading'>It's a bug!</h5>
                        <p>
                        Your bug has been sent to the development team to be resolved. Thank you for taking the time to report this bug through Flik.
                        Please note that the development team may reach out to you for further details if required.
                        </p>
                    </div>
                    """,
                    "success",
                )

            # Commit bug to database 
            bug = save_bug(
                title=bug_details["title"],
                description=bug_details["description"],
                priority=priority_label,
                role_id=bug_details["role"].id,
                page_id=bug_details["page"].id,
                assignee_id=assigned_to,  # or None if unassigned
                author_id=current_user.id,
                skill_ids=[Skill.query.filter_by(name=tag).first().id for tag in extracted_tags if Skill.query.filter_by(name=tag).first()] if extracted_tags else None
            )

            logging.info(f"Bug {bug.id} saved to database.") 

            # Clear form after successful send
            form.title.data = ""
            form.role.data = None
            form.page.data = None
            form.description.data = ""
            form.expected.data = ""

        except Exception as e:
            flash(f"Failed to create ticket: {e}", "danger")

    return render_template("raise_bug.html", form=form, bug_details=bug_details)
