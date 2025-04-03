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
from .models import FlikUser, Skill, db
from .utils import roles_required

main = Blueprint("main", __name__)

# Redirect 40e (permission) erros to 403.html
@main.errorhandler(403)
def forbidden(e):
    return render_template("403.html"), 403


# @main.route("/dashboard")
# @login_required
# def dashboard():
#     if current_user.role == "Manager":
#         return render_template("manager_dashboard.html")
#     elif current_user.role == "Developer":
#         return render_template("developer_dashboard.html")
#     elif current_user.role == "Client":
#         return render_template("client_dashboard.html")
#     else:
#         flash("Unauthorised access", "danger")
#         return redirect(url_for("main.index"))


@main.route("/", methods=["GET"])
def index():
    return redirect(url_for("main.raise_bug"))


# List user accounts for testing
@main.route("/users")
def list_users():
    users = FlikUser.query.all()
    return "<br>".join([f"{u.id} | {u.email} | {u.role}" for u in users])


# Developer teamsheet
@main.route("/teamsheet", methods=["GET", "POST"])
@login_required
@roles_required("Developer")
def teamsheet():
    # Update skills
    if request.method == "POST":
        user_id = int(request.form.get("user_id"))

        # Block updating other developer's profiles
        if current_user.id != user_id:
            abort(403)

        selected_skills = request.form.getlist("skills")
        user = FlikUser.query.get(user_id)
        user.skills = Skill.query.filter(Skill.id.in_(selected_skills)).all()
        db.session.commit()
        flash("Your skills were successfully updated!", "success")

        return redirect(url_for("main.teamsheet"))

    developers = FlikUser.query.filter_by(role="Developer").all()
    # Put current user profile at the top 
    developers.sort(key=lambda d: d.id != current_user.id)
    skills = Skill.query.order_by(Skill.name).all()
    return render_template("teamsheet.html", developers=developers, skills=skills)


@main.route("/raise_bug", methods=["GET", "POST"])
@login_required
def raise_bug():
    form = RaiseBugForm()
    bug_details = None
    additional_comments = None
    matching_docs = None
    tags = []

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

        # Check for additioal comments
        if not additional_comments:
            # Generate documentation similarity
            prep_documentation_comparison = (
                "I am a "
                + bug_details["role"].strip()
                + "user on the "
                + bug_details["page"].strip()
                + "page.\n"
                + bug_details["description"].strip()
                + ".\n"
                # + bug_details["expected"].strip()  # Include in comparison?
                # + ".\n"
            )
            # Return matching documentation
            match, matching_docs = assess_documentation(
                prep_documentation_comparison, bug_details["role"].strip()
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
            bug_details["title"].strip()
            + ".\n"  # Add full stops to end of each step
            + f"I am a "
            + bug_details["role"].strip()
            + "user.\n"
            + f"I am on the "
            + bug_details["page"].strip()
            + "page.\n"
            + bug_details["description"].strip()
            + ".\n"
            + bug_details["expected"].strip()
            + ".\n"
        )

        summary = extractive_summary(prep_summary_data)
        priority_label, priority_level = predict_priority(prep_summary_data)

        # Send ticket to Azure in HTML format
        description = (
            f"Summary:<br>{summary}<br><br>"
            f"Priority: {priority_label}<br><br>"
            f"--Steps to Reproduce--<br>"
            f"Background:<br>I am a {bug_details['role']} user on the {bug_details['page']} page.<br><br>"
            f"Problem Description:<br>{bug_details['description']}<br><br>"
            f"Expected Behaviour:<br>{bug_details['expected']}<br><br>"
        )

        # Append additional comments on documentation match modal
        if additional_comments:
            description += f"This bug flagged a documentation issue. The author provided additional comments:<br>{additional_comments}<br><br>"

        assigned_to, tags = assign_developer(
            prep_summary_data,
            ORGANISATION,
            PROJECT_NAME,
            RETRIEVAL_ACCESS_TOKEN,
        )
        if additional_comments:
            tags.append("Documentation Misalignment")
        structured_tags = ", ".join(tags) if tags else "Miscellaneous"

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
                flash(
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
                # Bug Logo: Bootstrap 5.2 images (https://icons.getbootstrap.com/)
                flash(
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

            # Clear form after successful send
            form.title.data = ""
            form.role.data = ""
            form.page.data = ""
            form.description.data = ""
            form.expected.data = ""

        except Exception as e:
            flash(f"Failed to create ticket: {e}", "danger")

    return render_template("raise_bug.html", form=form, bug_details=bug_details)
