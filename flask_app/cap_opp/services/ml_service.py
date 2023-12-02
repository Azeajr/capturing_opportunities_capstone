# cap_opp/ml_service.py
import os
from pathlib import Path

import numpy as np
import tensorflow as tf
from sklearn.metrics import make_scorer
from sklearn.model_selection import GridSearchCV
from sklearn.svm import OneClassSVM


class MLService:
    def __init__(self):
        # Load MobileNetV3 pre-trained on ImageNet without the top layer
        self.model = tf.keras.applications.MobileNetV3Large(
            weights="imagenet", include_top=False
        )
        self.best_svm = None  # Placeholder for the trained SVM model

    def preprocess_and_extract_features(self, img_dir):
        img_list = []
        img_paths = []
        for img_path in img_dir.glob("*.png"):
            try:
                # Load image and preprocess it for MobileNetV3
                img = tf.keras.preprocessing.image.load_img(
                    img_path, target_size=(224, 224)
                )
                img_array = tf.keras.preprocessing.image.img_to_array(img)
                img_array = tf.keras.applications.mobilenet_v3.preprocess_input(
                    img_array
                )
                img_list.append(img_array)
                img_paths.append(img_path)
            except Exception as e:
                print(f"Error processing image {img_path}: {e}")

        if not img_list:
            return np.array([])

        # Ensure that img_batch has a batch dimension
        img_batch = np.stack(img_list, axis=0)

        # Extract features using MobileNetV3
        features = self.model.predict(img_batch)
        features = features.reshape((features.shape[0], -1))  # Flatten the features
        return img_paths, features

    def train_svm(self, train_features):
        # Define the one-class SVM with a grid search for hyperparameter tuning
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
        clf.fit(train_features)
        self.best_svm = clf.best_estimator_
        self.threshold = np.quantile(
            self.best_svm.decision_function(train_features), 0.3
        )

    def predict(self, img_dir):
        if self.best_svm is None:
            raise ValueError("The SVM model has not been trained yet.")

        img_paths, new_features = self.preprocess_and_extract_features(img_dir)
        scores = self.best_svm.decision_function(new_features)
        predictions = self.best_svm.predict(new_features)
        return img_paths, scores, predictions

    def classify_images(self, scores):
        if self.threshold is None:
            raise ValueError("Threshold for anomaly detection has not been set.")

        return ["inlier" if score > self.threshold else "outlier" for score in scores]

    def process_images(self, img_path):
        # Convert single image path to a directory-like object for compatibility
        img_dir = Path(img_path)
        img_paths, scores, predictions = self.predict(img_dir)

        classifications = self.classify_images(scores)

        return zip(
            img_paths,
            predictions.tolist(),
            scores.tolist(),
            classifications,
        )


# Example usage:
# ml_service = MLService()
# train_dir = Path("path/to/train_images")
# train_features = ml_service.preprocess_and_extract_features(train_dir)
# ml_service.train_svm(train_features)
# img_dir = Path("path/to/new_images")
# scores, predictions = ml_service.predict(img_dir)
# classifications = ml_service.classify_images(scores)
