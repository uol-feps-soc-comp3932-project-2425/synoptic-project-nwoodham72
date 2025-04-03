from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from .models import FlikUser
from .forms import LoginForm, RegisterForm
from . import db

auth = Blueprint("auth", __name__)

@auth.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("main.index"))

    form = LoginForm()
    if form.validate_on_submit():
        user = FlikUser.query.filter_by(email=form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user)
            flash("Login successful!", "info")
            return redirect(url_for("main.index"))
        else:
            flash("Login failed. Check your credentials.", "danger")

    return render_template("login.html", form=form)

@auth.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("auth.login"))

@auth.route("/register", methods=["GET", "POST"])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        user = FlikUser(email=form.email.data, role=form.role.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        # flash("Account created! You can now log in.", "info")
        return redirect(url_for("auth.login"))

    return render_template("register.html", form=form)
