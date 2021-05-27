from flask import current_app, url_for
from flask_mail import Message

from itsdangerous import TimedJSONWebSignatureSerializer as Serializer

from price_tracker import mail


def send_reset_password_email(user):
    s = Serializer(current_app.config["SECRET_KEY"], 86400)
    token = s.dumps({"user_id": user.id}).decode("utf-8")
    msg = Message("Reset password", recipients=[user.email])
    msg.body = f"""We received a request to reset your password on price tracker.
To reset your password, visit the following URL within 24 hours:
{url_for("auth.reset_password", token=token, _external=True)}
If you don't want to change your password, ignore this email.
"""
    mail.send(msg)


def send_sign_up_warning_email(user):
    msg = Message("Sign up attempt", recipients=[user.email])
    msg.body = f"""Someone tried to sign up on price tracker using your email, but it's already tied to an existing account.
If you forgot your password, visit the following URL:
{url_for("auth.reset_password_request", _external=True)}
If this wasn't you, ignore this email.
"""
    mail.send(msg)


def send_verify_email(user):
    s = Serializer(current_app.config["SECRET_KEY"], 86400)
    token = s.dumps({"user_id": user.id}).decode("utf-8")
    msg = Message("Verify email", recipients=[user.email])
    msg.body = f"""Your email was used to sign up on price tracker.
If this was you, visit the following URL within 24 hours to verify your email:
{url_for("auth.verify_email", token=token, _external=True)}
If this wasn't you, ignore this email.
"""
    mail.send(msg)