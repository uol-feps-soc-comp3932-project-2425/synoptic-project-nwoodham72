from flask import Blueprint, render_template, redirect, url_for
from .forms import RaiseBugForm

main = Blueprint("main", __name__)

@main.route("/", methods=["GET"])
def index():
    return redirect(url_for("main.raise_bug"))

@main.route("/raise_bug", methods=["GET", "POST"])
def raise_bug():
    form = RaiseBugForm()
    bug_details = None

    if form.validate_on_submit():
        # Capture submitted details
        bug_details = {
            'title': form.title.data,
            'description': form.description.data
        }

        # Clear form after submission (optional)
        form.title.data = ''
        form.description.data = ''

    return render_template("raise_bug.html", form=form, bug_details=bug_details)
