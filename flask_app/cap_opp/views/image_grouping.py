from flask import Blueprint, current_app, redirect, render_template, request, url_for

image_grouping_bp = Blueprint("image_grouping", __name__, template_folder="templates")


@image_grouping_bp.route("/image-grouping", methods=["GET"])
def image_grouping():
    # Process the uploaded images and store their filenames in 'processed_images'
    processed_images = [
        p.name for p in current_app.config["UPLOAD_FOLDER"].glob("*.png")
    ]
    # for image in processed_images:
    #     log.info('processing image', image=image)

    return render_template("processed_images.html", processed_images=processed_images)
