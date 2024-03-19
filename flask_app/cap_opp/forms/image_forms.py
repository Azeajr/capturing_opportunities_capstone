import structlog
from flask_wtf import FlaskForm
from flask_wtf.file import FileRequired, MultipleFileField

log = structlog.get_logger()


class TrainingImagesForm(FlaskForm):
    training_images = MultipleFileField(
        "Upload Training Images", validators=[FileRequired()]
    )
    class Meta:
        csrf = False


class CollectionImagesForm(FlaskForm):
    collection_images = MultipleFileField(
        "Upload Collection Images", validators=[FileRequired()]
    )
    class Meta:
        csrf = False
