from pathlib import Path
from typing import Any, Iterator

import structlog
from flask import (
    Blueprint,
    current_app,
    redirect,
    render_template,
    send_from_directory,
    url_for,
    session,
    jsonify,
)
from werkzeug.utils import secure_filename

from cap_opp.forms.image_forms import CollectionImagesForm, TrainingImagesForm
from cap_opp.services.base import MlABC
from cap_opp.services.svm import SVM
from cap_opp.services.auto_encoder import AutoEncoder
from cap_opp.config import get_config


settings = get_config()

log = structlog.get_logger()

main_bp = Blueprint("main", __name__, template_folder="templates")

if settings.MODEL == "svm":
    ml_service: MlABC = SVM(augment=False)
elif settings.MODEL == "auto_encoder":
    ml_service: MlABC = AutoEncoder(augment=False)


@main_bp.route("/", methods=["GET", "POST"])
def index():
    training_images_form = TrainingImagesForm()
    collection_images_form = CollectionImagesForm()

    training_images = [
        p.name for p in current_app.config["TRAINING_IMAGES_FOLDER"].glob("*")
    ]
    image_collection = [
        p.name for p in current_app.config["IMAGE_COLLECTION_FOLDER"].glob("*")
    ]

    scored_paths = session.pop("scored_paths", [])
    log.info("scored_paths", scored_paths=scored_paths)


    return render_template(
        "index.jinja2",
        training_images_form=training_images_form,
        collection_images_form=collection_images_form,
        training_images=training_images,
        image_collection=image_collection,
        processed_images=scored_paths,
    )


@main_bp.route("/upload/training_images", methods=["POST"])
def upload_training_images():
    training_images_form = TrainingImagesForm()
    log.info("upload_training_images")

    if training_images_form.validate_on_submit():
        for image in training_images_form.training_images.data:
            image_path = Path(
                current_app.config["TRAINING_IMAGES_FOLDER"],
                secure_filename(image.filename),
            )
            image.save(image_path)

        ml_service.process_training_images(current_app.config["TRAINING_IMAGES_FOLDER"])

    return redirect(url_for("main.index"))


@main_bp.route("/upload/collection_images", methods=["POST"])
def upload_collection_images():
    collection_images_form = CollectionImagesForm()

    if collection_images_form.validate_on_submit():
        for image in collection_images_form.collection_images.data:
            image_path = Path(
                current_app.config["IMAGE_COLLECTION_FOLDER"],
                secure_filename(image.filename),
            )
            image.save(image_path)

        scored_paths: Iterator[tuple[str, Any]] = ml_service.process_collection_images(
            current_app.config["IMAGE_COLLECTION_FOLDER"]
        )

        log.info("scored_paths_from_model", scored_paths=scored_paths)

        scored_paths = list(scored_paths)
        scored_paths.sort(key=lambda x: x[1], reverse=True)
        scored_paths = [p for p, _ in scored_paths]

        session["scored_paths"] = jsonify(scored_paths).json

    return redirect(url_for("main.index", scored_paths=scored_paths))


@main_bp.route("/uploaded/<folder>/<filename>")
def uploaded_file(folder, filename):
    return send_from_directory(current_app.config[folder.upper()], filename)
