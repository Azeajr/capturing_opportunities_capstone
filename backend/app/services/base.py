from abc import ABC
from pathlib import Path


class MlABC(ABC):
    def __init__(self, session_id: str, is_training: bool = True):
        raise NotImplementedError

    async def process_training_images(self, img_path):
        raise NotImplementedError

    async def process_collection_images(self, img_path):
        raise NotImplementedError
