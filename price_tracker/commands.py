from flask.cli import with_appcontext

import click
from datetime import datetime

from price_tracker import bcrypt, db
from price_tracker.models import User
from price_tracker.webpages import get_response_text


@click.command(name="create_demo_user")
@with_appcontext
def create_demo_user():
    """Create a demo user."""
    email = click.prompt("Email")
    if '@' not in email:
        email += "@pricetracker.ml"
    password = click.prompt("Password", hide_input=True, confirmation_prompt=True)
    password_hash = bcrypt.generate_password_hash(password).decode("utf-8")
    user = User(email=email, password_hash=password_hash, is_demo_user=True)
    db.session.add(user)
    db.session.commit()


@click.command(name="delete_user")
@click.argument("user_id")
@with_appcontext
def delete_user(user_id):
    """Delete a user."""
    user = User.query.get(user_id)
    if not user:
        raise click.ClickException("user does not exist")
    click.confirm(f"Are you sure you want to delete {user.email}?", abort=True)
    for item in user.items:
        db.session.delete(item)
    db.session.delete(user)
    db.session.commit()


@click.command(name="create_db")
@with_appcontext
def create_db():
    """Create all the database tables."""
    db.create_all()


@click.command(name="drop_db")
@click.confirmation_option(prompt="Are you sure you want to drop the database?")
@with_appcontext
def drop_db():
    """Drop all the database tables."""
    db.drop_all()


@click.command(name="update_prices")
@with_appcontext
def update_prices():
    """Update the price of every item."""
    users = User.query.all()
    for user in users:
        prices = user.get_all_prices()
        for i in range(len(prices)):
            if prices[i]:
                user.items[i].current_price = prices[i]
                user.items[i].last_update_datetime = datetime.utcnow()
                user.items[i].add_to_price_history(prices[i])
    db.session.commit()


@click.command(name="echo_response")
@click.option("-m", "--method", help="Use requests or selenium.", type=click.Choice(["requests", "selenium"]), default="requests")
@click.option("-s", "--start", help="Start index of string.", type=int)
@click.option("-e", "--end", help="End index of string.", type=int)
@click.argument("url")
@with_appcontext
def echo_response(method, start, end, url):
    """Echo the response."""
    click.echo(get_response_text(url, method)[start:end])