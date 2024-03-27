from pathlib import Path

import numpy as np
import structlog
import tensorflow as tf

from app.services.base import MlABC

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
    def __init__(self):
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

        return zip(
            file_paths,
            errors.tolist(),
        )
