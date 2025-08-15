.. _conv2D:

Convolution and attention
=========================

**8. A convolutional and attention example**

If your dataset consists of a number of variables (e.g. temperature and pressure, so 2 variables) over a 2 dimensional grid, 
convolutional layers can be used in the encoder/decoder. Here is an example for a grid (y, x) = (32, 64). 
The dataset would then have a shape of (nbr_of_samples, 32, 64, 2). We will use a stack of 3 convolutional/maxpooling blocks
in the encoder (the decoder mirrors the encoder). The first block uses 3 Conv2D layers, the second bock 2 and the third block 1, 
followed by a MaxPooling2D layer (*stack=(3, 2, 1)*). The number of filters in the first block is 32, in the second 16 and 
in the third 8 (*stack_filters=(32, 16, 8)*). The number of filters in Latent space, before flattening, is 1 (*latent_filters=1*). 
This will result in a latent shape (before flattening) of (4, 8, 1).

.. code-block:: ipython
  
  diresa = build_diresa(input_shape=(32, 64, 2),
                        stack=(3, 2, 1),
                        stack_filters=(32, 16, 8),
                        latent_filters=1,
                        )
  diresa.summary(expand_nested=True)

We can add an attention layer after the last convolutional layer in a block, to catch long distance relations.
Here we add an attention layer in the second and third block. After the convolutional/attention blocks,
2 dense layers are added, bringing the dimension of the latent space to 10.

.. code-block:: ipython

  diresa = build_diresa(input_shape=(32, 64, 2),
                        stack=(3, 2, 1),
                        stack_filters=(32, 16, 8),
                        attention=(False, True, True),
                        dense_units=(30, 10),
                        )
  diresa.summary(expand_nested=True)
	