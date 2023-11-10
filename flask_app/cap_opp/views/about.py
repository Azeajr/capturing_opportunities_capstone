from flask import Blueprint, render_template

about_bp = Blueprint("about", __name__, template_folder="templates")


@about_bp.route("/about")
def index():
    return render_template("about.html")