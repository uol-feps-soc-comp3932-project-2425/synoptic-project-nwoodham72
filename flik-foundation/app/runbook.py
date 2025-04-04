from flask import Blueprint, render_template, redirect, url_for, flash, request, abort
from flask_login import login_required, current_user
from .models import FlikUser, Skill, ApplicationRole, ApplicationPage, db
from .utils import roles_required

runbook = Blueprint("runbook", __name__)

# Redirect 403 (permission) errors to 403.html
@runbook.errorhandler(403)
def forbidden(e):
    return render_template("403.html"), 403


""" Page Overview """
@runbook.route("/documentation", methods=["GET", "POST"])
@login_required
@roles_required("Developer")
def documentation():
    application_roles = ApplicationRole.query.order_by(ApplicationRole.name).all()
    if not application_roles:
        flash("You must define at least one role before users can submit bug reports.", "warning")
    
    application_pages = ApplicationPage.query.order_by(ApplicationPage.name).all()
    if not application_pages:
        flash("You must define at least one page before users can submit bug reports.", "warning")

    return render_template("documentation.html", application_roles=application_roles, application_pages=application_pages)

@runbook.route("/add-role", methods=["POST"])
@login_required
@roles_required("Developer")
def add_application_role():
    app_role_name = request.form.get("role_name")
    if app_role_name:
        existing = ApplicationRole.query.filter_by(name=app_role_name).first()
        if not existing:
            db.session.add(ApplicationRole(name=app_role_name))
            db.session.commit()
            flash(f"'{app_role_name}' added to available roles", "success")
        else:
            flash(f"Cannot add '{app_role_name}', the role already exists.", "warning")
    return redirect(url_for("runbook.documentation"))


""" Application Role Management """


@runbook.route("/update-role/<int:application_role_id>", methods=["POST"])
@login_required
@roles_required("Developer")
def update_application_role(application_role_id):
    new_name = request.form.get("new_name")
    app_role = ApplicationRole.query.get_or_404(application_role_id)

    if new_name and new_name != app_role.name:
        existing = ApplicationRole.query.filter_by(name=new_name).first()
        if existing:
            flash(f"{new_name} already exists.", "warning")
        else:
            app_role.name = new_name
            db.session.commit()
            flash("Role updated successfully.", "success")

    return redirect(url_for("runbook.documentation"))

@runbook.route("/delete-role/<int:application_role_id>", methods=["POST"])
@login_required
@roles_required("Developer")
def delete_application_role(application_role_id):
    app_role = ApplicationRole.query.get_or_404(application_role_id)
    db.session.delete(app_role)
    db.session.commit()
    flash(f"Role '{app_role.name}' deleted.", "success")
    return redirect(url_for("runbook.documentation"))

""" Application Page Management """

@runbook.route("/add-page", methods=["POST"])
@login_required
@roles_required("Developer")
def add_application_page():
    page_name = request.form.get("page_name")
    if page_name:
        existing = ApplicationPage.query.filter_by(name=page_name).first()
        if not existing:
            db.session.add(ApplicationPage(name=page_name))
            db.session.commit()
            flash(f"Page '{page_name}' added successfully.", "success")
        else:
            flash(f"Page '{page_name}' already exists.", "warning")
    return redirect(url_for("runbook.documentation"))