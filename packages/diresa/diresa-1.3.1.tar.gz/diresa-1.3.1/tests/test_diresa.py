#!/usr/bin/env python3
"""
:Author:  Geert De Paepe
:Email:   geert.de.paepe@vub.be
:License: MIT License
"""

import numpy as np
from diresa.models import build_diresa
from diresa.loss import mse_dist_loss, LatentCovLoss
from diresa.layers import DistLayer
from tensorflow.keras import backend as K
from diresa.callback import LossWeightAnnealing
from diresa.toolbox import encoder_decoder, cut_sub_model, decoded_latent_components
from tensorflow.keras.models import load_model
from tensorflow.keras.regularizers import L2


def load_dataset():
    data_file = "docs/lorenz.csv"
    data = np.loadtxt(data_file, delimiter=",")
    train = data[:5000]
    val = data[5000:6000]
    id_train = np.argsort((np.random.random(train.shape[0])))
    id_val = np.argsort((np.random.random(val.shape[0])))
    train_twin = train[id_train]
    val_twin = val[id_val]
    return train, train_twin, val, val_twin


def test_diresa():
    train, train_twin, val, val_twin = load_dataset()

    # build the model
    diresa = build_diresa(input_shape=(3,), dense_units=(40, 20, 2))
    diresa.compile(loss=['MSE', LatentCovLoss(), mse_dist_loss], loss_weights=[1., 1., 1.5])

    # train the model
    diresa.fit((train, train_twin), (train, train, train),
               validation_data=((val, val_twin), (val, val, val)),
               epochs=5, batch_size=512, shuffle=True, verbose=2)

    # encoder submodel
    cut_sub_model(diresa, 'Recon')

    # save and open model
    diresa.save('diresa.keras')
    load_model('diresa.keras')


def test_annealing_diresa():
    train, train_twin, val, val_twin = load_dataset()

    # build the model
    diresa = build_diresa(input_shape=(3,), dense_units=(40, 20, 2),
                          kernel_initializer="he_normal", kernel_regularizer=L2(1e-4),
                          dist_layer=DistLayer(dim_less=True))
    cov_weight = K.variable(0.)
    diresa.compile(loss=['MSE', LatentCovLoss(cov_weight), mse_dist_loss], loss_weights=[1., 1., 1.], optimizer="adam")

    # train the model
    callback = [LossWeightAnnealing(cov_weight, target_loss=0.0001, anneal_step=0.2,
                                    start_epoch=3)]
    diresa.fit((train, train_twin), (train, train, train),
               validation_data=((val, val_twin), (val, val, val)),
               epochs=5, batch_size=512, shuffle=True, verbose=2, callbacks=callback)

    # decoder and decoder submodel
    encoder, decoder = encoder_decoder(model=diresa, dataset=val)
    encoder.summary(expand_nested=True)
    decoder.summary(expand_nested=True)

    # decoded latent components
    latent = encoder.predict(val, verbose=0)
    decoded_latent_components(latent, decoder)


if __name__ == "__main__":
    test_diresa()
