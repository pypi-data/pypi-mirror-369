.. _eval:

Evaluate
========

**6. Show latent space**

We plot the 2D latent space.

.. code-block:: ipython
  
  import matplotlib.pyplot as plt
  plt.figure()
  plt.title("Latent space")
  plt.scatter(latent[:, 0], latent[:, 1], marker='.', s=0.1, color='C2')
  plt.show()

.. image:: images/latent.png
    :width: 50%
	
**7. Original versus decoded datset**

We compair the origonal dataset with the decoded one.

.. code-block:: ipython
  
  fig = plt.figure()
  ax = fig.add_subplot(projection='3d')
  ax.scatter(val[:, 0], val[:, 1], val[:, 2], marker='.', s=0.1)
  ax.scatter(predict[:, 0], predict[:, 1], predict[:, 2], marker='.', s=0.1, color='C1')
  plt.show()
  
.. image:: images/reconstruction.png
    :width: 50%
	