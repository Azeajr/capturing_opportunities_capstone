import uuid
from pathlib import Path

# from keras.layers import Input, Conv2D, MaxPooling2D, UpSampling2D
import keras
import numpy as np
import structlog
import tensorflow as tf

# from keras.preproc
from keras.models import Model

from app.config import get_config
from app.services.base import MlABC

config = get_config()

ImageDataGenerator = tf.keras.preprocessing.image.ImageDataGenerator

TARGET_SIZE = (224, 224)
BATCH_SIZE = 32
DESIRED_DATASET_SIZE = 100


class AutoEncoder(MlABC):
    def __init__(self, model_path: Path = None):
        self.logger = structlog.get_logger()
        if model_path:
            self.logger.info(
                "AutoEncoder",
                model_path=model_path,
                full_path=(config.MODELS_FOLDER / "auto_encoder" / model_path),
            )
        self.autoencoder = (
            keras.models.load_model(config.MODELS_FOLDER / "auto_encoder" / model_path)
            if model_path
            else None
        )

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

        input_img = keras.layers.Input(shape=(224, 224, 3))
        x = keras.layers.Conv2D(32, (3, 3), activation="relu", padding="same")(
            input_img
        )
        x = keras.layers.MaxPooling2D((2, 2), padding="same")(x)
        x = keras.layers.Conv2D(16, (3, 3), activation="relu", padding="same")(x)
        encoded = keras.layers.MaxPooling2D((2, 2), padding="same")(x)

        x = keras.layers.Conv2D(16, (3, 3), activation="relu", padding="same")(encoded)
        x = keras.layers.UpSampling2D((2, 2))(x)
        x = keras.layers.Conv2D(32, (3, 3), activation="relu", padding="same")(x)
        x = keras.layers.UpSampling2D((2, 2))(x)
        decoded = keras.layers.Conv2D(3, (3, 3), activation="sigmoid", padding="same")(
            x
        )

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

        model_id = uuid.uuid4()
        path = config.MODELS_FOLDER / "auto_encoder" / str(model_id)
        path.mkdir(parents=True, exist_ok=True)
        autoencoder.save(path / "autoencoder.keras")

        return Path("/auto_encoder") / str(model_id) / "autoencoder.keras"

    def process_collection_images(self, img_path):
        if not self.autoencoder:
            raise ValueError("Autoencoder model not loaded")

        collection_ds: tf.data.Dataset = (
            keras.preprocessing.image_dataset_from_directory(
                img_path,
                labels=None,
                seed=123,
                shuffle=False,
                image_size=TARGET_SIZE,
                batch_size=BATCH_SIZE,
            )
        )

        file_paths = [Path(path).name for path in collection_ds.file_paths]

        data_augmentation = keras.Sequential(
            [
                keras.layers.Rescaling(1.0 / 255),
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