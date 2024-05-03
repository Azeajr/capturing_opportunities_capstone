import math
import pickle
from pathlib import Path

import keras
import numpy as np
import structlog
import tensorflow as tf
from sklearn.metrics import make_scorer
from sklearn.model_selection import GridSearchCV
from sklearn.svm import OneClassSVM

from app.config import get_config
from app.services.base import MlABC

# Retrieve application configuration
config = get_config()

# Define target image size and batch processing parameters
TARGET_SIZE = (224, 224)
BATCH_SIZE = 32
DESIRED_TRAIN_SIZE = 300


class SVM(MlABC):
    def __init__(self, session_id: str, is_training: bool = True):
        # Initialize logging
        self.logger = structlog.get_logger()
        self.session_id = session_id
        # Load MobileNetV3 pre-trained on ImageNet without the top layer for feature extraction
        self.model = keras.applications.MobileNetV3Large(
            weights="imagenet", include_top=False
        )

        # Load previously trained SVM model if not in training mode
        if is_training:
            self.best_svm = None
        else:
            with open(
                config.SESSIONS_FOLDER / session_id / "svm" / "svm.pkl", "rb"
            ) as f:
                self.best_svm = pickle.load(f)

    async def process_training_images(self, img_path):
        # Log the start of the image processing
        self.logger.info("Processing Training Images", img_path=img_path)

        # Create a dataset from the directory containing training images
        train_ds = keras.preprocessing.image_dataset_from_directory(
            img_path,
            labels=None,
            image_size=TARGET_SIZE,
            batch_size=BATCH_SIZE,
        )

        # Determine the number of times the dataset needs to be augmented to reach the desired size
        img_count = len(train_ds.file_paths)
        factor = math.ceil(DESIRED_TRAIN_SIZE / img_count)

        # Define data augmentation strategies
        data_augmentation = keras.Sequential(
            [
                keras.layers.Rescaling(1.0 / 255),
                keras.layers.RandomRotation(0.2),
                keras.layers.RandomTranslation(0.2, 0.2),
                keras.layers.RandomZoom(0.2),
                keras.layers.RandomFlip("horizontal"),
                keras.layers.Resizing(*TARGET_SIZE),
            ]
        )

        # Apply transformations and repeat the dataset to augment data
        augmented_ds = train_ds.repeat(factor).map(
            lambda x: (
                data_augmentation(x, training=True),
                data_augmentation(x, training=True),
            ),
            num_parallel_calls=tf.data.AUTOTUNE,
        )

        # Extract features using the pre-trained MobileNetV3 model
        features = self.model.predict(augmented_ds)
        features = features.reshape(
            (features.shape[0], -1)
        )  # Flatten the features for SVM input

        # Set up the SVM and perform grid search for hyperparameter optimization
        svm = OneClassSVM()
        anomaly_scorer = make_scorer(
            lambda estimator, X: -estimator.decision_function(X).ravel()
        )
        params_grid = {
            "nu": [0.01, 0.05, 0.1, 0.5],
            "gamma": ["scale", "auto"],
            "kernel": ["rbf"],
        }

        grid_search = GridSearchCV(
            svm,
            param_grid=params_grid,
            scoring=anomaly_scorer,
            cv=5,
            n_jobs=-1,
        )

        # Fit the SVM model to the extracted features
        grid_search.fit(features)

        self.best_svm = grid_search.best_estimator_

        # Save the best SVM model
        path = config.SESSIONS_FOLDER / self.session_id / "svm"
        path.mkdir(parents=True, exist_ok=True)
        with open(path / "svm.pkl", "wb") as f:
            pickle.dump(self.best_svm, f)

        self.logger.info(
            "processed_training_images",
            session_id=self.session_id,
            model_name="svm",
            augmented_image_count=img_count * factor,
            analytics=True,
        )

        return Path("/", self.session_id) / "svm" / "svm.pkl"

    async def process_collection_images(self, img_path):
        # Log the start of processing collection images
        self.logger.info("Processing Collection Images", img_path=img_path)

        # Ensure the previously trained SVM model is loaded
        if not self.best_svm:
            raise ValueError("SVM model not loaded")

        # Create a dataset from the directory containing collection images
        collection_ds = keras.preprocessing.image_dataset_from_directory(
            img_path,
            labels=None,
            shuffle=False,
            image_size=TARGET_SIZE,
            batch_size=BATCH_SIZE,
        )

        # Extract file paths for later reference
        file_paths = [Path(path).name for path in collection_ds.file_paths]

        # Normalize and resize images
        data_augmentation = keras.Sequential(
            [
                keras.layers.Rescaling(1.0 / 255),
                keras.layers.Resizing(*TARGET_SIZE),
            ]
        )

        # Apply preprocessing to dataset
        collection_ds = collection_ds.map(
            data_augmentation, num_parallel_calls=tf.data.AUTOTUNE
        )

        # Predict with the SVM and extract decision function values
        features = self.model.predict(collection_ds)
        features = features.reshape((features.shape[0], -1))
        errors = self.best_svm.decision_function(features)

        self.logger.info("Paths and Scores", paths=file_paths, scores=errors)

        self.logger.info(
            "processed_collection_images",
            session_id=self.session_id,
            model_name="svm",
            image_count=len(file_paths),
            analytics=True,
        )

        return zip(file_paths, errors)
