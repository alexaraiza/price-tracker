import os


class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY")
    SQLALCHEMY_DATABASE_URI = os.environ.get("SQLALCHEMY_DATABASE_URI")
    MAIL_SERVER = os.environ.get("MAIL_SERVER")
    MAIL_USERNAME = os.environ.get("MAIL_USERNAME")
    MAIL_PASSWORD = os.environ.get("MAIL_PASSWORD")
    MAIL_PORT = os.environ.get("MAIL_PORT")
    MAIL_USE_SSL = os.environ.get("MAIL_USE_SSL")
    MAIL_DEFAULT_SENDER = (os.environ.get("MAIL_DEFAULT_SENDER_NAME"), os.environ.get("MAIL_DEFAULT_SENDER_EMAIL"))
    USER_AGENT = os.environ.get("USER_AGENT")

class ProductionConfig(Config):
    ENV = "production"
    DEBUG = False

class DevelopmentConfig(Config):
    ENV = "development"
    DEBUG = True

class TestingConfig(DevelopmentConfig):
    TESTING = True
    WTF_CSRF_ENABLED = False