from flask_wtf import FlaskForm

from wtforms.fields import BooleanField, PasswordField, SubmitField
from wtforms.fields.html5 import EmailField
from wtforms.validators import DataRequired, Email, EqualTo


class ChangePasswordForm(FlaskForm):
    current_password = PasswordField("Current password", validators=[DataRequired(message="Password required")])
    new_password = PasswordField("New password", validators=[DataRequired(message="Password required")])
    confirm_new_password = PasswordField("Confirm new password", validators=[DataRequired(message="Password required"), EqualTo("new_password")])
    submit = SubmitField("Change password")


class LoginForm(FlaskForm):
    email = EmailField("Email", validators=[DataRequired(message="Email required"), Email(message="Invalid email")])
    password = PasswordField("Password", validators=[DataRequired(message="Password required")])
    remember = BooleanField("Remember me")
    submit = SubmitField("Log in")


class ResetPasswordForm(FlaskForm):
    password = PasswordField("Password", validators=[DataRequired(message="Password required")])
    confirm_password = PasswordField("Confirm password", validators=[DataRequired(message="Password required"), EqualTo("password")])
    submit = SubmitField("Reset password")


class SendEmailForm(FlaskForm):
    email = EmailField("Email", validators=[DataRequired(message="Email required"), Email(message="Invalid email")])
    submit = SubmitField("Send email")


class SignupForm(FlaskForm):
    email = EmailField("Email", validators=[DataRequired(message="Email required"), Email(message="Invalid email")])
    password = PasswordField("Password", validators=[DataRequired(message="Password required")])
    confirm_password = PasswordField("Confirm password", validators=[DataRequired(message="Password required"), EqualTo("password")])
    submit = SubmitField("Sign up")