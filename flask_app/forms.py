from flask_wtf import FlaskForm
from wtforms import MultipleFileField, SubmitField
from wtforms.validators import DataRequired

import structlog

log = structlog.get_logger()


# class TrainingImagesForm(FlaskForm):
#     images = MultipleFileField("Upload Training Images", validators=[DataRequired()])
#     submit1 = SubmitField("Upload")

# class ImageCollectionForm(FlaskForm):
#     images = MultipleFileField("Upload Image Collection", validators=[DataRequired()])
#     submit2 = SubmitField("Upload")
class ImageForm(FlaskForm):
    images = MultipleFileField(validators=[DataRequired()])
    submit = SubmitField("Upload")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.images.label = kwargs.get("label", "Upload Images")