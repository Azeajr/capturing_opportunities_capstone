from pathlib import Path

import structlog
from flask import (
    Flask,
    render_template,
    request,
    send_from_directory,
    redirect,
    url_for,
)
from werkzeug.utils import secure_filename

from forms import ImageForm

log = structlog.get_logger()

UPLOAD_FOLDER = Path("temp", "uploads")
TRAINING_IMAGES_FOLDER = Path(UPLOAD_FOLDER, "training_images")
IMAGE_COLLECTION_FOLDER = Path(UPLOAD_FOLDER, "image_collection")
UPLOAD_FOLDER.mkdir(parents=True, exist_ok=True)
TRAINING_IMAGES_FOLDER.mkdir(parents=True, exist_ok=True)
IMAGE_COLLECTION_FOLDER.mkdir(parents=True, exist_ok=True)
ALLOWED_EXTENSIONS = {"jpg", "jpeg", "png" }

app = Flask(__name__)
app.config["SECRET_KEY"] = "mysecret"
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.config["TRAINING_IMAGES_FOLDER"] = TRAINING_IMAGES_FOLDER
app.config["IMAGE_COLLECTION_FOLDER"] = IMAGE_COLLECTION_FOLDER


@app.route("/", methods=["GET", "POST"])
def index():
    training_images_form = ImageForm(csrf_enabled=False, label="Upload Training Images")
    image_collection_form = ImageForm(csrf_enabled=False, label="Upload Image Collection")
    
    training_images = [
        p.name for p in app.config["TRAINING_IMAGES_FOLDER"].glob("*.png")
    ]
    image_collection = [
        p.name for p in app.config["IMAGE_COLLECTION_FOLDER"].glob("*.png")
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


@app.route("/about")
def about():
    return render_template("about.html")


@app.route("/upload/training_images", methods=["POST"])
def upload_training_images():
    training_images_form = ImageForm(csrf_enabled=False, label="Upload Training Images")
    image_collection_form = ImageForm(csrf_enabled=False, label="Upload Image Collection")

    if training_images_form.validate_on_submit():
        for image in training_images_form.images.data:
            image_path = Path(
                app.config["TRAINING_IMAGES_FOLDER"], secure_filename(image.filename)
            )
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
    return redirect(url_for("index"))


@app.route("/upload/collection_images", methods=["POST"])
def upload_collection_images():
    training_images_form = ImageForm(csrf_enabled=False, label="Upload Training Images")
    image_collection_form = ImageForm(csrf_enabled=False, label="Upload Image Collection")

    if image_collection_form.validate_on_submit():
        for image in image_collection_form.images.data:
            image_path = Path(
                app.config["IMAGE_COLLECTION_FOLDER"], secure_filename(image.filename)
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
    return redirect(url_for("index"))



@app.route("/uploaded/<folder>/<filename>")
def uploaded_file(folder, filename):
    return send_from_directory(app.config[folder.upper()], filename)

processed_images = ["image1.jpg", "image2.jpg"]  # Replace with your actual filenames


@app.route("/image-grouping", methods=["GET"])
def image_grouping():
    # Process the uploaded images and store their filenames in 'processed_images'
    processed_images = [p.name for p in UPLOAD_FOLDER.glob("*.png")]
    # for image in processed_images:
    #     log.info('processing image', image=image)

    return render_template("processed_images.html", processed_images=processed_images)


if __name__ == "__main__":
    app.run()
