from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required
from app.models import db, ApplicationRole, ApplicationPage, ApplicationRule
from app.forms import ApplicationRuleForm
from app.utils import roles_required

runbook = Blueprint("runbook", __name__)

# Redirect 403 (permission) errors to 403.html
@runbook.errorhandler(403)
def forbidden(e):
    return render_template("403.html"), 403

@runbook.route("/documentation", methods=["GET", "POST"])
@login_required
@roles_required("Developer")
def documentation():
    form = ApplicationRuleForm()
    form.page.query = ApplicationPage.query.order_by(ApplicationPage.name)
    form.roles.query = ApplicationRole.query.order_by(ApplicationRole.name)

    # Get tab (default = 'roles)
    tab = request.args.get("tab", "roles") 

    return render_template(
        "documentation.html",
        application_roles=ApplicationRole.query.order_by(ApplicationRole.name).all(),
        application_pages=ApplicationPage.query.order_by(ApplicationPage.name).all(),
        application_rules=ApplicationRule.query.order_by(ApplicationRule.title).all(),
        form=form,
        tab=tab
    )

# ----- Role routes -----
@runbook.route("/add-role", methods=["POST"])
def add_application_role():
    role_name = request.form.get("role_name")
    if role_name:
        exists = ApplicationRole.query.filter_by(name=role_name).first()
        if not exists:
            db.session.add(ApplicationRole(name=role_name))
            db.session.commit()
            flash(f"Role '{role_name}' added.", "success")
    return redirect(url_for("runbook.documentation", tab="roles"))

@runbook.route("/update-application-role/<int:application_role_id>", methods=["POST"])
@login_required
@roles_required("Developer")
def update_application_role(application_role_id):
    new_name = request.form.get("new_name")

    role = ApplicationRole.query.get_or_404(application_role_id)

    if new_name and new_name != role.name:
        exists = ApplicationRole.query.filter_by(name=new_name).first()
        if exists:
            flash("A role with that name already exists.", "warning")
        else:
            role.name = new_name
            db.session.commit()
            flash("Role updated successfully.", "success")

    return redirect(url_for("runbook.documentation", tab="roles"))

@runbook.route("/delete-application-role/<int:application_role_id>", methods=["POST"])
def delete_application_role(application_role_id):
    role = ApplicationRole.query.get_or_404(application_role_id)
    db.session.delete(role)
    db.session.commit()
    flash(f"Role '{role.name}' deleted.", "success")
    return redirect(url_for("runbook.documentation", tab="roles"))

# ----- Page routes -----
@runbook.route("/add-page", methods=["POST"])
def add_application_page():
    page_name = request.form.get("page_name")
    if page_name:
        exists = ApplicationPage.query.filter_by(name=page_name).first()
        if not exists:
            db.session.add(ApplicationPage(name=page_name))
            db.session.commit()
            flash(f"Page '{page_name}' added.", "success")
    return redirect(url_for("runbook.documentation", tab="pages"))

@runbook.route("/update-application-page/<int:application_page_id>", methods=["POST"])
@login_required
@roles_required("Developer")
def update_application_page(application_page_id):
    new_name = request.form.get("new_name")

    page = ApplicationPage.query.get_or_404(application_page_id)

    if new_name and new_name != page.name:
        exists = ApplicationPage.query.filter_by(name=new_name).first()
        if exists:
            flash("A page with that name already exists.", "warning")
        else:
            page.name = new_name
            db.session.commit()
            flash("Page updated successfully.", "success")

    return redirect(url_for("runbook.documentation", tab="pages"))

@runbook.route("/delete-application-page/<int:application_page_id>", methods=["POST"])
def delete_application_page(application_page_id):
    page = ApplicationPage.query.get_or_404(application_page_id)
    db.session.delete(page)
    db.session.commit()
    flash(f"Page '{page.name}' deleted.", "success")
    return redirect(url_for("runbook.documentation", tab="pages"))

# ----- Rule routes -----
@runbook.route("/add-rule", methods=["POST"])
@login_required
@roles_required("Developer")
def add_application_rule():
    form = ApplicationRuleForm()
    
    if form.validate_on_submit():
        # Check for at least one rule
        if not form.roles.data or len(form.roles.data) == 0:
            flash("At least one application role must be selected.", "danger")
            return redirect(url_for("runbook.documentation", tab="rules"))

        existing = ApplicationRule.query.filter_by(title=form.title.data).first()

        if not existing:
            # Create new rule
            new_rule = ApplicationRule(
                title=form.title.data,
                description=form.description.data,
                page=form.page.data
            )
            
            # Add selected roles to the rule
            for role in form.roles.data:
                new_rule.roles.append(role)
                
            db.session.add(new_rule)
            db.session.commit()
            flash(f"Rule '{form.title.data}' added to runbook.", "success")
        else:
            flash(f"Cannot add '{form.title.data}', the rule already exists.", "warning")
    else:
        for field, errors in form.errors.items():
            for error in errors:
                flash(f"{getattr(form, field).label.text}: {error}", "danger")
                
    return redirect(url_for("runbook.documentation", tab="rules"))

@runbook.route("/update-application-rule/<int:application_rule_id>", methods=["POST"])
@login_required
@roles_required("Developer")
def update_application_rule(application_rule_id):
    rule = ApplicationRule.query.get_or_404(application_rule_id)

    new_title = request.form.get("title").strip()
    new_description = request.form.get("description").strip()
    new_page_id = request.form.get("page")
    new_roles = request.form.getlist("roles")

    # Validate updated inputs 
    if not new_title or len(new_title) < 10:
        flash("Title must be at least 10 characters.", "danger")
    elif not new_description or len(new_description) < 50:
        flash("Description must be at least 50 characters.", "danger")
    elif not new_page_id:
        flash("A page is required.", "danger")
    elif not new_roles:
        flash("At least one role is required.", "danger")
    else:
        existing = ApplicationRule.query.filter(ApplicationRule.title == new_title, ApplicationRule.id != rule.id).first()
        if existing:
            flash("A rule with that title already exists.", "danger")
        else:
            # Update rule
            rule.title = new_title
            rule.description = new_description
            rule.page = ApplicationPage.query.get(new_page_id)
            rule.roles = ApplicationRole.query.filter(ApplicationRole.id.in_(new_roles)).all()
            db.session.commit()
            flash("Rule updated successfully.", "success")

    return redirect(url_for("runbook.documentation", tab="rules"))
