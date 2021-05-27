from flask import Blueprint, flash, redirect, render_template, url_for
from flask_login import current_user, login_required

from price_tracker import bcrypt, db
from price_tracker.auth.forms import ChangePasswordForm, LoginForm


main = Blueprint("main", __name__)


@main.route("/")
def index():
    if current_user.is_authenticated:
        items = current_user.items
        return render_template("main/index.html", items=items)
    form = LoginForm()
    return render_template("landing.html", form=form)


@main.route("/account", methods=["GET", "POST"])
@login_required
def account():
    form = ChangePasswordForm()
    if form.validate_on_submit():
        if current_user.is_demo_user:
            flash("Demo users cannot change their password", "warning")
            return redirect(url_for("main.account"))
        if bcrypt.check_password_hash(current_user.password_hash, form.current_password.data):
            password_hash = bcrypt.generate_password_hash(form.new_password.data).decode("utf-8")
            current_user.password_hash = password_hash
            db.session.commit()
            flash("Your password has been changed", "success")
            return redirect(url_for("main.account"))
        flash("Incorrect password", "warning")
    return render_template("main/account.html", title="Account", form=form)


@main.route("/faq")
def faq():
    return render_template("main/faq.html", title="FAQ")