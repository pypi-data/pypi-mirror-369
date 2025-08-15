#!/usr/bin/env python3
"""
DIRESA helper functions

:Author:  Geert De Paepe
:Email:   geert.de.paepe@vub.be
:License: MIT License
"""

from sys import exit
import tensorflow as tf
from tensorflow.keras import Input
from tensorflow.keras.models import Model
from diresa.layers import OrderLayer


def _covariance(x):
    """
    Computes the covariance matrix of x (normalisation is divided by N)

    :param x: 2-D array, row are variables, columns are samples
    :return: covariance matrix
    """
    mean_x = tf.expand_dims(tf.reduce_mean(x, axis=0), 0)
    mx = tf.matmul(tf.transpose(mean_x), mean_x)
    vx = tf.matmul(tf.transpose(x), x)/tf.cast(tf.shape(x)[0], tf.float32)
    cov_xx = vx - mx
    return cov_xx


def _r2_score(y, y_pred):
    """
    :param y: original dataset
    :param y_pred: predicted dataset
    :return: R2 score between y and y_pred
    """
    error = tf.math.reduce_sum(tf.math.square(y - y_pred))
    var = tf.math.reduce_sum(tf.math.square(y - tf.math.reduce_mean(y, axis=0)))
    r2 = 1.0 - error / var
    return r2.numpy()


def _set_components_to_mean(latent, retain=(0,)):
    """
    Sets all latent components to mean except the ones in the list (which are kept untouched)
    Limitations: assumes a flat latent space (rank of latent is 2)

    :param latent: latent dataset
    :param retain: components not in this list are set to mean
    :return: latent dataset with all components set to mean except the ones in the list
    """
    mean_values = tf.reduce_mean(latent, axis=0)
    mask = tf.constant([i not in retain for i in range(latent.shape[1])], dtype=tf.bool)
    latent = tf.where(mask, mean_values, latent)
    return latent


def cut_sub_model(model, sub_model_name):
    """
    Cuts a sub-model out of a keras model 
    Limitations: does not work for a sub-model of a sub-model

    :param model: keras model
    :param sub_model_name: name of the sub-model
    :return: submodel
    """
    sub_model_nbr = None
    sub_model_config = None

    for nbr, layer in enumerate(model.get_config()['layers']):
        if layer['name'] == sub_model_name:
            sub_model_config = layer['config']
            sub_model_nbr = nbr

    if sub_model_config is None:
        print(sub_model_name, " not found in model")
        exit(1)

    sub_model = Model.from_config(sub_model_config)
    weights = [layer.get_weights() for layer in model.layers[sub_model_nbr].layers[1:]]

    for layer, weight in zip(sub_model.layers[1:], weights):
        layer.set_weights(weight)

    return sub_model


def latent_component_r2_scores(dataset, latent, decoder, cumulated=False):
    """
    Calculate R2 score of latent components

    :param dataset: dataset
    :param latent: latent (encoded) dataset
    :param decoder: decoder model
    :param cumulated: if True, cumulated R2 score is calculated (assumes that latent components are ordered!)
    :return: list with R2 scores of latent components
    """
    latent_dim = latent.shape[1]
    score = []
    for component in range(latent_dim):
        if not cumulated:
            retain_list = [component,]
        else:
            retain_list = list(range(0, component + 1))
        latent_component = _set_components_to_mean(latent, retain=retain_list)
        decoded_component = decoder.predict(latent_component, verbose=0)
        score.append(_r2_score(dataset, decoded_component))
    return score


def _order_latent(dataset, latent, decoder, verbose=False):
    """
    Orders latent components by R2 score

    :param dataset: dataset
    :param latent: latent (encoded) dataset
    :param decoder: decoder model
    :param verbose: if True, prints rankings
    :return: ranking and reverse ranking of latent components, ordered R2 scores
    """
    score = latent_component_r2_scores(dataset, latent, decoder)
    ranking = sorted(range(len(score)), key=score.__getitem__, reverse=True)
    reverse_ranking = sorted(range(len(ranking)), key=ranking.__getitem__)
    ordered_score = [score[i] for i in ranking]
    if verbose:
        print("Ranking:", ranking)
        print("Reverse ranking:", reverse_ranking)
    return ranking, reverse_ranking, ordered_score


def encoder_decoder(model, dataset=None, encoder_name="Encoder", decoder_name="Recon", verbose=True):
    """
    Returns encoder and decoder out of DIRESA model
    If dataset is not None: adds ordering layers after encoder and before decoder

    :param model: keras model
    :param dataset: dataset
    :param encoder_name: name of the encoder
    :param decoder_name: name of the decoder
    :param verbose: if True, prints R2 score
    :return: encoder and decoder model
    """
    encoder = cut_sub_model(model, encoder_name)
    decoder = cut_sub_model(model, decoder_name)

    if dataset is not None:
        # Calculate latent dataset
        latent = encoder.predict(dataset, verbose=0)
        latent_dim = latent.shape[1]

        # Calculate order of latent components by R2 score
        order, reverse_order, r2 = _order_latent(dataset, latent, decoder)

        # Add order layer as last layer to encoder
        order_layer = OrderLayer(name="Order", order=order)
        encoder = Model(inputs=encoder.inputs, outputs=order_layer(encoder.layers[-1].output))

        # Insert reverse order layer as first layer to decoder
        reverse_order_layer = OrderLayer(name="ReverseOrder", order=reverse_order)
        decoder_input = Input(name="Ordered_Decoder_input", shape=(latent_dim,))
        decoder = Model(inputs=decoder_input, outputs=decoder(reverse_order_layer(decoder_input)))

        if verbose:
            print("\nR2 score:", r2)
            ordered_latent = order_layer(latent)
            cumul_score = latent_component_r2_scores(dataset, ordered_latent, decoder, cumulated=True)
            print("Cumulated R2 score:", cumul_score)
            print("\n")

    return encoder, decoder


def decoded_latent_components(latent, decode, factor=0.5):
    """
    :param latent: latent dataset
    :param decode: decoder model
    :param factor: factor to multiply with standard deviation
    :return: decoded latent components
    """
    mean_values = tf.reduce_mean(latent, axis=0)
    std_dev = tf.math.reduce_std(latent, axis=0)

    # Update the specific component
    latent_plus = tf.stack([tf.tensor_scatter_nd_update(mean_values, [[i]], [mean_values[i] + factor * std_dev[i]])
                            for i in range(mean_values.shape[0])])
    latent_minus = tf.stack([tf.tensor_scatter_nd_update(mean_values, [[i]], [mean_values[i] - factor * std_dev[i]])
                             for i in range(mean_values.shape[0])])

    components = decode.predict(latent_plus, verbose=0) - decode.predict(latent_minus, verbose=0)
    return components


def set_encoder_trainable(model, trainable=True, encoder_name="Encoder"):
    """
    Set trainable attribute of encoder

    :param model: keras DIRESA/AE model
    :param trainable: True or False
    :param encoder_name: name of the encoder
    """
    for layer in model.layers:
        if layer.name == encoder_name:
            layer.trainable = trainable
