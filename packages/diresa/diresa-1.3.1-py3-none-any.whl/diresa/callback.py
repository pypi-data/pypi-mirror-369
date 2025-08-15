#!/usr/bin/env python3
"""
DIRESA callback classes/functions

:Author:  Geert De Paepe
:Email:   geert.de.paepe@vub.be
:License: MIT License
"""

from tensorflow.keras.backend import get_value, set_value
from tensorflow.keras.callbacks import Callback


class LossWeightAnnealing(Callback):
    """
    https://keras.io/guides/writing_your_own_callbacks/
    https://medium.com/dive-into-ml-ai/adaptive-weighing-of-loss-functions-for-multiple-output-keras-models-71a1b0aca66e
    """
    def __init__(self, weight, loss_name="val_Cov_loss", target_loss=0.000003, anneal_step=0.1, start_epoch=5):
        """
        :param weight: keras.backend.variable with initial loss weight
        :param loss_name: name of the loss function to apply the annealing
        :param target_loss: target loss, weight is increased until loss < target
        :param anneal_step: annealing step size for increasing weight
        :param start_epoch: epoch from which annealing starts
        """
        super().__init__()
        self.weight = weight
        self.loss_name = loss_name
        self.target_loss = target_loss
        self.anneal_step = anneal_step
        self.start_epoch = start_epoch
        self.stop_annealing = None

    def on_epoch_end(self, epoch, logs=None):
        """
        Executed during training on each epoch end
        Increases weight with anneal_step as from start_epoch until unweighted loss is smaller than target
        Prints loss weight, reconstruction loss and unweighted loss

        :param epoch: number of epoch
        :param logs: dict containing the loss values
        """
        weight = float(get_value(self.weight))
        if weight > 0.00001:
            unweighted_loss = logs[self.loss_name] / weight
        else:
            unweighted_loss = 1.
        if unweighted_loss < self.target_loss and self.stop_annealing is None:
            self.stop_annealing = epoch
        if (epoch + 2) >= self.start_epoch and self.stop_annealing is None:
            set_value(self.weight, weight + self.anneal_step)
        print("Covariance loss weight: {:g}, Validation Covariance loss (unweighted): {:g}."
              .format(weight, unweighted_loss))

    def on_epoch_begin(self, epoch, logs=None):
        """
        Divides learning rate by 2 every 10th epoch after annealing is stopped

        :param epoch: number of epoch
        :param logs: dict containing the loss values
        """
        if self.stop_annealing is not None:
            if epoch > self.stop_annealing + 10 and (epoch - self.stop_annealing) % 10 == 0:
                lr = float(get_value(self.model.optimizer.learning_rate))
                lr /= 2
                set_value(self.model.optimizer.lr, lr)
                print("\nEpoch %05d: Learning rate is %f" % (epoch, lr))
