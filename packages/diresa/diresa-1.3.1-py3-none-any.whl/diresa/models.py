#!/usr/bin/env python3
"""
Creates DIRESA and AE models out of an encoder and decoder model.
Creates DIRESA and AE models from hyperparameters.

:Author:  Geert De Paepe
:Email:   geert.de.paepe@vub.be
:License: MIT License

1. Creating AE and Diresa models out of an encoder and decoder model:
  - autoencoder_model(x, encoder, decoder)
  - diresa_model(x, x_twin, encoder, decoder)

2. Creating AE and Diresa models from hyperparameters
  - build_ae(input_shape, stack, stack_filters, latent_filters, kernel_size=(3, 3),
    conv_transpose=False, up_first=False, attention=False, residual=False, dense_units=(), dropout_rate=0,
    activation='relu', encoder_activation='linear', decoder_activation='linear', **kwargs)
  - build_diresa(input_shape, stack, stack_filters, latent_filters, kernel_size=(3, 3),
    conv_transpose=False, up_first=False, attention=False, residual=False, dense_units=(), dropout_rate=0,
    activation='relu', encoder_activation='linear', decoder_activation='linear', **kwargs)

   Encoder:
    - 0 or more [blocks] with C (Conv2D) or residual units and a P (MaxPooling layer)
    - 0 or 1 [block] of D (Dense layers)
   Decoder:
    - 0 or 1 [block] with D (Dense layers)
    - 0 or more [blocks] with C (Conv2D) or residual units and an U (UpSampling layer)
   Examples:
    - stack;     dense_units;  Encoder;                Decoder (up_first=True);    Decoder (up_first=False)
    - [1];       ();           [C-P]-Cout;             [U-C]-Cout;                 [C-U]-Cout
    - [3];       ();           [C-C-C-P]-Cout;         [U-C-C-C]-Cout;             [C-U-C-C]-Cout
    - [1,1];     ();           [C-P]-[C-P]-Cout;       [U-C]-[U-C]-Cout;           [C-U]-[C-U]-Cout
    - ();        [20,10];      [D-Dout];               [D-Dout];                   [D-Dout]
    - [2];       [20,10];      [C-C-P]-[D-Dout];       [D-D]-[U-C]-Cout;           [D-D]-[C-U]-Cout
    - [1,1];     [20,10];      [C-P]-[C-P]-[D-Dout];   [D-D]-[U]-[U-C]-Cout;       [D-D]-[U]-[C-U]-Cout

   If conv_transpose=True, C is a ConvTranspose layer, only possible for up_first=True.
   If attention=True, attention layer is added after last C in block.
   Attention can also be a list of Boolean with length equal the number of blocks.
   If residual=True, C is a ResNet V1 residual unit with a skip connection, only possible for up_first=True.
   If attention=True and residual=True, C is ResNet V1 and attention layer with skip connection is added.
   If dropout_rate!=0, Dropout(dropout_rate) is added between Dense units, only possible if len(dense_units)>0.
   kwargs are passed to all Conv2D and Dense layers, e.g. they can be used for changing kernel_initializer or kernel_regularizer.
   Input rank should be 3 if Conv2D blocks, first 2 dimensions of input_shape should be a multiple of 2^len(stack).
   Input rank should be 1 if only a Dense block.
"""

from inspect import isfunction
from math import prod as _prod
from sys import exit
from tensorflow.keras import layers, Input
from tensorflow.keras.models import Model
from diresa.layers import DistLayer


def autoencoder_model(x, encoder, decoder):
    """
    Creates autoencoder model out of an encoder and a decoder model
    
    :param x: keras input tensor (keras.Input())
    :param encoder: encoder functional Keras model
    :param decoder: decoder functional Keras model
    :return: autoencoder model
    """
    y = encoder(x)
    y = decoder(y)
    return Model(x, y)


def diresa_model(x, x_twin, encoder, decoder, dist_layer=DistLayer()):
    """
    Creates a Diresa model out of an encoder and a decoder model
    
    :param x: keras input tensor (keras.Input())
    :param x_twin: keras input tensor for shuffled input
    :param encoder: encoder functional Keras model
    :param decoder: decoder functional Keras model
    :param dist_layer: distance layer to be used
    :return: Diresa model
    """
    latent_orig = encoder(x)
    latent_twin = encoder(x_twin)
    dist = dist_layer(x, x_twin, latent_orig, latent_twin)
    latent = layers.Flatten(name="Cov")(latent_orig)
    output = decoder(latent_orig)
    return Model((x, x_twin), (output, latent, dist))


def build_ae(input_shape=(),
             stack=(),
             stack_filters=(),
             latent_filters=1,
             kernel_size=(3, 3),
             conv_transpose=False,
             up_first=False,
             attention=False,
             residual=False,
             dropout_rate=0,
             dense_units=(),
             activation='relu',
             activation_layer_param=None,
             encoder_activation='linear',
             decoder_activation='linear',
             **kwargs,
             ):
    """
    Creates an AE model out of hyperparameters
    
    :param input_shape: rank 3 with Conv2D layers, first 2 dims should be a multiple of 2^len(stack); rank 1 if only Dense layers
    :param stack: elements are nbr of Conv2D or residual units in a block
    :param stack_filters: elements are nbr of filters in a block
    :param latent_filters: nbr of filters in convolutional output (only used if no dense units)
    :param kernel_size: kernel size for convolution
    :param conv_transpose: if True ConvTranspose is used in decoder, only possible for up_first=True
    :param up_first: if True UpSampling is first in decoder block, if False UpSampling is second
    :param attention: if True, attention layer is added after last Conv2D layer in block
    :param residual: if True, elements in blocks are residual units, if False elements are Conv2D layers
    :param dense_units: elements are nbr of nodes of a Dense layer in the dense block
    :param dropout_rate: if dropout_rate!=0, Dropout(dropout_rate) is added between Dense units, only if len(dense_units)>0
    :param activation: activation function or layer used (except for output of encoder/decoder)
    :param activation_layer_param: parameters for activation layer (dictionary)
    :param encoder_activation: activation function used for output of encoder
    :param decoder_activation: activation function used for output of decoder
    :param kwargs: are passed to all Conv2D and Dense layers, e.g. can be used for changing kernel_initializer, kernel_regularizer
    :return: AE functional Keras model
    """

    activation, activation_layer = _activation(activation)
    if type(attention) is bool:
        if attention:
            attention = [True] * len(stack)
        else:
            attention = [False] * len(stack)
    encoder, decoder = _encoder_decoder_model(input_shape=input_shape,
                                              stack=stack,
                                              stack_filters=stack_filters,
                                              latent_filters=latent_filters,
                                              kernel_size=kernel_size,
                                              conv_transpose=conv_transpose,
                                              up_first=up_first,
                                              attention=attention,
                                              residual=residual,
                                              dense_units=dense_units,
                                              dropout_rate=dropout_rate,
                                              activation=activation,
                                              activ_layer=activation_layer,
                                              activ_layer_param=activation_layer_param,
                                              encoder_activation=encoder_activation,
                                              decoder_activation=decoder_activation,
                                              **kwargs,
                                              )
    x = Input(shape=input_shape)
    return autoencoder_model(x, encoder, decoder)


def build_diresa(input_shape=(),
                 stack=(),
                 stack_filters=(),
                 latent_filters=1,
                 kernel_size=(3, 3),
                 conv_transpose=False,
                 up_first=False,
                 attention=False,
                 residual=False,
                 dropout_rate=0,
                 dense_units=(),
                 activation='relu',
                 activation_layer_param=None,
                 encoder_activation='linear',
                 decoder_activation='linear',
                 dist_layer=DistLayer(),
                 **kwargs,
                 ):
    """
    Creates a Diresa model out of hyperparameters
    
    :param input_shape: rank 3 with Conv2D layers, first 2 dims should be a multiple of 2^len(stack); rank 1 if only Dense layers
    :param stack: elements are nbr of Conv2D or residual units in a block
    :param stack_filters: elements are nbr of filters in a block
    :param latent_filters: nbr of filters in convolutional output (only used if no dense units)
    :param kernel_size: kernel size for convolution
    :param conv_transpose: if True ConvTranspose is used in decoder, only possible for up_first=True
    :param up_first: if True UpSampling is first in decoder block, if False UpSampling is second
    :param attention: if True, attention layer is added after last Conv2D layer in block
    :param residual: if True, elements in blocks are residual units, if False elements are Conv2D layers
    :param dense_units: elements are nbr of nodes of a Dense layer in the dense block
    :param dropout_rate: if dropout_rate!=0, Dropout(dropout_rate) is added between Dense units, only if len(dense_units)>0
    :param activation: activation function or layer used (except for output of encoder/decoder)
    :param activation_layer_param: parameters for activation layer
    :param encoder_activation: activation function used for output of encoder
    :param decoder_activation: activation function used for output of decoder
    :param dist_layer: distance layer to be used
    :param kwargs: are passed to all Conv2D and Dense layers, e.g. can be used for changing kernel_initializer, kernel_regularizer
    :return: Diresa functional Keras model
    """

    activation, activation_layer = _activation(activation)
    if type(attention) is bool:
        if attention:
            attention = [True] * len(stack)
        else:
            attention = [False] * len(stack)
    encoder, decoder = _encoder_decoder_model(input_shape=input_shape,
                                              stack=stack,
                                              stack_filters=stack_filters,
                                              latent_filters=latent_filters,
                                              kernel_size=kernel_size,
                                              conv_transpose=conv_transpose,
                                              up_first=up_first,
                                              attention=attention,
                                              residual=residual,
                                              dense_units=dense_units,
                                              dropout_rate=dropout_rate,
                                              activation=activation,
                                              activ_layer=activation_layer,
                                              activ_layer_param=activation_layer_param,
                                              encoder_activation=encoder_activation,
                                              decoder_activation=decoder_activation,
                                              **kwargs,
                                              )
    input_orig = Input(name="Input", shape=input_shape)
    input_twin = Input(name="Shuffled_Input", shape=input_shape)
    return diresa_model(input_orig, input_twin, encoder, decoder, dist_layer=dist_layer)


#
# Helper functions for creating the encoder and decoder models out of the hyperparameters
#
def _activation(activation):
    if isfunction(activation) or isinstance(activation, str):
        activation_layer = None
    elif issubclass(activation, layers.Layer):
        activation_layer = activation
        activation = None
    else:
        print("Activation should be a function, string or layer")
        exit(1)
    return activation, activation_layer


def _residual_unit(x, filters, kernel_size, activation, activ_layer, activ_layer_param, name, **kwargs):
    y = layers.Conv2D(filters, kernel_size, padding='same', name=name + '_A', **kwargs)(x)
    y = layers.BatchNormalization(name=name + '_BN_A')(y)
    if activ_layer is not None: y = activ_layer(**activ_layer_param)(y)
    if activation is not None: y = layers.Activation(activation)(y)
    y = layers.Conv2D(filters, kernel_size, padding='same', name=name + '_B', **kwargs)(y)
    y = layers.BatchNormalization(name=name + '_BN_B')(y)

    # If input has a  different nbr of filters
    if x.shape[-1] != filters:
        x = layers.Conv2D(filters, (1, 1), padding='same', name=name + '_C', **kwargs)(x)

    # Add skip connection
    y = layers.Add(name=name.replace("Conv2D", "Add"))([x, y])

    return layers.Activation(activation)(y)


def _attention_unit(x, channels, residual, name):
    # same linear transformation over channels for all grid points
    query = layers.Conv2D(channels, 1, name=name + 'Conv_q')(x)
    value = layers.Conv2D(channels, 1, name=name + 'Conv_v')(x)
    key = layers.Conv2D(channels, 1, name=name + 'Conv_k')(x)
    # flatten 2-dim grid
    query = layers.Reshape((-1, channels), name=name + '_q')(query)
    value = layers.Reshape((-1, channels), name=name + '_v')(value)
    key = layers.Reshape((-1, channels), name=name + '_k')(key)
    # dot-product attention over grid points: Tq = Tv = #gridpoints, dim = #channels
    y = layers.Attention(name=name)([query, value, key])
    # un-flatten grid
    y = layers.Reshape(x.shape[1:], name=name + '_out')(y)
    if residual:
        y = layers.Add(name=name.replace("Att", "Att_Add"))([x, y])
    return y


def _encoder_block(y, block, filters, kernel_size, attention, residual,
                   activation, activ_layer, activ_layer_param, name, **kwargs):
    # Block of num residual or Conv2D units followed by a MaxPooling2D layer
    for unit in range(block):
        if residual:
            y = _residual_unit(y, filters, kernel_size, activation=activation, activ_layer=activ_layer,
                               activ_layer_param=activ_layer_param, name=name + "_Conv2D_" + str(unit), **kwargs)
        else:
            y = layers.Conv2D(filters, kernel_size, activation=activation, padding='same',
                              name=name + "_Conv2D_" + str(unit), **kwargs)(y)
            if activ_layer is not None: y = activ_layer(**activ_layer_param)(y)
    if attention:
        y = _attention_unit(y, filters, residual=residual, name=name + "_Att")
    y = layers.MaxPooling2D((2, 2), padding='same', name=name + '_MaxPooling2D')(y)
    return y


def _decoder_block(y, block, filters, kernel_size, conv_transpose, attention, residual,
                   activation, activ_layer, activ_layer_param, up_first, name, **kwargs):
    if up_first:
        # Block of an UpSampling2D layer followed by num residual or Conv2D units
        y = layers.UpSampling2D((2, 2), name=name + '_UpSampling2D')(y)
        for unit in range(block):
            if residual:
                y = _residual_unit(y, filters, kernel_size, activation=activation, activ_layer=activ_layer,
                                   activ_layer_param=activ_layer_param, name=name + "_Conv2D_" + str(unit), **kwargs)
            elif conv_transpose:
                y = layers.Conv2DTranspose(filters, kernel_size, activation=activation, padding='same',
                                           name=name + "_Conv2DTranspose_" + str(unit), **kwargs)(y)
                if activ_layer is not None: y = activ_layer(**activ_layer_param)(y)
            else:
                y = layers.Conv2D(filters, kernel_size, activation=activation, padding='same',
                                  name=name + "_Conv2D_" + str(unit), **kwargs)(y)
                if activ_layer is not None: y = activ_layer(**activ_layer_param)(y)
    else:
        # Block of a Conv2D layer followed by an UpSampling2D layer followed by num-1 Conv2D layers
        if block > 0:
            y = layers.Conv2D(filters, kernel_size, activation=activation, padding='same',
                              name=name + '_Conv2D_0', **kwargs)(y)
            if activ_layer is not None: y = activ_layer(**activ_layer_param)(y)
        y = layers.UpSampling2D((2, 2), name=name + '_UpSampling2D')(y)
        for unit in range(1, block):
            y = layers.Conv2D(filters, kernel_size, activation=activation, padding='same',
                              name=name + '_Conv2D_' + str(unit), **kwargs)(y)
            if activ_layer is not None: y = activ_layer(**activ_layer_param)(y)
    if attention:
        y = _attention_unit(y, filters, residual=residual, name=name + "_Att")
    return y


def _encoder_model(input_shape, stack, stack_filters, latent_filters, kernel_size, conv_transpose, up_first, attention, residual,
                   dense_units, dropout_rate, activation, activ_layer, activ_layer_param, encoder_activation, **kwargs):
    x = Input(input_shape, name="Encoder_Input")
    y = x

    # Encoder blocks with Conv2D or residual units and a MaxPooling layer
    block_nr = 1
    for block, filters, att in zip(stack, stack_filters, attention):
        y = _encoder_block(y, block=block, filters=filters, kernel_size=kernel_size, attention=att, residual=residual,
                           activation=activation, activ_layer=activ_layer, activ_layer_param=activ_layer_param,
                           name='Enc_' + str(block_nr), **kwargs)
        block_nr += 1

    # Encoder dense layers
    if len(dense_units) != 0:
        if len(stack) > 0:
            y = layers.Flatten()(y)
        for layer, units in enumerate(dense_units):
            if layer != len(dense_units) - 1:
                y = layers.Dense(units, activation=activation,
                                 name='Enc_' + str(block_nr) + '_Dense_' + str(layer), **kwargs)(y)
                if activ_layer is not None: y = activ_layer(**activ_layer_param)(y)
                if dropout_rate != 0:
                    y = layers.Dropout(dropout_rate)(y)
            else:  # last layer has other activation
                y = layers.Dense(units, activation=encoder_activation, name='Dense_Latent', **kwargs)(y)
    # If no dense layers, last Conv2D layer
    else:
        y = layers.Conv2D(latent_filters, kernel_size, activation=encoder_activation, padding='same',
                          name='Enc_' + str(block_nr) + '_Conv2D_0', **kwargs)(y)
        y = layers.Flatten(name='Flatten_Latent')(y)

    model = Model(x, y, name="Encoder")
    return model


def _decoder_model(input_shape, stack, stack_filters, latent_filters, kernel_size, conv_transpose, up_first, attention, residual,
                   dense_units, dropout_rate, activation, activ_layer, activ_layer_param, decoder_activation, **kwargs):
    # Nbr of blocks in en/decoder
    block_nr = len(stack) + 1
    # Input shape of decoder
    comp_factor = 2 ** len(stack_filters)
    if len(dense_units) == 0 and len(stack) != 0:  # only convolutional layers
        conv_output_shape = (input_shape[0] // comp_factor, input_shape[1] // comp_factor, latent_filters)
        decoder_input_shape = (_prod(conv_output_shape),)
    elif len(stack) != 0:  # convolutional and dense layers
        decoder_input_shape = (dense_units[-1],)
        conv_output_shape = (input_shape[0] // comp_factor, input_shape[1] // comp_factor, stack_filters[-1])
    else:  # only dense layers
        decoder_input_shape = (dense_units[-1],)

    x = Input(shape=decoder_input_shape, name="Decoder_Input")
    y = x

    # Decoder dense layers
    if len(dense_units) != 0:
        if len(dense_units) > 1:
            for layer, units in enumerate(dense_units[-2::-1]):
                y = layers.Dense(units, activation=activation,
                                 name='Dec_' + str(block_nr) + '_Dense_' + str(len(dense_units) - layer - 1), **kwargs)(y)
                if activ_layer is not None: y = activ_layer(**activ_layer_param)(y)
                if dropout_rate != 0:
                    y = layers.Dropout(dropout_rate)(y)
        if len(stack) != 0:
            # Last dense layer units should match conv layer
            y = layers.Dense(_prod(conv_output_shape), activation=activation,
                             name='Dec_' + str(block_nr) + '_Dense_0', **kwargs)(y)
            if activ_layer is not None: y = activ_layer(**activ_layer_param)(y)
            # Shape of encoder output after convolution
            y = layers.Reshape(conv_output_shape)(y)
        else:
            # Last dense layer if no conv layers
            y = layers.Dense(input_shape[0], activation=decoder_activation, name='Dec_' + str(block_nr) + '_Dense_0', **kwargs)(y)
        block_nr -= 1
    else:
        y = layers.Reshape(conv_output_shape)(y)

    # Decoder blocks with Conv2D layers or residual elements and an UpSampling layer
    for block, filters, att in zip(stack[::-1], stack_filters[::-1], attention[::-1]):
        if len(dense_units) != 0 and block_nr == len(stack):
            # Fist block has 1 conv layer less in case of a dense block
            y = _decoder_block(y, block=block - 1, filters=filters, conv_transpose=conv_transpose, kernel_size=kernel_size,
                               attention=att, residual=residual, activation=activation, activ_layer=activ_layer,
                               activ_layer_param=activ_layer_param, up_first=up_first, name='Dec_' + str(block_nr), **kwargs)
        else:
            y = _decoder_block(y, block=block, filters=filters, conv_transpose=conv_transpose, kernel_size=kernel_size,
                               attention=att, residual=residual, activation=activation, activ_layer=activ_layer,
                               activ_layer_param=activ_layer_param, up_first=up_first, name='Dec_' + str(block_nr), **kwargs)
        block_nr -= 1

    # Last Conv2D layer
    if len(stack) != 0:
        y = layers.Conv2D(input_shape[-1], kernel_size, activation=decoder_activation, padding='same',
                          name='Dec_' + str(block_nr) + '_Conv2D_0', **kwargs)(y)

    model = Model(x, y, name="Recon")
    return model


def _encoder_decoder_model(input_shape, stack, stack_filters, latent_filters, kernel_size, conv_transpose, up_first, attention,
                           residual, dense_units, dropout_rate, activation, activ_layer, activ_layer_param, encoder_activation,
                           decoder_activation, **kwargs):
    if len(stack) == 0 and len(dense_units) == 0:
        print("You should have minimum 1 convolutional or 1 dense layer")
        exit(1)
    if len(stack) > 1 and len(input_shape) != 3:
        print("Length input_shape should be 3 with convolutional layers")
        exit(1)
    if len(stack) == 0 and len(input_shape) != 1:
        print("Length input_shape should be 1 if only dense layers")
        exit(1)
    if len(stack) != len(stack_filters):
        print("stack and stack_filters should have the same length")
        exit(1)
    if len(stack) != len(attention):
        print("stack and attention should have the same length")
        exit(1)
    if len(stack) > 1 and input_shape[0] % (2 ** len(stack)) != 0:
        print("input_shape[0] should be a multiple of 2^len(stack)")
        exit(1)
    if len(stack) > 1 and input_shape[1] % (2 ** len(stack)) != 0:
        print("input_shape[1] should be a multiple of 2^len(stack)")
        exit(1)
    if not up_first and residual:
        print("Residual only possible with UpSampling layer first in decoder")
        exit(1)
    if residual and conv_transpose:
        print("Residual not possible with Conv2DTranspose layer in decoder")
        exit(1)
    if not up_first and conv_transpose:
        print("Transposed convolution only possible with UpSampling layer first in decoder")
        exit(1)
    if dropout_rate != 0 and len(dense_units) < 2:
        print("Dropout only possible if more than 1 dense layer")
        exit(1)

    encoder = _encoder_model(input_shape=input_shape, stack=stack, stack_filters=stack_filters, latent_filters=latent_filters,
                             kernel_size=kernel_size, conv_transpose=conv_transpose, up_first=up_first, attention=attention,
                             residual=residual, dense_units=dense_units, dropout_rate=dropout_rate, activation=activation,
                             activ_layer=activ_layer, activ_layer_param=activ_layer_param, encoder_activation=encoder_activation,
                             **kwargs)
    decoder = _decoder_model(input_shape=input_shape, stack=stack, stack_filters=stack_filters, latent_filters=latent_filters,
                             kernel_size=kernel_size, conv_transpose=conv_transpose, up_first=up_first, attention=attention,
                             residual=residual, dense_units=dense_units, dropout_rate=dropout_rate, activation=activation,
                             activ_layer=activ_layer, activ_layer_param=activ_layer_param, decoder_activation=decoder_activation,
                             **kwargs)
    return encoder, decoder
