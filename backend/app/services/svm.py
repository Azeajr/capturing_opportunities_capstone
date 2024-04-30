import pickle
from pathlib import Path
from uuid import uuid4

import numpy as np
import structlog
import tensorflow as tf
from sklearn.metrics import make_scorer
from sklearn.model_selection import GridSearchCV
from sklearn.svm import OneClassSVM

from app.config import get_config
from app.services.base import MlABC

# log = structlog.get_logger()

# Minimum number of training images required to train the SVM
min_training_size = 100
config = get_config()


class SVM(MlABC):
    def __init__(self, session_id: str, is_training: bool = True):
        self.logger = structlog.get_logger()
        self.session_id = session_id
        # Load MobileNetV3 pre-trained on ImageNet without the top layer
        self.model = tf.keras.applications.MobileNetV3Large(
            weights="imagenet", include_top=False
        )

        if is_training:
            self.best_svm = None
        else:
            with open(
                config.SESSIONS_FOLDER / session_id / "svm" / "svm.pkl", "rb"
            ) as f:
                self.best_svm = pickle.load(f)

    async def process_training_images(self, img_path):
        self.logger.info("Processing Training Images", img_path=img_path)

        img_dir_size = len(list(img_path.glob("*")))
        factor = (
            (max(min_training_size, 100) + img_dir_size - 1) // img_dir_size
            if img_dir_size > 0
            else 0
        )
        img_list = []

        data_augmentation = tf.keras.preprocessing.image.ImageDataGenerator(
            rotation_range=20,
            width_shift_range=0.2,
            height_shift_range=0.2,
            shear_range=0.2,
            zoom_range=0.2,
            horizontal_flip=True,
            fill_mode="nearest",
        )

        for path in img_path.glob("*"):
            try:
                # Load image and preprocess it for MobileNetV3
                img = tf.keras.preprocessing.image.load_img(
                    path, target_size=(224, 224)
                )
                img_array = tf.keras.preprocessing.image.img_to_array(img)
                img_array = tf.keras.applications.mobilenet_v3.preprocess_input(
                    img_array
                )

                # Apply data augmentation if needed
                for _ in range(factor - 1):
                    img_list.append(data_augmentation.random_transform(img_array))
                img_list.append(img_array)
            except Exception as e:
                print(f"Error processing image {path}: {e}")

        if not img_list:
            return None

        self.logger.info("Length of training images", length=len(img_list))
        # Ensure that img_batch has a batch dimension
        img_batch = np.stack(img_list, axis=0)

        # Extract features using MobileNetV3
        features = self.model.predict(img_batch)
        features = features.reshape((features.shape[0], -1))  # Flatten the features

        svm = OneClassSVM()
        anomaly_scorer = make_scorer(
            lambda estimator, X: -estimator.decision_function(X).ravel()
        )
        clf = GridSearchCV(
            svm,
            {
                "nu": [0.01, 0.05, 0.1, 0.5],
                "gamma": ["scale", "auto"],
                "kernel": ["rbf"],
            },
            scoring=anomaly_scorer,
            cv=5,
            n_jobs=-1,
        )
        clf.fit(features)
        self.best_svm = clf.best_estimator_

        # Save the best SVM model
        path = config.SESSIONS_FOLDER / self.session_id / "svm"
        path.mkdir(parents=True, exist_ok=True)

        with open(path / "svm.pkl", "wb") as f:
            pickle.dump(self.best_svm, f)

        self.logger.info(
            "process_training_images",
            session_id=self.session_id,
            model_name="svm",
            augmented_image_count=len(img_list),
            analytics=True,
        )

        return Path("/", self.session_id) / "svm" / "svm.pkl"

    async def process_collection_images(self, img_path):
        # Convert single image path to a directory-like object for compatibility
        self.logger.info("Processing Collection Images", img_path=img_path)

        if not self.best_svm:
            raise ValueError("SVM model not loaded")

        img_paths: list[Path] = []
        img_list = []
        for path in img_path.glob("*"):
            try:
                # Load image and preprocess it for MobileNetV3
                img = tf.keras.preprocessing.image.load_img(
                    path, target_size=(224, 224)
                )
                img_array = tf.keras.preprocessing.image.img_to_array(img)
                img_array = tf.keras.applications.mobilenet_v3.preprocess_input(
                    img_array
                )

                img_paths.append(path)
                img_list.append(img_array)
            except Exception as e:
                print(f"Error processing image {path}: {e}")

        # Ensure that img_batch has a batch dimension
        img_batch = np.stack(img_list, axis=0) if img_list else np.array([])
        self.logger.info("Length of collection images", length=len(img_list))

        # Extract features using MobileNetV3
        features = self.model.predict(img_batch)
        features = features.reshape((features.shape[0], -1))  # Flatten the features

        # img_paths, new_features = self.extract_features(img_dir)
        scores = self.best_svm.decision_function(features)

        img_paths = [p.name for p in img_paths]

        self.logger.info(
            "Paths and Scores",
            paths=img_paths,
            scores=scores.tolist(),
        )

        self.logger.info(
            "processed_collection_images",
            session_id=self.session_id,
            model_name="svm",
            image_count=len(img_paths),
            analytics=True,
        )

        return zip(img_paths, scores.tolist())
