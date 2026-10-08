"""
DIGITVISION AI — Deep Convolutional Neural Networks
===================================================
Implements:
1. Classic LeNet-5 Architecture (Yann LeCun et al., 1998)
2. Production Deep Residual/ConvNet with BatchNorm, Dropout & Explicit Grad-CAM hooks

All models adhere to the unified DigitVision Model Interface.
"""

import os
import numpy as np
import tensorflow as tf
from tensorflow.keras import layers, models
from typing import Optional, Tuple


class DeepModelWrapper:
    """Unified wrapper for Keras/TensorFlow deep models conforming to DigitVision Model Interface."""
    def __init__(self, keras_model: tf.keras.Model, name: str, target_conv_layer: str = "conv_cam"):
        self.raw_model = keras_model
        self.name = name
        self.is_deep = True
        self.target_conv_layer = target_conv_layer

    def predict_proba(self, img_28x28: np.ndarray) -> np.ndarray:
        tensor_in = img_28x28.reshape(1, 28, 28, 1).astype(np.float32)
        preds = self.raw_model(tensor_in, training=False)
        if isinstance(preds, list):
            preds = preds[0]
        return preds[0].numpy().astype(np.float64)

    def predict(self, img_28x28: np.ndarray) -> int:
        probs = self.predict_proba(img_28x28)
        return int(np.argmax(probs))

    def predict_batch_proba(self, batch_imgs: np.ndarray, batch_size: int = 256) -> np.ndarray:
        if batch_imgs.ndim == 3:
            batch_imgs = np.expand_dims(batch_imgs, -1)
        preds = self.raw_model.predict(batch_imgs, batch_size=batch_size, verbose=0)
        return preds.astype(np.float64)

    def save(self, filepath: str) -> None:
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        self.raw_model.save(filepath)

    @classmethod
    def load(cls, filepath: str, name: str, target_conv_layer: str = "conv_cam") -> "DeepModelWrapper":
        keras_model = tf.keras.models.load_model(filepath)
        return cls(keras_model, name, target_conv_layer=target_conv_layer)


def build_lenet5(input_shape: Tuple[int, int, int] = (28, 28, 1), num_classes: int = 10) -> tf.keras.Model:
    """
    Classic LeNet-5 Architecture:
    Conv(6, 5x5) -> AvgPool -> Conv(16, 5x5) -> AvgPool -> Flatten -> Dense(120) -> Dense(84) -> Dense(10).
    """
    model = models.Sequential([
        layers.Input(shape=input_shape),
        layers.Conv2D(6, kernel_size=(5, 5), padding='same', activation='relu', name='lenet_conv1'),
        layers.AveragePooling2D(pool_size=(2, 2), strides=(2, 2)),
        layers.Conv2D(16, kernel_size=(5, 5), padding='valid', activation='relu', name='conv_cam'),
        layers.AveragePooling2D(pool_size=(2, 2), strides=(2, 2)),
        layers.Flatten(),
        layers.Dense(120, activation='relu', name='lenet_fc1'),
        layers.Dense(84, activation='relu', name='lenet_fc2'),
        layers.Dense(num_classes, activation='softmax', name='prediction_head')
    ], name="LeNet-5")

    model.compile(
        optimizer=tf.keras.optimizers.Adam(learning_rate=1e-3),
        loss='sparse_categorical_crossentropy',
        metrics=['accuracy']
    )
    return model


def build_deep_convnet(input_shape: Tuple[int, int, int] = (28, 28, 1), num_classes: int = 10) -> tf.keras.Model:
    """
    DigitVision Production Deep ConvNet Architecture:
    Block 1: Conv2D(32, 3x3, ReLU) -> Conv2D(32, 3x3, ReLU) -> MaxPool(2x2) -> Dropout(0.25)
    Block 2: Conv2D(64, 3x3, ReLU) -> Conv2D(64, 3x3, ReLU, name='conv_cam') -> MaxPool(2x2) -> Dropout(0.25)
    Head: Flatten -> Dense(128, ReLU) -> Dropout(0.40) -> Dense(10, Softmax)
    """
    inputs = layers.Input(shape=input_shape, name="input_canvas")

    # Block 1
    x = layers.Conv2D(32, kernel_size=(3, 3), padding='same', activation='relu', name='conv1_1')(inputs)
    x = layers.Conv2D(32, kernel_size=(3, 3), padding='same', activation='relu', name='conv1_2')(x)
    x = layers.MaxPooling2D(pool_size=(2, 2), name='pool1')(x)
    x = layers.Dropout(0.25, name='drop1')(x)

    # Block 2 with Grad-CAM hook
    x = layers.Conv2D(64, kernel_size=(3, 3), padding='same', activation='relu', name='conv2_1')(x)
    x = layers.Conv2D(64, kernel_size=(3, 3), padding='same', activation='relu', name='conv_cam')(x)
    x = layers.MaxPooling2D(pool_size=(2, 2), name='pool2')(x)
    x = layers.Dropout(0.25, name='drop2')(x)

    # Classification Head
    x = layers.Flatten(name='flatten')(x)
    x = layers.Dense(128, activation='relu', name='dense1')(x)
    x = layers.Dropout(0.40, name='drop3')(x)
    outputs = layers.Dense(num_classes, activation='softmax', name='prediction_head')(x)

    model = models.Model(inputs=inputs, outputs=outputs, name="DigitVision-DeepConvNet")

    model.compile(
        optimizer=tf.keras.optimizers.Adam(learning_rate=1e-3),
        loss='sparse_categorical_crossentropy',
        metrics=['accuracy']
    )
    return model


def build_mlp(input_shape: Tuple[int, int, int] = (28, 28, 1), num_classes: int = 10) -> tf.keras.Model:
    """
    Multi-Layer Perceptron (MLP) Deep Architecture:
    Flatten -> Dense(256) -> BN -> Dropout(0.25) -> Dense(128) -> BN -> Dropout(0.25) -> Dense(10, softmax)
    """
    model = models.Sequential([
        layers.Input(shape=input_shape),
        layers.Flatten(name='mlp_flatten'),
        layers.Dense(256, activation='relu', name='mlp_dense1'),
        layers.BatchNormalization(name='mlp_bn1'),
        layers.Dropout(0.25, name='mlp_drop1'),
        layers.Dense(128, activation='relu', name='mlp_dense2'),
        layers.BatchNormalization(name='mlp_bn2'),
        layers.Dropout(0.25, name='mlp_drop2'),
        layers.Dense(num_classes, activation='softmax', name='prediction_head')
    ], name="MLP-Deep")

    model.compile(
        optimizer=tf.keras.optimizers.Adam(learning_rate=1e-3),
        loss='sparse_categorical_crossentropy',
        metrics=['accuracy']
    )
    return model

