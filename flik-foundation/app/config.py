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

