# application/auth.py

from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user

from application import db
from application.forms import RegistrationForm, LoginForm
from application.crud import create_user, get_user_by_email

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("main.hdb_predict"))

    form = RegistrationForm()
    if form.validate_on_submit():
        existing = get_user_by_email(form.email.data.lower())
        if existing:
            flash("An account with this email already exists.", "danger")
            return redirect(url_for("auth.register"))

        user = create_user(
            username=form.username.data.strip(),
            email=form.email.data.lower().strip(),
            password=form.password.data,
        )
        login_user(user)
        flash("Account created and you are now logged in.", "success")
        return redirect(url_for("main.hdb_predict"))

    return render_template("auth/register.html", form=form)


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    # Always create the form first so POST can be processed
    form = LoginForm()

    # If user is already logged in and is just visiting /login via GET,
    # send them to the predictor. But on POST we still validate the password
    # so tests like "wrong password should fail" behave correctly.
    if current_user.is_authenticated and request.method == "GET":
        return redirect(url_for("main.hdb_predict"))

    if form.validate_on_submit():
        user = get_user_by_email(form.email.data.lower())
        if user is None or not user.check_password(form.password.data):
            flash("Invalid email or password.", "danger")
            return redirect(url_for("auth.login"))

        login_user(user)
        flash("Logged in successfully.", "success")

        next_page = request.args.get("next")
        return redirect(next_page or url_for("main.hdb_predict"))

    return render_template("auth/login.html", form=form)


@auth_bp.route("/logout")
@login_required
def logout():
    logout_user()
    flash("You have been logged out.", "info")
    return redirect(url_for("auth.login"))
