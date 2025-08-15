.. _custom:

Custom encoder/decoder
======================

**9. Build DIRESA with custom encoder and decoder**

We can also build *DIRESA* models with custom encoder and decoder (reconstruction) models.
We define those two here.

.. code-block:: ipython
  
  from keras import layers, Input
  from keras.models import Model
  def encoder_model(input_shape=(3,), output_shape=2, units=40):
      x = Input(shape=input_shape)
      y = layers.Dense(units=units, activation="relu")(x)
      y = layers.Dense(units=units // 2, activation="relu")(y)
      y = layers.Dense(output_shape, activation="linear")(y)
      model = Model(x, y, name="Encoder")
      return model
  def decoder_model(input_shape=2, output_shape=3, units=40):
      x = Input(shape=input_shape)
      y = layers.Dense(units=units // 2, activation="relu")(x)
      y = layers.Dense(units=units, activation="relu")(y)
      y = layers.Dense(output_shape, activation="linear")(y)
      model = Model(x, y, name="Recon")
      return model
	  
Based on the custom encoder and decoder model, we now build the *DIRESA* 
model with the *diresa_model* function.

.. code-block:: ipython
  
  from diresa.models import diresa_model
  from diresa.loss import mse_dist_loss, LatentCovLoss

  diresa = diresa_model(x=Input(shape=3),
                        x_twin=Input(shape=3),
                        encoder=encoder_model(),
                        decoder=decoder_model(),
                        )

  diresa.compile(loss=['MSE', LatentCovLoss(1.), mse_dist_loss], loss_weights=[1., 3., 1.])
  diresa.summary(expand_nested=True)