#!/usr/bin/env python3
"""
:Author:  Geert De Paepe
:Email:   geert.de.paepe@vub.be
:License: MIT License
"""

import tensorflow as tf
from diresa.loss import LatentCovLoss, mse_dist_loss


def test_latent_cov_loss():
    # Create sample input tensors
    latent = tf.constant([[1., 3., 3.], [2., 6., 6.], [3., 9., 9.]], dtype=tf.float32)
    dummy = tf.constant([[0., 0., 0.], [0., 0., 0.], [0., 0., 0.]], dtype=tf.float32)

    # Create the loss object
    loss = LatentCovLoss()

    # Apply the loss to the input tensors
    cov_loss = loss(dummy, latent)

    # Expected output
    expected_cov_loss = 14.666667

    # Assert the output is as expected
    tf.debugging.assert_near(cov_loss, expected_cov_loss)


def test_mse_dist_loss():
    # Create sample input tensors
    distances = tf.constant([[1.0, 2.0], [2.0, 4.0], [3.0, 6.0]], dtype=tf.float32)
    dummy = tf.constant([[0., 0., 0.], [0., 0., 0.], [0., 0., 0.]], dtype=tf.float32)

    # Apply the loss function to the input tensors
    loss = mse_dist_loss(dummy, distances)

    # Expected output (calculated manually or using a reliable source)
    expected_loss = tf.constant([1.0, 4.0, 9.0], dtype=tf.float32)

    # Assert the output is as expected
    tf.debugging.assert_near(loss, expected_loss)


if __name__ == "__main__":
    test_mse_dist_loss()


if __name__ == "__main__":
    test_latent_cov_loss()
