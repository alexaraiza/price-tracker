from flask import Blueprint, flash, Markup, redirect, render_template, request, url_for
from flask_login import current_user, login_required

from datetime import datetime
import json

from price_tracker import db
from .forms import EditItemForm, NewItemForm
from price_tracker.models import Item, PriceResolutionError


items = Blueprint("items", __name__, url_prefix="/items")


@items.route("/new", methods=["GET", "POST"])
@login_required
def new_item():
    form = NewItemForm()

    if form.validate_on_submit():
        current_price = form.get_price(form.current_price)
        notification_choice = form.get_notification_choice()
        target_price = form.get_price(form.target_price)
        item = Item(name=form.name.data, url=form.url.data, current_price=current_price, currency=form.currency.data, notification_choice=notification_choice, target_price=target_price, user=current_user)
        if current_price:
            try:
                elements = item.get_elements()
            except ValueError:
                elements = []
                flash(Markup(f"Could not find the price of <span class='price'>{item.get_price_string(item.current_price)}</span>. <a href='{url_for('main.faq')}'>Why?</a>"), "warning")
            else:
                if not elements:
                    flash(f"Cannot track the price of {item.name}. Sorry about that!", "warning")
            item.elements = json.dumps(elements, separators=(',', ':'))
        db.session.add(item)
        db.session.commit()
        return redirect(url_for("main.index"))

    return render_template("items/new_item.html", title="New item", form=form)


@items.route("/<int:item_id>", methods=["GET", "POST", "DELETE"])
@login_required
def item(item_id):
    item = Item.query.get_or_404(item_id)
    if item.user != current_user:
        abort(404)

    if request.method == "DELETE":
        db.session.delete(item)
        db.session.commit()
        flash(f"{item.name} has been deleted", "success")
        return redirect(url_for("main.index"))

    form = EditItemForm()

    if form.validate_on_submit():
        item.name = form.name.data
        item.url = form.url.data
        item.current_price = form.get_price(form.current_price)
        item.currency = form.currency.data
        item.notification_choice = form.get_notification_choice()
        item.target_price = form.get_price(form.target_price)
        if item.current_price:
            try:
                elements = item.get_elements()
            except ValueError:
                elements = []
                flash(Markup(f"Could not find the price of <span class='price'>{item.get_price_string(item.current_price)}</span>. <a href='{url_for('main.faq')}'>Why?</a>"), "warning")
            else:
                if not elements:
                    flash(f"Cannot track the price of {item.name}. Sorry about that!", "warning")
            item.elements = json.dumps(elements, separators=(',', ':'))
        db.session.commit()
        flash(f"{item.name} has been updated", "success")
        return redirect(url_for("items.item", item_id=item_id))

    if request.method == "GET":
        form.name.data = item.name
        form.url.data = item.url
        if item.current_price:
            form.current_price.data = item.get_price_string(item.current_price, False)
        form.currency.data = item.currency
        if item.notification_choice != -1:
            form.notify_user.data = True
            form.notification_choice.data = form.notification_choice.choices[item.notification_choice]
        if item.target_price:
            form.target_price.data = item.get_price_string(item.target_price, False)
    return render_template("items/item.html", title=item.name, form=form, item=item)


@items.route("/<int:item_id>/price", methods=["POST"])
@login_required
def price(item_id):
    item = Item.query.get_or_404(item_id)
    if item.user != current_user:
        abort(404)
    try:
        price = item.get_price()
    except PriceResolutionError:
        flash(f"Could not get the price of {item.name}. Sorry about that!", "warning")
    else:
        if price:
            item.current_price = price
            item.last_update_datetime = datetime.utcnow()
            item.add_to_price_history(price)
            db.session.commit()
        else:
            flash(f"Could not get the price of {item.name}. Sorry about that!", "warning")
    return redirect(url_for("items.item", item_id=item_id))


@items.route("/<int:item_id>/delete", methods=["POST"])
@login_required
def delete_item(item_id):
    item = Item.query.get_or_404(item_id)
    if item.user != current_user:
        abort(404)
    db.session.delete(item)
    db.session.commit()
    flash(f"{item.name} has been deleted", "success")
    return redirect(url_for("main.index"))