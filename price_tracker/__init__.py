from flask import Flask
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_mail import Mail
from flask_sqlalchemy import SQLAlchemy


db = SQLAlchemy()
bcrypt = Bcrypt()
login_manager = LoginManager()
login_manager.login_view = "auth.login"
login_manager.login_message_category = "info"
mail = Mail()


def create_app(config):
    app = Flask(__name__)
    app.config.from_object(config)

    db.init_app(app)
    bcrypt.init_app(app)
    login_manager.init_app(app)
    mail.init_app(app)

    from price_tracker.auth import auth
    from price_tracker.items import items
    from price_tracker.main import main

    app.register_blueprint(auth)
    app.register_blueprint(items)
    app.register_blueprint(main)

    from price_tracker import commands
    app.cli.add_command(commands.create_demo_user)
    app.cli.add_command(commands.delete_user)
    app.cli.add_command(commands.create_db)
    app.cli.add_command(commands.drop_db)
    app.cli.add_command(commands.update_prices)
    app.cli.add_command(commands.echo_response)

    return app