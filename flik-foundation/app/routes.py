from flask import Blueprint, render_template, redirect, url_for, flash
from .forms import RaiseBugForm
from azure_integration.client import create_work_item
from azure_integration.config import PROJECT_NAME

main = Blueprint("main", __name__)

@main.route("/", methods=["GET"])
def index():
    return redirect(url_for("main.raise_bug"))

# @main.route("/raise_bug", methods=["GET", "POST"])
# def raise_bug():
#     form = RaiseBugForm()
#     bug_details = None

#     if form.validate_on_submit():
#         # Capture submitted details
#         bug_details = {
#             'title': form.title.data,
#             'given': form.given.data,
#             'when': form.when.data,
#             'then': form.then.data,
#             'expected': form.expected.data,
#             'actual': form.actual.data
#         }

#         # Clear form after submission (optional)
#         form.title.data = ''
#         form.given.data = ''
#         form.when.data = '' 
#         form.then.data = ''
#         form.expected.data = ''
#         form.actual.data = ''

#     return render_template("raise_bug.html", form=form, bug_details=bug_details)

@main.route("/raise_bug", methods=["GET", "POST"])
def raise_bug():
    form = RaiseBugForm()
    if form.validate_on_submit():
        # Extract form data
        title = form.title.data
        given = form.given.data
        when = form.when.data
        then = form.then.data
        expected = form.expected.data
        actual = form.actual.data

        # Build a description string from the collected inputs
        description = (
            f"Actual Behaviour:\n{actual}\n\n"
            f"Steps to Reproduce:\nGiven: {given}\nWhen: {when}\nThen: {then}\n\n"
            f"Expected Behaviour:\n{expected}"
        )

        # Set additional parameters (you might let these come from the form too)
        priority = 4  # For example, a default priority
        assignee = "nathanmw72@gmail.com"  # Example: a default assignee
        tags = "bug, report"  # Example: default tags

        try:
            # Call the Azure DevOps function to create the work item
            work_item = create_work_item(PROJECT_NAME, title, description, priority, assignee, tags)
            flash(f"Ticket created with ID: {work_item.id}", "success")
        except Exception as e:
            flash(f"Failed to create ticket: {e}", "danger")

        return redirect(url_for("main.raise_bug"))
    
    return render_template("raise_bug.html", form=form)

