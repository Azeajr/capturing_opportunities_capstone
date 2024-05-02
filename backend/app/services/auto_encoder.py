import math
from pathlib import Path
import keras
import numpy as np
import structlog
import tensorflow as tf
from keras.models import Model

from app.config import get_config
from app.services.base import MlABC

# Retrieve application configuration
config = get_config()

TARGET_SIZE = (224, 224)
BATCH_SIZE = 32
DESIRED_TRAIN_SIZE = 100


class AutoEncoder(MlABC):
    def __init__(self, session_id: str, is_training: bool = True):
        # Initialize logger
        self.logger = structlog.get_logger()
        self.session_id = session_id

        # Load pre-trained autoencoder model if not training
        if is_training:
            self.autoencoder = None
        else:
            self.autoencoder = keras.models.load_model(
                config.SESSIONS_FOLDER
                / session_id
                / "auto_encoder"
                / "autoencoder.keras"
            )

    async def process_training_images(self, img_path):
        # Log the start of image processing
        self.logger.info("Processing Training Images", img_path=img_path)

        train_ds = keras.preprocessing.image_dataset_from_directory(
            img_path,
            labels=None,
            image_size=TARGET_SIZE,
            batch_size=BATCH_SIZE,
        )

        img_count = len(train_ds.file_paths)
        factor = math.ceil(DESIRED_TRAIN_SIZE / img_count)

        data_augmentation = keras.Sequential(
            [
                keras.layers.Rescaling(1.0 / 255),
                keras.layers.RandomRotation(0.1),
                keras.layers.RandomTranslation(0.1, 0.1),
                keras.layers.RandomZoom(0.1),
                keras.layers.RandomFlip(),
                keras.layers.Resizing(*TARGET_SIZE),
            ]
        )

        augmented_ds = train_ds.repeat(factor).map(
            lambda x: (
                data_augmentation(x, training=True),
                data_augmentation(x, training=True),
            ),
            num_parallel_calls=tf.data.AUTOTUNE,
        )

        # Define autoencoder architecture
        input_img = keras.layers.Input(shape=(224, 224, 3))  # Input layer
        x = keras.layers.Conv2D(32, (3, 3), activation="relu", padding="same")(
            input_img
        )
        x = keras.layers.MaxPooling2D((2, 2), padding="same")(x)
        x = keras.layers.Conv2D(16, (3, 3), activation="relu", padding="same")(x)
        encoded = keras.layers.MaxPooling2D((2, 2), padding="same")(x)

        # Decoding architecture
        x = keras.layers.Conv2D(16, (3, 3), activation="relu", padding="same")(encoded)
        x = keras.layers.UpSampling2D((2, 2))(x)
        x = keras.layers.Conv2D(32, (3, 3), activation="relu", padding="same")(x)
        x = keras.layers.UpSampling2D((2, 2))(x)
        decoded = keras.layers.Conv2D(3, (3, 3), activation="sigmoid", padding="same")(
            x
        )

        # Complete model setup
        autoencoder = Model(input_img, decoded)
        autoencoder.compile(optimizer="adam", loss="binary_crossentropy")

        steps_per_epoch = img_count * factor // BATCH_SIZE
        autoencoder.fit(
            augmented_ds,
            epochs=10,
            steps_per_epoch=steps_per_epoch,
        )

        # Save the trained model
        self.autoencoder = autoencoder
        path = config.SESSIONS_FOLDER / self.session_id / "auto_encoder"
        path.mkdir(parents=True, exist_ok=True)
        autoencoder.save(path / "autoencoder.keras")

        self.logger.info(
            "processed_training_images",
            session_id=self.session_id,
            model_name="auto_encoder",
            augmented_image_count=img_count * factor,
            analytics=True,
        )

        return Path("/", self.session_id) / "auto_encoder" / "autoencoder.keras"

    async def process_collection_images(self, img_path):
        if not self.autoencoder:
            raise ValueError("Autoencoder model not loaded")

        collection_ds: tf.data.Dataset = (
            keras.preprocessing.image_dataset_from_directory(
                img_path,
                labels=None,
                shuffle=False,
                image_size=TARGET_SIZE,
                batch_size=BATCH_SIZE,
            )
        )

        # Extract file paths from dataset for reference
        file_paths = [Path(path).name for path in collection_ds.file_paths]

        # Data preprocessing to normalize images
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

        def compute_error(batch):
            reconstructions = self.autoencoder(batch, training=False)
            return tf.reduce_mean(tf.abs(batch - reconstructions), axis=(1, 2, 3))

        errors = collection_ds.map(compute_error, num_parallel_calls=tf.data.AUTOTUNE)

        errors = np.concatenate(list(errors.as_numpy_iterator()))

        self.logger.info(
            "processed_collection_images",
            session_id=self.session_id,
            model_name="auto_encoder",
            image_count=len(file_paths),
            analytics=True,
        )

        return zip(file_paths, errors.tolist())
