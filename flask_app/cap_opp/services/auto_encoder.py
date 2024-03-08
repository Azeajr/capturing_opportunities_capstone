from typing import Any
from cap_opp.services.base import MlABC

import tensorflow as tf
from pathlib import Path
import random
import math
import shutil
import numpy as np
import structlog


ImageDataGenerator = tf.keras.preprocessing.image.ImageDataGenerator
Model = tf.keras.models.Model
Input = tf.keras.layers.Input
Conv2D = tf.keras.layers.Conv2D
MaxPooling2D = tf.keras.layers.MaxPooling2D
UpSampling2D = tf.keras.layers.UpSampling2D
# TARGET_SIZE = (1920, 1080)
TARGET_SIZE = (224, 224)
BATCH_SIZE = 32
DESIRED_DATASET_SIZE = 100


class AutoEncoder(MlABC):
    def __init__(self, augment=False, min_training_size=100):
        self.augment = augment
        self.min_training_size = max(min_training_size, 100)
        self.logger = structlog.get_logger()
        self.autoencoder = None

    def process_training_images(self, img_path):
        self.logger.info("Processing Training Images", img_path=img_path)

        img_path = img_path.parent

        datagen = ImageDataGenerator(
            rescale=1.0 / 255,
            rotation_range=20,
            width_shift_range=0.2,
            height_shift_range=0.2,
            shear_range=0.2,
            zoom_range=0.2,
            horizontal_flip=True,
            fill_mode="nearest",
        )

        augmented_ds = datagen.flow_from_directory(
            img_path,
            target_size=TARGET_SIZE,
            batch_size=BATCH_SIZE,
            class_mode="input",
            shuffle=True,
        )

        # train_ds: tf.data.Dataset = tf.keras.preprocessing.image_dataset_from_directory(
        #     img_path,
        #     labels=None,
        #     # labels="inferred",
        #     # label_mode="int",
        #     # validation_split=0.2,
        #     # subset="training",
        #     seed=123,
        #     image_size=TARGET_SIZE,
        #     batch_size=BATCH_SIZE,
        # )

        # data_augmentation = tf.keras.Sequential(
        #     [
        #         tf.keras.layers.Rescaling(1.0 / 255),
        #         tf.keras.layers.RandomFlip("horizontal_and_vertical"),
        #         tf.keras.layers.RandomRotation(0.2),
        #         tf.keras.layers.RandomZoom(0.2),
        #         tf.keras.layers.RandomTranslation(height_factor=0.2, width_factor=0.2),
        #         tf.keras.layers.RandomContrast(factor=0.2),
        #     ]
        # )

        # augmented_ds = train_ds.map(
        #     lambda image: (data_augmentation(image, training=True), image),
        #     num_parallel_calls=tf.data.AUTOTUNE,
        # ).repeat(DESIRED_DATASET_SIZE // BATCH_SIZE)

        input_img = Input(shape=(224, 224, 3))
        x = Conv2D(32, (3, 3), activation="relu", padding="same")(input_img)
        x = MaxPooling2D((2, 2), padding="same")(x)
        x = Conv2D(16, (3, 3), activation="relu", padding="same")(x)
        encoded = MaxPooling2D((2, 2), padding="same")(x)

        x = Conv2D(16, (3, 3), activation="relu", padding="same")(encoded)
        x = UpSampling2D((2, 2))(x)
        x = Conv2D(32, (3, 3), activation="relu", padding="same")(x)
        x = UpSampling2D((2, 2))(x)
        decoded = Conv2D(3, (3, 3), activation="sigmoid", padding="same")(x)

        autoencoder = Model(input_img, decoded)
        autoencoder.compile(optimizer="adam", loss="binary_crossentropy")

        desired_dataset_size = 100
        steps_per_epoch = desired_dataset_size // BATCH_SIZE
        epochs = 10

        # autoencoder.fit(
        #     augmented_ds,
        #     epochs=epochs,
        #     # steps_per_epoch=steps_per_epoch,
        # )

        epochs = 100
        steps_per_epoch = 1

        for _ in range(epochs):
            for _ in range(steps_per_epoch):
                images, _ = next(augmented_ds)
                self.logger.info(
                    "training loss", loss=autoencoder.train_on_batch(images, images)
                )

        self.autoencoder = autoencoder

    def process_collection_images(self, img_path):
        collection_ds: tf.data.Dataset = (
            tf.keras.preprocessing.image_dataset_from_directory(
                img_path,
                labels=None,
                seed=123,
                shuffle=False,
                image_size=TARGET_SIZE,
                batch_size=BATCH_SIZE,
            )
        )

        file_paths = [Path(path).name for path in collection_ds.file_paths]

        data_augmentation = tf.keras.Sequential(
            [
                tf.keras.layers.Rescaling(1.0 / 255),
            ]
        )

        collection_ds = collection_ds.map(
            data_augmentation, num_parallel_calls=tf.data.AUTOTUNE
        )

        self.logger.info("Processing Collection Images", img_path=img_path)
        self.logger.info("Collection DS", collection_ds=collection_ds)

        reconstruction_errors = []
        original_images = []
        reconstructed_images = []

        for batch in collection_ds:
            # self.logger.info("Batch", batch=batch)
            # Get the reconstructed images
            reconstructed = self.autoencoder.predict(batch)
            # Calculate MAE for each image in the batch
            batch_errors = tf.reduce_mean(tf.abs(batch - reconstructed), axis=(1, 2, 3))

            # self.logger.info("Batch Errors", batch_errors=batch_errors)

            reconstruction_errors.extend(batch_errors)
            original_images.extend(batch.numpy())
            reconstructed_images.extend(reconstructed)

        errors = np.array(reconstruction_errors)
        originals = np.array(original_images)
        reconstructs = np.array(reconstructed_images)

        # self.logger.info(
        #     "Paths and Scores",
        #     file_paths=file_paths,
        #     errors=errors.tolist(),
        # )

        # self.logger.info(
        #     "Paths and Scores",
        #     errors=errors.tolist(),
        #     originals=originals.tolist(),
        #     reconstructs=reconstructs.tolist(),
        # )

        return zip(
            file_paths,
            errors.tolist(),
        )

    def preprocess_and_extract_features(self, img_dir, augment=None):
        if augment is None:
            augment = self.augment

        img_dir_size = len(list(img_dir.glob("*")))
        factor = (
            (self.min_training_size + img_dir_size - 1) // img_dir_size
            if img_dir_size > 0
            else 0
        )

        img_list = []

    # TODO: Rename to train
    def train_svm(self, train_features):
        pass

    def process_images(self, img_path):
        pass

    # Function to load and preprocess images for training
    def load_and_preprocess_images(
        self,
        directory,
        target_size=TARGET_SIZE,
        batch_size=32,
        subset_fraction=None,
        subset_number=None,
    ):
        datagen = ImageDataGenerator(
            rescale=1.0 / 255,
            rotation_range=20,
            width_shift_range=0.2,
            height_shift_range=0.2,
            shear_range=0.2,
            zoom_range=0.2,
            horizontal_flip=True,
            fill_mode="nearest",
        )

        generator = datagen.flow_from_directory(
            directory,
            target_size=target_size,
            batch_size=batch_size,
            class_mode="input",
            shuffle=True,
        )
        for images, _ in generator:
            paths = [Path(directory) / Path(path) for path in generator.filenames]
            yield images, paths

    # Function to load images for assessment without augmentation
    def load_images_for_assessment(
        self, directory, target_size=TARGET_SIZE, batch_size=32
    ):
        datagen = ImageDataGenerator(rescale=1.0 / 255)
        generator = datagen.flow_from_directory(
            directory,
            target_size=target_size,
            batch_size=batch_size,
            class_mode="input",
            shuffle=False,
        )

        for images, _ in generator:
            paths = [Path(directory) / Path(path) for path in generator.filenames]
            yield images, paths

    # Building the autoencoder
    def build_autoencoder(self, input_shape):
        input_img = Input(shape=input_shape)
        x = Conv2D(32, (3, 3), activation="relu", padding="same")(input_img)
        x = MaxPooling2D((2, 2), padding="same")(x)
        x = Conv2D(16, (3, 3), activation="relu", padding="same")(x)
        encoded = MaxPooling2D((2, 2), padding="same")(x)

        x = Conv2D(16, (3, 3), activation="relu", padding="same")(encoded)
        x = UpSampling2D((2, 2))(x)
        x = Conv2D(32, (3, 3), activation="relu", padding="same")(x)
        x = UpSampling2D((2, 2))(x)
        decoded = Conv2D(3, (3, 3), activation="sigmoid", padding="same")(x)

        autoencoder = Model(input_img, decoded)
        autoencoder.compile(optimizer="adam", loss="binary_crossentropy")

        return autoencoder

    # Training the autoencoder
    def train_autoencoder(
        self, autoencoder, train_generator, epochs=50, steps_per_epoch=200
    ):
        # autoencoder.fit(train_generator, epochs=epochs, steps_per_epoch=steps_per_epoch)
        all_image_paths = []
        for _ in range(epochs):
            for _ in range(steps_per_epoch):
                images, paths = next(train_generator)
                autoencoder.train_on_batch(images, images)
                all_image_paths.extend(paths)

        return all_image_paths

    # Feature extraction and anomaly detection
    def get_encoded_images(self, model, data_generator):
        encoder = Model(inputs=model.input, outputs=model.get_layer(index=4).output)
        encoded_images = encoder.predict(data_generator)
        return encoded_images

    def get_reconstruction_error(self, model, data):
        reconstructed = model.predict(data)
        reconstruction_error = np.mean(np.abs(data - reconstructed), axis=(1, 2, 3))
        return reconstruction_error

    # Function to calculate the reconstruction error
    def calculate_reconstruction_error(self, model, generator, steps):
        all_reconstruction_errors = []
        all_paths = []

        # Loop over the generator to process all images
        for _ in range(steps):
            images, paths = next(generator)
            reconstructed = model.predict(
                images
            )  # Reconstruct the images using the autoencoder
            batch_reconstruction_error = np.mean(
                np.abs(images - reconstructed), axis=(1, 2, 3)
            )

            all_reconstruction_errors.extend(batch_reconstruction_error)
            all_paths.extend(paths)

        return all_paths, all_reconstruction_errors
