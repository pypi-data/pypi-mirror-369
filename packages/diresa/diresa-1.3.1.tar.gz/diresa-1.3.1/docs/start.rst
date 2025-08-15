.. _start:

Start tutorial
==============

You can copy this tutorial in a Jupyter_ notebook or run it directly on |Colab|.

.. _Jupyter: https://jupyter.org

.. |Colab| image:: https://colab.research.google.com/assets/colab-badge.svg
   :target: https://colab.research.google.com/github/gdepaepe/diresa/blob/main/diresa.ipynb
   :alt: Colab
   :class: cmlbadge

**1. Install packages**

The *DIRESA* package depends on the tensorflow_ package. 
This tutorial also uses numpy_ and matplotlib_.

.. _tensorFlow: https://www.tensorflow.org
.. _numpy: https://numpy.org
.. _matplotlib: https://matplotlib.org

.. code-block:: ipython

  # Install needed packages
  !pip install numpy
  !pip install matplotlib
  !pip install tensorflow
  !pip install diresa

**2. Load the dataset**

In this tutorial, we are going to compress the 3D lorenz ‘63 butterfly into a 2D latent space. 
The lorenz.csv:_ contains a list of butterfly points, with three colums for the X, Y and Z coordinate. 
The *DIRESA* model has 2 inputs: the original dataset and a shuffled version of this dataset for the twin encoder.

.. _lorenz.csv: https://gitlab.com/etrovub/ai4wcm/public/diresa/-/raw/master/docs/lorenz.csv

.. code-block:: ipython

  !wget https://gitlab.com/etrovub/ai4wcm/public/diresa/-/raw/master/docs/lorenz.csv

.. code-block:: ipython
  
  import numpy as np
  data_file = "lorenz.csv"
  data = np.loadtxt(data_file, delimiter=",")
  print("Shape", data_file, ":", data.shape)
  train = data[:30000]
  val = data[30000:]
  id_train = np.argsort((np.random.random(train.shape[0])))
  id_val = np.argsort((np.random.random(val.shape[0])))
  train_twin = train[id_train]
  val_twin = val[id_val]