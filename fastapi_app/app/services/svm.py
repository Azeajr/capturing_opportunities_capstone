from pathlib import Path

import numpy as np
import structlog
import tensorflow as tf
from sklearn.metrics import make_scorer
from sklearn.model_selection import GridSearchCV
from sklearn.svm import OneClassSVM

from app.services.base import MlABC

# log = structlog.get_logger()

# Minimum number of training images required to train the SVM
min_training_size = 100


class SVM(MlABC):
    def __init__(self):
        self.logger = structlog.get_logger()
        # Load MobileNetV3 pre-trained on ImageNet without the top layer
        self.model = tf.keras.applications.MobileNetV3Large(
            weights="imagenet", include_top=False
        )
        self.best_svm = None  # Placeholder for the trained SVM model

    def process_training_images(self, img_path):
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
            return np.array([])

        self.logger.info("Length of training images", length=len(img_list))
        # Ensure that img_batch has a batch dimension
        img_batch = np.stack(img_list, axis=0)

        # Extract features using MobileNetV3
        features = self.model.predict(img_batch)
        features = features.reshape((features.shape[0], -1))  # Flatten the features

        params = {
            "nu": [0.01, 0.05, 0.1, 0.5],
            "gamma": ["scale", "auto"],
            "kernel": ["rbf"],
        }
        svm = OneClassSVM()
        anomaly_scorer = make_scorer(
            lambda estimator, X: -estimator.decision_function(X).ravel()
        )
        clf = GridSearchCV(svm, params, scoring=anomaly_scorer, cv=5, n_jobs=-1)
        clf.fit(features)
        self.best_svm = clf.best_estimator_

    def process_collection_images(self, img_path):
        # Convert single image path to a directory-like object for compatibility

        if self.best_svm is None:
            raise ValueError("The SVM model has not been trained yet.")

        img_paths: list[Path] = []
        img_list = []
        for path in img_path.glob("*.png"):
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

        # return zip(
        #     img_paths,
        #     predictions.tolist(),
        #     scores.tolist(),
        #     classifications,
        # )
        return zip(img_paths, scores.tolist())
