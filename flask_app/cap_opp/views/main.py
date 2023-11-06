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

from cap_opp.forms.image_forms import ImageForm

log = structlog.get_logger()

main_bp = Blueprint("main", __name__, template_folder="templates")


@main_bp.route("/", methods=["GET", "POST"])
def index():
    log.info("index", root_path=current_app.root_path)
    log.info(
        "training images folder", folder=current_app.config["TRAINING_IMAGES_FOLDER"]
    )
    log.info("current_path", current_path=Path.cwd())
    training_images_form = ImageForm(csrf_enabled=False, label="Upload Training Images")
    image_collection_form = ImageForm(
        csrf_enabled=False, label="Upload Image Collection"
    )

    training_images = [
        p.name for p in current_app.config["TRAINING_IMAGES_FOLDER"].glob("*.png")
    ]
    image_collection = [
        p.name for p in current_app.config["IMAGE_COLLECTION_FOLDER"].glob("*.png")
    ]

    processed_images = []

    return render_template(
        "index.html",
        training_images_form=training_images_form,
        image_collection_form=image_collection_form,
        training_images=training_images,
        image_collection=image_collection,
        processed_images=processed_images,
    )


@main_bp.route("/upload/training_images", methods=["POST"])
def upload_training_images():
    training_images_form = ImageForm(csrf_enabled=False, label="Upload Training Images")
    image_collection_form = ImageForm(
        csrf_enabled=False, label="Upload Image Collection"
    )

    if training_images_form.validate_on_submit():
        for image in training_images_form.images.data:
            image_path = Path(
                current_app.config["TRAINING_IMAGES_FOLDER"],
                secure_filename(image.filename),
            )
            log.info("image_path", image_path=image_path)
            image_path.parent.mkdir(parents=True, exist_ok=True)
            image.save(image_path)
            log.info("training image file uploaded", file_path=image_path)
        # training_images_form.images.data = []
        # training_images = [
        #     p.name for p in app.config["TRAINING_IMAGES_FOLDER"].glob("*.jpg")
        # ]
    # return render_template(
    #     "index.html",
    #     training_images_form=training_images_form,
    #     image_collection_form=image_collection_form,
    # )
    return redirect(url_for("main.index"))


@main_bp.route("/upload/collection_images", methods=["POST"])
def upload_collection_images():
    training_images_form = ImageForm(csrf_enabled=False, label="Upload Training Images")
    image_collection_form = ImageForm(
        csrf_enabled=False, label="Upload Image Collection"
    )

    if image_collection_form.validate_on_submit():
        for image in image_collection_form.images.data:
            image_path = Path(
                current_app.config["IMAGE_COLLECTION_FOLDER"],
                secure_filename(image.filename),
            )
            image.save(image_path)
            log.info("image collection file uploaded", file_path=image_path)
        # image_collection_form.images.data = []
        # image_collection = [
        #     p.name for p in app.config["IMAGE_COLLECTION_FOLDER"].glob("*.jpg")
        # ]
    # return render_template(
    #     "index.html",
    #     training_images_form=training_images_form,
    #     image_collection_form=image_collection_form,
    # )
    return redirect(url_for("main.index"))


@main_bp.route("/uploaded/<folder>/<filename>")
def uploaded_file(folder, filename):
    log.info(
        "uploaded file",
        folder=folder,
        filename=filename,
        path=current_app.config[folder.upper()],
    )
    return send_from_directory(current_app.config[folder.upper()], filename)
