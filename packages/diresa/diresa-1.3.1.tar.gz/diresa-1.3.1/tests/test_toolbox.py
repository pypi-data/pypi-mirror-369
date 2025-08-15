#!/usr/bin/env python3
"""
:Author:  Geert De Paepe
:Email:   geert.de.paepe@vub.be
:License: MIT License
"""

from math import isclose
import tensorflow as tf
from diresa.toolbox import _covariance, _r2_score, _set_components_to_mean, decoded_latent_components


def test_covariance():
    # Create sample input tensors
    data = tf.constant([[2.1, 2.5, 3.6], [3.4, 4.1, 5.2], [4.5, 5.6, 6.7]], dtype=tf.float32)

    # Apply the function to the input tensors
    # numpy: np.cov(data, bias=True, rowvar=False)
    cov = _covariance(data)

    # Expected outputs
    expected_cov = [[0.96222230, 1.24111112, 1.24111112],
                    [1.24111112, 1.60222212, 1.60222212],
                    [1.24111112, 1.60222212, 1.60222212]]

    # Assert the outputs are as expected
    tf.debugging.assert_near(cov, expected_cov)


def test_r2_score():
    # Create sample input tensors
    y_true = tf.constant([[3, -0.5, 2, 7], [2, 0, 0, 1]], dtype=tf.float32)
    y_pred = tf.constant([[2.5, 0.0, 2, 8], [2, 0.5, 0, 1]], dtype=tf.float32)

    # Apply the function to the input tensors
    # scikit-learn: r2_score(y_true, y_pred, multioutput='variance_weighted')
    r2 = _r2_score(y_true, y_pred)

    # Expected outputs
    expected_r2 = 0.9151515

    # Assert the outputs are as expected
    assert isclose(r2, expected_r2, abs_tol=1e-5), f"Expected {expected_r2}, but got {r2}"


def test_set_components_to_mean():
    # Create sample input tensors
    latent = tf.constant([[1.0, 2.0, 3.0], [4.0, 5.0, 6.0], [7.0, 8.0, 9.0]], dtype=tf.float32)
    untouched = (1,)

    # Apply the function to the input tensors
    result = _set_components_to_mean(latent, untouched)

    # Expected outputs
    expected_result = tf.constant([[4.0, 2.0, 6.0], [4.0, 5.0, 6.0], [4.0, 8.0, 6.0]], dtype=tf.float32)

    # Assert the outputs are as expected
    tf.debugging.assert_near(result, expected_result)


def test_decoded_latent_components():
    # Create sample input tensors
    latent = tf.constant([[0.0, 0.0, 0.0], [4.0, 2.0, 8.0]], dtype=tf.float32)

    # Test model where output is equal to input
    x = tf.keras.layers.Input(shape=(latent.shape[1],))
    y = tf.keras.layers.Identity()(x)
    model = tf.keras.models.Model(inputs=x, outputs=y)

    # Apply the function to the input tensor and unity model
    result = decoded_latent_components(latent, model, factor=0.5)

    # Expected outputs
    expected_result = tf.constant([[2.0, 0.0, 0.0], [0.0, 1.0, 0.0], [0.0, 0.0, 4.0]], dtype=tf.float32)

    # Assert the outputs are as expected
    tf.debugging.assert_near(result, expected_result)


if __name__ == "__main__":
    test_set_components_to_mean()
