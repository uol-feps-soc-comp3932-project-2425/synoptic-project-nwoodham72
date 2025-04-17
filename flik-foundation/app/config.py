from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required
from app.models import db 
from app.utils import roles_required, get_or_create_config

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
    return render_template("config.html", tab=tab, columns=columns, retention=config.database_retention_period)

# Define Azure DevOps columns to track
@config.route("/config/columns", methods=["POST"])
@login_required
@roles_required("Manager")
def add_column():
    config = get_or_create_config()
    new_col = request.form.get("column_name", "").strip()

    if new_col:
        existing_cols = config.columns_to_track.split(",") if config.columns_to_track else []
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

    existing_cols = config.columns_to_track.split(",") if config.columns_to_track else []
    if column_name in existing_cols and new_name and new_name not in existing_cols:
        updated_cols = [new_name if col == column_name else col for col in existing_cols]
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
    existing_cols = config.columns_to_track.split(",") if config.columns_to_track else []

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
        config.database_retention_period = days
        db.session.commit()
        flash("Retention period updated.", "success")
    except (ValueError, TypeError):
        flash("Invalid input. Please enter a valid number.", "danger")

    return redirect(url_for("config.load_config", tab="database"))

