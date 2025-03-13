from flask import Blueprint, render_template, redirect, url_for, flash
from .forms import RaiseBugForm
from azure_integration.client import create_work_item
from azure_integration.config import PROJECT_NAME
from bert.summariser import extractive_summary
from bert.prioritiser import predict_priority
from bert.assigner import assign_developer

main = Blueprint("main", __name__)

@main.route("/", methods=["GET"])
def index():
    return redirect(url_for("main.raise_bug"))

@main.route("/raise_bug", methods=["GET", "POST"])
def raise_bug():
    form = RaiseBugForm()
    bug_details = None  # 1. Define up front

    if form.validate_on_submit():
        # 2. Populate it after successful validation
        bug_details = {
            'title': form.title.data,
            'given': form.given.data,
            'when': form.when.data,
            'then': form.then.data,
            'expected': form.expected.data,
            'actual': form.actual.data
        }

        # Generate extractive summary of bug ticket
        prep_summary_data = (
            bug_details['title'].strip() + ".\n" +  # Add full stops to end of each step
            bug_details['given'].strip() + ".\n" +  
            bug_details['when'].strip() + ".\n" +
            bug_details['then'].strip() + ".\n" +      
            bug_details['expected'].strip() + ".\n" +
            bug_details['actual'].strip() + ".\n"
        )

        summary = extractive_summary(prep_summary_data)
        priority_label, priority_level = predict_priority(prep_summary_data)

        # Send ticket to Azure in HTML format
        description = (
            f"Summary:<br>{summary}<br><br>"
            f"Priority: {priority_label}<br><br>"
            f"Actual Behaviour:<br>{bug_details['actual']}<br><br>"
            f"Expected Behaviour:<br>{bug_details['expected']}<br><br>"
            f"Steps to Reproduce:<br>"
            f"Given: {bug_details['given']}<br>"
            f"When: {bug_details['when']}<br>"
            f"Then: {bug_details['then']}<br><br>"
        )

        developers = {
            "nathanmw72@gmail.com": {"front-end", "user accounts", "organisations"},
            "sc21nw@leeds.ac.uk": {"back-end", "team members", "team member's skills"}
        }

        assignee = assign_developer(developers, prep_summary_data)
        tags = "bug, report"

        try:
            work_item = create_work_item(
                PROJECT_NAME,
                bug_details['title'],
                description,
                priority_level,
                assignee,
                tags
            )
            flash(f"Ticket created with ID: {work_item.id}", "success")

            # Optionally clear form after success
            form.title.data = ''
            form.given.data = ''
            form.when.data = ''
            form.then.data = ''
            form.expected.data = ''
            form.actual.data = ''

        except Exception as e:
            flash(f"Failed to create ticket: {e}", "danger")

        # If you want to stay on the same page (and show bug_details), DON'T redirect
        # If you do redirect, you'll lose bug_details unless you store it in session or flash
        # return redirect(url_for("main.raise_bug"))

    # 3. Now bug_details is either None or a dict, but it always exists
    return render_template("raise_bug.html", form=form, bug_details=bug_details)


