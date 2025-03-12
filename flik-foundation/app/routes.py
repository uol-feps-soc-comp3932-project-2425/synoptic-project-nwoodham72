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
            'given': form.given.data,
            'when': form.when.data,
            'then': form.then.data,
            'expected': form.expected.data,
            'actual': form.actual.data
        }

        # Clear form after submission (optional)
        form.title.data = ''
        form.given.data = ''
        form.when.data = '' 
        form.then.data = ''
        form.expected.data = ''
        form.actual.data = ''

    return render_template("raise_bug.html", form=form, bug_details=bug_details)
