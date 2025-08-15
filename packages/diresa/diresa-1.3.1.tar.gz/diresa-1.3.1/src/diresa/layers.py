#!/usr/bin/env python3
"""
DIRESA custom layer classes

:Author:  Geert De Paepe
:Email:   geert.de.paepe@vub.be
:License: MIT License
"""

import tensorflow as tf
from tensorflow.keras import layers


@tf.keras.utils.register_keras_serializable()
class DistLayer(layers.Layer):
    """
    Calculates (squared) distances between the 2 inputs and distances between the 2 latent representations of a twin model
    """

    def __init__(self, dim_less=True, squared=True, name="Dist", **kwargs):
        """
        :param dim_less: if True distance is divided by dimension of space
        :param squared: if True distance is squared
        """
        super(DistLayer, self).__init__(name=name, **kwargs)
        self.dim_less = dim_less
        self.squared = squared

    def call(self, x1, x2, y1, y2):
        """
        :param x1: batch of input samples to encoder
        :param x2: batch of input shuffled samples to twin encoder
        :param y1: batch of latent representations of encoder
        :param y2: batch of latent representations of twin encoder
        :return: batch of distances between inputs, batch of distances between latent representations
        """
        dist1 = tf.math.square(x1 - x2)
        dist2 = tf.math.square(y1 - y2)
        dist1 = tf.reduce_sum(tf.reshape(dist1, [tf.shape(dist1)[0], -1]), axis=1)  # sum over all dims, except 0
        dist2 = tf.reduce_sum(tf.reshape(dist2, [tf.shape(dist2)[0], -1]), axis=1)  # sum over all dims, except 0
        if not self.squared:
            dist1 = tf.math.sqrt(dist1)
            dist2 = tf.math.sqrt(dist2)
        if self.dim_less:
            dim1 = tf.cast(tf.math.divide(tf.size(x1), tf.shape(x1)[0]), dtype=tf.float32)
            dist1 = tf.math.divide(dist1, dim1)  # divide by input dimension
            dim2 = tf.cast(tf.math.divide(tf.size(y1), tf.shape(y1)[0]), dtype=tf.float32)
            dist2 = tf.math.divide(dist2, dim2)  # divide by latent space dimension
        return tf.stack((dist1, dist2), axis=1)

    def get_config(self):
        config = super().get_config()
        config.update({'dim_less': self.dim_less})
        return config

    @classmethod
    def from_config(cls, config):
        return cls(**config)


@tf.keras.utils.register_keras_serializable()
class OrderLayer(layers.Layer):
    """
    Reorders the inputs according to a given order
    """

    def __init__(self, order, name=None, **kwargs):
        super(OrderLayer, self).__init__(name=name, **kwargs)
        self.order = order

    def call(self, x):
        """
        :param x: batch of inputs
        :return: batch with reordered inputs
        """
        y = tf.gather(x, self.order, axis=1)
        return y

    def get_config(self):
        config = super().get_config()
        config.update({'order': self.order})
        return config

    @classmethod
    def from_config(cls, config):
        return cls(**config)
