.. _build:

*DIRESA* model
==============

**3. Build DIRESA model**

We can build a *DIRESA* model with convolutional, attention and/or dense layers with the *build_diresa* function.
We can also build a *DIRESA* model based on a custom encoder and decoder with the *diresa_model* function (see below). 
We build here a model with an input shape of *(3,)* for the 3D butterfly points. 
Our encoder model has 3 dense layers with 40, 20 and 2 units (the latter is the dimension of the latent space). 
The decoder is a reflection of the encoder. The DIRESA model has 3 loss functions, 
the reconstruction loss (the MSE is used here), the covariance loss and a distance loss
(here the MSE distance loss is used). Also the weights for the different loss functions are specified.

.. code-block:: ipython
  
  from diresa.models import build_diresa
  from diresa.loss import mse_dist_loss, LatentCovLoss

  diresa = build_diresa(input_shape=(3,), dense_units=(40, 20, 2))

  diresa.compile(loss=['MSE', LatentCovLoss(), mse_dist_loss],
                 loss_weights=[1., 3., 1.5],
                 optimizer="adam",
                 )

In order to lower the loss weight tuning effort, we will use annealing for the covariance loss. In this case, 
the covariance weight starts from an initial value (here the keras backend variable *cov_weight* is initialized to 0.) 
and is increased until the covariance loss reaches a certain target.

.. code-block:: ipython
  
  import keras.backend as K
  from diresa.callback import LossWeightAnnealing

  cov_weight = K.variable(0.)
  diresa.compile(loss=['MSE', LatentCovLoss(cov_weight), mse_dist_loss],
                 loss_weights=[1., 1., 1.],
                 optimizer="adam",
                 )
  diresa.summary(expand_nested=True)
  
**4. Train the DIRESA model**

We train the *DIRESA* model in a standard way. The model is fit with 2 inputs: the original dataset and the shuffled dataset.
There are 3 outputs: the original dataset for the reconstruction loss; the 2 last outputs are not used, but are needed in Keras 3.
The batch size should be large enough for the calculation of the covariance loss, which calculates 
the covariance matrix of the latent space components over the batch.
In the *LossWeightAnnealing* callback, we specify the target (*target_loss*) for the mean squared covariance 
between the latent components. Also the step size by which the annealing weight factor is increased (*anneal_step*) 
and epoch from which annealing is started (*start_epoch*) is specified. If annealing is not used, 
the fit method is called without callback function.

.. code-block:: ipython
  
  callback = [LossWeightAnnealing(cov_weight, target_loss=0.0001, anneal_step=0.2, start_epoch=3)]
  diresa.fit((train, train_twin), (train, train, train),
             validation_data=((val, val_twin), (val, val, val)),
             epochs=20, batch_size=512, shuffle=True, verbose=2, callbacks=callback)
  
**5. Encoder and decoder submodel**

We cut out the encoder and decoder submodels with the *encoder_decoder* function.
If a dataset is given, the R2-scores of the individual latent components are calculated and a ranking layer,
which orders the latent components based on the R2-scores, is added to the submodels.

.. code-block:: ipython
  
  from diresa.toolbox import encoder_decoder
  compress_model, decode_model = encoder_decoder(diresa, dataset=val)
  latent = compress_model.predict(val)
  predict = decode_model.predict(latent)