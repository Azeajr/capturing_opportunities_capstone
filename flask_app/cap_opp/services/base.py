from abc import ABC
from typing import Any


class MlABC(ABC):
    def process_training_images(self, img_path):
        raise NotImplementedError

    def process_collection_images(self, img_path):
        raise NotImplementedError
