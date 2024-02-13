import shutil
from pathlib import Path

import structlog
from flask import (
    Blueprint,
    current_app,
    redirect,
    render_template,
    send_from_directory,
    url_for,
)
from werkzeug.utils import secure_filename

from cap_opp.forms.image_forms import CollectionImagesForm, TrainingImagesForm
from cap_opp.services.ml_service import MLService

log = structlog.get_logger()

main_bp = Blueprint("main", __name__, template_folder="templates")
# ml_service = MLService(augment=True, min_training_size=100)
ml_service = MLService(augment=False)


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

    processed_images = [
        p.name for p in current_app.config["PROCESSED_IMAGES_FOLDER"].glob("*")
    ]

    return render_template(
        "index.jinja2",
        training_images_form=training_images_form,
        collection_images_form=collection_images_form,
        training_images=training_images,
        image_collection=image_collection,
        processed_images=processed_images,
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

        ml_service.train_svm(
            ml_service.preprocess_and_extract_features(
                current_app.config["TRAINING_IMAGES_FOLDER"]
            )
        )
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

        for img_path, prediction, score, classification in ml_service.process_images(
            current_app.config["IMAGE_COLLECTION_FOLDER"]
        ):
            if classification == "inlier":
                shutil.copy(
                    img_path,
                    Path(current_app.config["PROCESSED_IMAGES_FOLDER"], img_path.name),
                )

                log.info(
                    f"IMAGE: {img_path}, PREDICTION: {prediction}, SCORE: {score}, CLASSIFICATION: {classification}"
                )

    return redirect(url_for("main.index"))


@main_bp.route("/uploaded/<folder>/<filename>")
def uploaded_file(folder, filename):
    return send_from_directory(current_app.config[folder.upper()], filename)
