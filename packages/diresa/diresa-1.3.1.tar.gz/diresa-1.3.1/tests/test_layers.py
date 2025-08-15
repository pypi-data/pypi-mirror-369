#!/usr/bin/env python3
"""
:Author:  Geert De Paepe
:Email:   geert.de.paepe@vub.be
:License: MIT License
"""

import tensorflow as tf
from diresa.layers import DistLayer, OrderLayer


# write test for Dist
def test_dist_layer():
    # Create sample input tensors
    x1 = tf.constant([[2, 3, 4], [7, 5, 6]], dtype=tf.float32)
    x2 = tf.constant([[1, 2, 3], [4, 5, 6]], dtype=tf.float32)
    y1 = tf.constant([[2, 3], [5, 4]], dtype=tf.float32)
    y2 = tf.constant([[1, 2], [3, 4]], dtype=tf.float32)

    # Create the DistLayers
    dist_layer1 = DistLayer(dim_less=False, squared=False)
    dist_layer2 = DistLayer(dim_less=True, squared=True)

    # Apply the layers to the input tensors
    output_tensor1 = dist_layer1(x1, x2, y1, y2)
    output_tensor2 = dist_layer2(x1, x2, y1, y2)

    # Expected outputs
    expected_output1 = tf.math.sqrt(tf.constant([[3, 2], [9, 4]], dtype=tf.float32))
    expected_output2 = tf.constant([[1, 1], [3, 2]], dtype=tf.float32)


    # Assert the outputs are as expected
    tf.debugging.assert_near(output_tensor1, expected_output1)
    tf.debugging.assert_near(output_tensor2, expected_output2)


def test_order_layer():
    # Create a sample input tensor
    input_tensor = tf.constant([[1, 2, 3], [4, 5, 6], [7, 8, 9]], dtype=tf.float32)

    # Define the order
    order = [2, 0, 1]

    # Create the OrderLayer
    order_layer = OrderLayer(order=order)

    # Apply the layer to the input tensor
    output_tensor = order_layer(input_tensor)

    # Expected output
    expected_output = tf.constant([[3, 1, 2], [6, 4, 5], [9, 7, 8]], dtype=tf.float32)

    # Assert the output is as expected
    tf.debugging.assert_equal(output_tensor, expected_output)


if __name__ == "__main__":
    test_dist_layer()
    test_order_layer()
