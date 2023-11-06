from pathlib import Path

from flask import Flask

from cap_opp.config import get_config
from cap_opp.views.about import about_bp
from cap_opp.views.main import main_bp


def create_app():
    # create and configure the app
    app = Flask(__name__)
    config = get_config()
    app.config.update(config.model_dump())

    app.register_blueprint(main_bp)
    app.register_blueprint(about_bp)

    return app
