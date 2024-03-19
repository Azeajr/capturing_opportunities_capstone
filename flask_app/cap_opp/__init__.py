from flask import Flask
from flask.cli import with_appcontext
from flask_cors import CORS
import click

from cap_opp.config import get_config


from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass


db = SQLAlchemy(model_class=Base)


def create_app():
    # create and configure the app
    app = Flask(__name__)
    CORS(app)
    config = get_config()
    app.config.update(config.model_dump())
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///example.db"
    app.config["TRAINING_IMAGES_FOLDER"].mkdir(parents=True, exist_ok=True)
    app.config["IMAGE_COLLECTION_FOLDER"].mkdir(parents=True, exist_ok=True)
    app.config["PROCESSED_IMAGES_FOLDER"].mkdir(parents=True, exist_ok=True)
    for file in app.config["TRAINING_IMAGES_FOLDER"].glob("*"):
        file.unlink(missing_ok=True)

    for file in app.config["IMAGE_COLLECTION_FOLDER"].glob("*"):
        file.unlink(missing_ok=True)

    db.init_app(app)

    app.cli.add_command(init_db_command)

    from cap_opp.views.about import about_bp
    from cap_opp.views.main import main_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(about_bp)

    return app


def init_db():
    db.drop_all()
    db.create_all()


@click.command("init-db")
@with_appcontext
def init_db_command():
    """Clear existing data and create new tables."""
    init_db()
    click.echo("Initialized the database.")
