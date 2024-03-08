from flask import Flask

from cap_opp.config import get_config
from cap_opp.views.about import about_bp
from cap_opp.views.main import main_bp


def create_app():
    # create and configure the app
    app = Flask(__name__)
    config = get_config()
    app.config.update(config.model_dump())
    app.config["TRAINING_IMAGES_FOLDER"].mkdir(parents=True, exist_ok=True)
    app.config["IMAGE_COLLECTION_FOLDER"].mkdir(parents=True, exist_ok=True)
    app.config["PROCESSED_IMAGES_FOLDER"].mkdir(parents=True, exist_ok=True)
    for file in app.config["TRAINING_IMAGES_FOLDER"].glob("*"):
        file.unlink(missing_ok=True)

    for file in app.config["IMAGE_COLLECTION_FOLDER"].glob("*"):
        file.unlink(missing_ok=True)

    app.register_blueprint(main_bp)
    app.register_blueprint(about_bp)

    return app
