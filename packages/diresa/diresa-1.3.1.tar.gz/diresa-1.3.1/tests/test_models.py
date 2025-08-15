#!/usr/bin/env python3
"""
:Author:  Geert De Paepe
:Email:   geert.de.paepe@vub.be
:License: MIT License
"""

from diresa.models import build_diresa
from tensorflow.keras.activations import relu
from tensorflow.keras.layers import PReLU
from tensorflow.keras.initializers import Constant


def test_build_models():
    hyper_params = [{"input_shape": [8, 8, 1], "stack": [1, ], "stack_filters": [32, ],
                     "dense_units": (), "up_first": False},
                    {"input_shape": [8, 8, 1], "stack": [1, ], "stack_filters": [32, ],
                     "dense_units": (), "up_first": True},
                    {"input_shape": [8, 8, 1], "stack": [1, ], "stack_filters": [32, ],
                     "dense_units": (), "up_first": True, "conv_transpose": True, "activation": "sigmoid"},
                    {"input_shape": [8, 8, 1], "stack": [1, ], "stack_filters": [32, ],
                     "dense_units": (), "up_first": True, "residual": True},
                    {"input_shape": [8, 8, 1], "stack": [3, ], "stack_filters": [32, ],
                     "dense_units": (), "up_first": False},
                    {"input_shape": [8, 8, 1], "stack": [3, ], "stack_filters": [32, ],
                     "dense_units": (), "up_first": True, "activation": relu},
                    {"input_shape": [8, 8, 1], "stack": [3, ], "stack_filters": [32, ],
                     "dense_units": (), "up_first": True, "attention": True, "conv_transpose": True},
                    {"input_shape": [8, 8, 1], "stack": [3, ], "stack_filters": [32, ],
                     "dense_units": (), "up_first": True, "residual": True},
                    {"input_shape": [8, 8, 1], "stack": [1, 1], "stack_filters": [32, 16],
                     "dense_units": (), "up_first": False,
                     "activation": PReLU, "activation_layer_param": {"alpha_initializer": Constant(-1.), "shared_axes": [1, 2]}},
                    {"input_shape": [8, 8, 1], "stack": [1, 1], "stack_filters": [32, 16],
                     "dense_units": (), "attention": True, "up_first": True},
                    {"input_shape": [8, 8, 1], "stack": [1, 1], "stack_filters": [32, 16],
                     "dense_units": (), "up_first": True, "conv_transpose": True},
                    {"input_shape": [8, 8, 1], "stack": [1, 1], "stack_filters": [32, 16],
                     "dense_units": (), "up_first": True, "attention": True, "residual": True},
                    {"input_shape": [20, ], "dense_units": [15, 10, 5]},
                    {"input_shape": [20, ], "stack": [], "stack_filters": [], "dense_units": (15, 10, 5),
                     "activation": PReLU, "activation_layer_param": {"alpha_initializer": Constant(-1.), "shared_axes": [1]}},
                    {"input_shape": [8, 8, 1], "stack": [2, ], "stack_filters": [32, ],
                     "dense_units": [20, 10], "up_first": False},
                    {"input_shape": [8, 8, 1], "stack": [2, ], "stack_filters": [32, ],
                     "dense_units": [20, 10], "up_first": True},
                    {"input_shape": [8, 8, 1], "stack": [2, ], "stack_filters": [32, ],
                     "dense_units": [20, 10], "up_first": True, "conv_transpose": True},
                    {"input_shape": [8, 8, 1], "stack": [2, ], "stack_filters": [32, ],
                     "dense_units": [20, 10], "up_first": True, "attention": True, "residual": True,
                     "activation": PReLU, "activation_layer_param": {"alpha_initializer": Constant(-1.)}},
                    {"input_shape": [8, 8, 1], "stack": [1, 1], "stack_filters": [32, 16],
                     "dense_units": [20, 10], "up_first": False},
                    {"input_shape": [8, 8, 1], "stack": [1, 1], "stack_filters": [32, 16],
                     "dense_units": [20, 10], "up_first": True},
                    {"input_shape": [8, 8, 1], "stack": [1, 2], "stack_filters": [32, 16],
                     "dense_units": [20, 10], "up_first": True, "conv_transpose": True},
                    {"input_shape": [8, 8, 1], "stack": [1, 2], "stack_filters": [32, 16],
                     "dense_units": [20, 10], "up_first": True, "residual": True},
                    {"input_shape": [8, 8, 1], "stack": [1, 1], "stack_filters": [32, 16],
                     "dense_units": [20, 10, 10], "dropout_rate": 0.25, "activation": relu},
                    {"input_shape": [8, 8, 1], "stack": [1, 1], "attention": [False, True], "stack_filters": [32, 16],
                     "dense_units": [20, 10, 10], "kernel_initializer": "he_normal", "kernel_regularizer": "L2"},
                    ]
    for hyper_param in hyper_params:
        print("\n\n", hyper_param)
        diresa = build_diresa(**hyper_param)
        diresa.summary(expand_nested=True)


if __name__ == "__main__":
    test_build_models()
