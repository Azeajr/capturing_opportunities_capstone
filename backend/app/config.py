import enum
from pathlib import Path
from uuid import uuid4

from pydantic_settings import BaseSettings

pod_uuid = str(uuid4())


class Models(str, enum.Enum):
    SVM = "svm"
    AUTO_ENCODER = "auto_encoder"


class CommonSettings(BaseSettings):
    APP_NAME: str = "Capture Opportunities"
    ENV: str
    API_KEY: str = "api_secret_key"
    SESSIONS_FOLDER: Path = Path("temp", "sessions")
    MODEL: Models = Models.SVM
    LOG_LEVEL: str = "DEBUG"
    LOG_FILE: Path = Path("logs", pod_uuid, "app.jsonl")
    ANALYTICS_LOG_FILE: Path = Path("logs", pod_uuid, "analytics.jsonl")


class DevelopmentConfig(CommonSettings):
    DEBUG: bool = True
    API_KEY: str = "devsecret"


class TestingConfig(CommonSettings):
    TESTING: bool = True
    API_KEY: str = "testsecret"


class ProductionConfig(CommonSettings):
    API_KEY: str


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
