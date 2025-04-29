from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from app.models import FlikUser, FlikRole, Bug, db
from app.utils import roles_required, get_or_create_config, get_deleted_account
from datetime import datetime, timedelta, timezone

config = Blueprint("config", __name__)


# Redirect 403 (permission) errors to 403.html
@config.errorhandler(403)
def forbidden(e):
    return render_template("403.html"), 403


# Load configuration page
@config.route("/config", methods=["GET"])
@login_required
@roles_required("Manager")
def load_config():
    tab = request.args.get("tab", "columns")
    config = get_or_create_config()
    columns = config.columns_to_track.split(",") if config.columns_to_track else []

    # Fetch current date for database retention period
    cleardown_date = (datetime.now(timezone.utc) + timedelta(days=config.database_retention_period)).date()

    developers, clients = [], []

    # Pass existing roles to 'users' tab
    if tab == "users":
        developers = FlikUser.query.filter(
            FlikUser.role.has(FlikRole.name.in_(["Developer", "Manager"])),
            FlikUser.id != current_user.id
        ).all()
        clients = FlikUser.query.filter(
            FlikUser.role.has(name="Client"),
            FlikUser.id != current_user.id
        ).all()

    return render_template(
        "config.html",
        tab=tab,
        columns=columns,
        developers=developers,
        clients=clients,
        retention=config.database_retention_period,
        cleardown_date=cleardown_date
    )


# Define Azure DevOps columns to track
@config.route("/config/columns", methods=["POST"])
@login_required
@roles_required("Manager")
def add_column():
    config = get_or_create_config()
    new_col = request.form.get("column_name", "").strip()

    if new_col:
        existing_cols = (
            config.columns_to_track.split(",") if config.columns_to_track else []
        )
        if new_col not in existing_cols:
            existing_cols.append(new_col)
            config.columns_to_track = ",".join(existing_cols)
            db.session.commit()
            flash(f"{new_col} will now be tracked for workload.", "success")
        else:
            flash(f"{new_col} is already being tracked.", "info")

    return redirect(url_for("config.load_config", tab="columns"))


@config.route("/update-column/<string:column_name>", methods=["POST"])
@login_required
@roles_required("Manager")
def update_column(column_name):
    new_name = request.form.get("new_name", "").strip()
    config = get_or_create_config()

    existing_cols = (
        config.columns_to_track.split(",") if config.columns_to_track else []
    )
    if column_name in existing_cols and new_name and new_name not in existing_cols:
        updated_cols = [
            new_name if col == column_name else col for col in existing_cols
        ]
        config.columns_to_track = ",".join(updated_cols)
        db.session.commit()
        flash("Column updated successfully.", "success")
    else:
        flash("A column with that name already exists.", "warning")

    return redirect(url_for("config.load_config", tab="columns"))


@config.route("/delete-column/<string:column_name>", methods=["POST"])
@login_required
@roles_required("Manager")
def delete_column(column_name):
    config = get_or_create_config()
    existing_cols = (
        config.columns_to_track.split(",") if config.columns_to_track else []
    )

    if column_name in existing_cols:
        existing_cols.remove(column_name)
        config.columns_to_track = ",".join(existing_cols)
        db.session.commit()
        flash(f"Column '{column_name}' deleted.", "success")

    return redirect(url_for("config.load_config", tab="columns"))


# Update database retention period
@config.route("/config/database", methods=["POST"])
@login_required
@roles_required("Manager")
def update_retention():
    config = get_or_create_config()
    try:
        days = int(request.form.get("retention_days"))
        if days <= 0:
            raise ValueError("Retention period must be greater than 0 days.")
        config.database_retention_period = days
        db.session.commit()
        flash("Retention period updated.", "success")
    except (ValueError, TypeError):
        flash("Invalid input. Please enter a valid number.", "danger")

    return redirect(url_for("config.load_config", tab="database"))

@config.route("/run-database-cleardown", methods=["POST"])
@login_required
@roles_required("Manager")
def run_database_cleardown():
    from datetime import datetime, timedelta
    config = get_or_create_config()

    current_date = datetime.now(timezone.utc).date()  # Today
    cleardown_date = config.database_retention_period  # Days

    # Use scheduled date logic from load_config()
    date_set = current_date - timedelta(days=cleardown_date)

    # If today >= original_set_date + retention_days => delete
    if current_date >= date_set + timedelta(days=cleardown_date):
        deleted = Bug.query.delete()
        db.session.commit()
        flash(f"Bug tickets cleared. Only new bugs will be used for duplicate detection and insights.", "success")
    else:
        flash("Scheduled deletion date has not yet arrived.", "warning")

    return redirect(url_for("config.load_config", tab="database"))

@config.route("/delete-user/<int:user_id>", methods=["POST"])
@login_required
@roles_required("Manager")
def delete_user(user_id):
    user = FlikUser.query.get_or_404(user_id)
    deleted_account = get_deleted_account()
    
    if user.id == current_user.id:
        flash("You cannot delete your own account.", "danger")
    else:
        # Reassign all bugs where account is author or assignee
        Bug.query.filter_by(author=user.id).update({Bug.author: deleted_account.id})
        Bug.query.filter_by(assignee=user.id).update({Bug.assignee: deleted_account.id})

        # Delete account
        db.session.delete(user)
        db.session.commit()
        flash(f"User '{user.email}' deleted.", "success")
    
    return redirect(url_for("config.load_config", tab="users"))
