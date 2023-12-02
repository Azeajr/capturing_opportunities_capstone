import structlog
from flask_wtf import FlaskForm
from wtforms import MultipleFileField, SubmitField
from wtforms.validators import DataRequired

log = structlog.get_logger()


class TrainingImagesForm(FlaskForm):
    training_images = MultipleFileField(
        "Upload Training Images", validators=[DataRequired()]
    )
    training_submit = SubmitField("Upload")


class CollectionImagesForm(FlaskForm):
    collection_images = MultipleFileField(
        "Upload Collection Images", validators=[DataRequired()]
    )
    collection_submit = SubmitField("Upload")
