from abc import ABC
from pathlib import Path


class MlABC(ABC):
    def __init__(self, session_id: str, model_path: Path = None):
        raise NotImplementedError

    def process_training_images(self, img_path):
        raise NotImplementedError

    def process_collection_images(self, img_path):
        raise NotImplementedError
