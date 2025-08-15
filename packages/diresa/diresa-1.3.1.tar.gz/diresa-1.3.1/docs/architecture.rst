.. _architecture:

*DIRESA* architecture
=====================

**Introduction**

*DIRESA* is a non-linear dimension reduction technique which fulfills the following requirements:

#. Decoded latent dataset is as close as possible to original dataset.
#. Distance (ordering) in real space is preserved in latent space.
#. Latent components are independent.
#. latent components are ordered by importance (R2-score).

.. image:: images/diresa_requirements.jpg
   :width: 75%

The fourth requirement is not enforced during training, but done afterwards.
The R2-scores of the individual latent components are calculated and a ranking layer,
which orders the latent components based on the R2-scores, is added to the encoder and decoder submodels.

**Architecture**

*DIRESA* is a Siamese twin autoencoder. The original dataset is fed in one encoder branch, while the
other is provided with a shuffled dataset. The two encoder branches share the weights and produce two different latent
space representations. These are used for the distance loss term, with the goal that the distance
between samples in the dataset be reflected (preserved or correlated) in the distance between
latent representations of those samples. Different distance loss functions are implemented, these can be found in the :doc:`loss`. 

.. image:: images/diresa_architecture.jpg
   :width: 75%

The total loss is the sum of the reconstruction loss, the covariance loss (multiplied by a weight factor) and the distance 
loss (multiplied by a weight factor). To lower the hyperparameter tuning effort, an annealing method is foreseen for the covariance
loss weight factor.

