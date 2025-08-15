*DIRESA* - distance-regularized Siamese twin autoencoder
========================================================

 |test| |release| |python| |tensorflow| |mit|

.. |test| image:: https://gitlab.com/etrovub/ai4wcm/public/diresa/badges/master/pipeline.svg?ignore_skipped=true&key_text=test&key_width=35
.. |release| image:: https://gitlab.com/etrovub/ai4wcm/public/diresa/-/badges/release.svg?key_text=pypi&key_width=35
.. |python| image:: https://img.shields.io/badge/python-3.8%20|%203.9%20|%203.10%20|%203.11%20|%203.12-blue
.. |tensorflow| image:: https://img.shields.io/badge/tensorflow-2.12%20|%202.13%20|%202.14%20|%202.15%20|%202.16%20|%202.17%20|%202.18-orange
.. |mit| image:: https://img.shields.io/badge/license-MIT-yellow

*DIRESA* is a Python package for dimension reduction based on TensorFlow_.
The distance-regularized Siamese twin autoencoder architecture is designed
to preserve distance (ordering) in latent space while capturing the non-linearities in
the datasets.

.. _TensorFlow: https://www.tensorflow.org

**Introduction**

* :doc:`architecture`
* :doc:`install`

.. toctree::
   :maxdepth: 1
   :caption: Introduction:
   :hidden:
   
   architecture
   install
   
**Tutorial**
 
* :doc:`start`
* :doc:`build`
* :doc:`eval`
* :doc:`conv2D`
* :doc:`custom`

.. toctree::
   :maxdepth: 1
   :caption: Tutorial:
   :hidden:
   
   start
   build
   eval
   conv2D
   custom
   
**Module reference**

* :doc:`models`
* :doc:`loss`
* :doc:`layers`
* :doc:`callback`
* :doc:`tool`

.. toctree::
   :maxdepth: 1
   :caption: Module reference:
   :hidden:
   
   models
   loss
   layers
   callback
   tool

**Project links**

* `Paper <https://doi.org/10.1175/AIES-D-24-0034.1>`_
* `Code <https://gitlab.com/etrovub/ai4wcm/public/diresa>`_
* `Issues <https://gitlab.com/etrovub/ai4wcm/public/diresa/-/issues>`_

.. toctree::
   :maxdepth: 1
   :caption: Project links:
   :hidden:

   Paper <https://doi.org/10.1175/AIES-D-24-0034.1>
   Code <https://gitlab.com/etrovub/ai4wcm/public/diresa>
   Issues <https://gitlab.com/etrovub/ai4wcm/public/diresa/-/issues>
