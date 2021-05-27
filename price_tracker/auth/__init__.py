from flask import Blueprint, current_app, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_user, logout_user

from itsdangerous import TimedJSONWebSignatureSerializer as Serializer

from price_tracker import bcrypt, db
from . import mail
from .forms import LoginForm, ResetPasswordForm, SendEmailForm, SignupForm
from price_tracker.models import User


auth = Blueprint("auth", __name__)


@auth.route("/signup", methods=["GET", "POST"])
def signup():
    if current_user.is_authenticated:
        return redirect(url_for("main.index"))
    form = SignupForm()
    if form.validate_on_submit():
        email = form.email.data
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            if not existing_user.is_demo_user:
                mail.send_sign_up_warning_email(existing_user)
        else:
            password_hash = bcrypt.generate_password_hash(form.password.data).decode("utf-8")
            user = User(email=email, password_hash=password_hash, is_demo_user=False)
            db.session.add(user)
            db.session.commit()
            mail.send_verify_email(user)
        flash(f"An email has been sent to {email}", "info")
        return redirect(url_for("auth.login"))
    return render_template("auth/signup.html", title="Sign up", form=form)


@auth.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("main.index"))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password_hash, form.password.data) and (user.is_email_verified or user.is_demo_user):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get("next")
            return redirect(next_page) if next_page else redirect(url_for("main.index"))
        flash("Incorrect email/password combination or unverified email", "warning")
    return render_template("auth/login.html", title="Log in", form=form)


@auth.route("/logout")
def logout():
    logout_user()
    return redirect(url_for("main.index"))


@auth.route("/verify-email/<token>")
def verify_email(token):
    if current_user.is_authenticated:
        return redirect(url_for("main.index"))
    s = Serializer(current_app.config["SECRET_KEY"])
    try:
        user_id = s.loads(token)["user_id"]
    except:
        flash("Invalid or expired token", "warning")
        return redirect(url_for("auth.signup"))
    user = User.query.get(user_id)
    if not user or user.is_demo_user:
        flash("Invalid or expired token", "warning")
        return redirect(url_for("auth.signup"))
    user.is_email_verified = True
    db.session.commit()
    flash("Email verified. You can now log in.", "success")
    return redirect(url_for("auth.login"))


@auth.route("/reset-password", methods=["GET", "POST"])
def reset_password_request():
    if current_user.is_authenticated:
        return redirect(url_for("main.index"))
    form = SendEmailForm()
    if form.validate_on_submit():
        email = form.email.data
        user = User.query.filter_by(email=email).first()
        if user and not user.is_demo_user:
            mail.send_reset_password_email(user)
        flash(f"An email has been sent to {email}", "info")
        return redirect(url_for("auth.login"))
    return render_template("auth/send_email.html", title="Reset password", form=form)


@auth.route("/reset-password/<token>", methods=["GET", "POST"])
def reset_password(token):
    if current_user.is_authenticated:
        return redirect(url_for("main.index"))
    s = Serializer(current_app.config["SECRET_KEY"])
    try:
        user_id = s.loads(token)["user_id"]
    except:
        flash("Invalid or expired token", "warning")
        return redirect(url_for("auth.reset_password_request"))
    user = User.query.get(user_id)
    if not user or user.is_demo_user:
        flash("Invalid or expired token", "warning")
        return redirect(url_for("auth.reset_password_request"))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        password_hash = bcrypt.generate_password_hash(form.password.data).decode("utf-8")
        user.password_hash = password_hash
        db.session.commit()
        flash("Your password has been changed", "success")
        return redirect(url_for("auth.login"))
    return render_template("auth/reset_password.html", title="Reset password", form=form)