"""Main Flask app configuration file.

Creates a new instance of our Flask app with plugins, blueprints, views, and configuration loaded.
"""
import logging
import os

import stripe
from flask import jsonify
from flask_crud import CRUD
from flask_migrate import Migrate, MigrateCommand

from .api import api
from .commands import init_cli
from .db import db
from .flask import App
from .secret import update_app_config, db_secret_to_url, get_secret
from aws_xray_sdk.core import patcher, xray_recorder
from aws_xray_sdk.ext.flask.middleware import XRayMiddleware
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_script import Manager
from nplusone.ext.flask_sqlalchemy import NPlusOne

log = logging.getLogger(__name__)


def create_app(test_config=None) -> App:
    app = App("supbackend")

    # load config
    configure(app=app, test_config=test_config)

    # extensions
    CORS(app)
    configure_database(app)
    api.init_app(app)  # flask-smorest
    NPlusOne(app)
    CRUD(app)

    # CLI
    manager = Manager(app)
    manager.add_command("db", MigrateCommand)  # migrations under "flask db"
    init_cli(app, manager)

    init_xray(app)
    init_auth(app)

    stripe.api_key = app.config["STRIPE_KEY_SECRET"]

    return app


def init_auth(app):
    jwt = JWTManager(app)

    @jwt.user_loader_callback_loader
    def user_loader_callback(identity):
        from supbackend.model.user import User

        if identity is None:
            return None
        user = User.query.get(identity)
        return user

    @jwt.user_loader_error_loader
    def custom_user_loader_error(identity):
        ret = {"msg": "User {} not found".format(identity)}
        return jsonify(ret), 404

    @jwt.user_identity_loader
    def user_identity_lookup(user):
        assert user.id
        return user.id


def configure_database(app):
    """Set up flask with SQLAlchemy."""
    # configure options for create_engine
    engine_opts = app.config.get("SQLALCHEMY_ENGINE_OPTIONS", {})
    app.config["SQLALCHEMY_ENGINE_OPTIONS"] = engine_opts

    db.init_app(app)  # init sqlalchemy
    app.migrate = Migrate(app, db)  # alembic

    @app.teardown_appcontext
    def shutdown_session(exception=None):
        """Close session after request.

        Ensures no open transactions remain.
        """
        db.session.remove()

    test_db(app)


def configure_class(app):
    config_class = os.getenv("supbackend_CONFIG".upper())

    if not config_class:
        # figure out which config to load
        # get stage name
        stage = os.getenv("STAGE")
        if stage:
            # running in AWS or sls wsgi serve
            if stage == "prd":
                config_class = "supbackend.config.ProductionConfig"
            else:
                config_class = "supbackend.config.QAConfig"
        else:
            # local dev
            config_class = "supbackend.config.LocalDevConfig"

    app.config.from_object(config_class)


def configure_secrets(app: App) -> None:
    if app.config.get("LOAD_RDS_SECRETS"):
        # fetch db config secrets from Secrets Manager
        secret_name = app.config["RDS_SECRETS_NAME"]
        assert secret_name, "RDS_SECRETS_NAME missing"
        rds_secrets = get_secret(secret_name=secret_name)
        # construct database connection string from secret
        app.config["SQLALCHEMY_DATABASE_URI"] = db_secret_to_url(rds_secrets)

    if app.config.get("LOAD_APP_SECRETS"):
        # fetch app config secrets from Secrets Manager
        secret_name = app.config["APP_SECRETS_NAME"]
        update_app_config(app, secret_name)


def configure_instance(app):
    # load 'instance.cfg'
    # if it exists as our local instance configuration override
    app.config.from_pyfile("instance.cfg", silent=True)


def configure(app: App, test_config=None) -> None:
    configure_class(app)
    config = app.config
    if test_config:
        config.update(test_config)
    else:
        configure_secrets(app)
        configure_instance(app)

    if config.get("SQLALCHEMY_ECHO"):
        logging.basicConfig()
        logging.getLogger("sqlalchemy.engine").setLevel(logging.INFO)

    from .config import check_valid

    if not check_valid(config):
        raise Exception("Configuration is not valid.")


def init_xray(app: App):
    if not app.config.get("XRAY"):
        return
    patcher.patch(("requests", "boto3"))  # xray tracing for external requests
    xray_recorder.configure(service="supbackend")
    XRayMiddleware(app, xray_recorder)


def test_db(app: App) -> None:
    # verify DB works
    try:
        with app.app_context():
            db.session.execute("SELECT 1").scalar()
    except Exception as ex:
        log.error(
            f"Database configuration is invalid. Using URI: {app.config['SQLALCHEMY_DATABASE_URI']}"
        )
        raise ex
