import enum
from pathlib import Path

from pydantic_settings import BaseSettings


class Models(str, enum.Enum):
    SVM = "svm"
    AUTO_ENCODER = "auto_encoder"


class CommonSettings(BaseSettings):
    APP_NAME: str = "Capture Opportunities"
    ENV: str
    SECRET_KEY: str = "mysecret"
    UPLOAD_FOLDER: Path = Path("temp", "uploads")
    TRAINING_IMAGES_FOLDER: Path = UPLOAD_FOLDER / "training_images" / "raw"
    IMAGE_COLLECTION_FOLDER: Path = UPLOAD_FOLDER / "image_collection"
    PROCESSED_IMAGES_FOLDER: Path = UPLOAD_FOLDER / "processed_images"
    MODEL: Models = Models.SVM


class DevelopmentConfig(CommonSettings):
    DEBUG: bool = True


class TestingConfig(CommonSettings):
    TESTING: bool = True


class ProductionConfig(CommonSettings):
    SECRET_KEY: str


def get_config():
    config = CommonSettings()
    match config.ENV:
        case "dev":
            return DevelopmentConfig()
        case "test":
            return TestingConfig()
        case "prod":
            return ProductionConfig()
        case _:
            raise ValueError(f"Invalid environment {config.ENV}.")
