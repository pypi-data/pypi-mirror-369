Examples
========

End-to-end workflows are shown in the following set of tutorials:

.. toctree::
   :caption: Workflows
   :maxdepth: 2

   workflows/index

Further examples for the individual packages are available in these tutorials:

.. toctree::
   :caption: Packages
   :maxdepth: 2

   mammos-analysis/index
   mammos-dft/index
   mammos-entity/index
   mammos-mumag/index
   mammos-spindynamics/index
   mammos-units/index

.. _download-all-examples:

Downloading all examples
------------------------

To conveniently download all example notebooks use the ``mammos-fetch-examples``
script, which is installed as part of the ``mammos`` package. All notebooks are
written to a new `examples` directory with a subdirectory per package. The
command fails if a directory or file with the name `example` exists in the
current working directory.

Upon completion a list of downloaded examples is displayed:

.. code:: shell

   $ mammos-fetch-examples
   Downloading examples...
   The following examples have been downloaded:
   examples/mammos/hard-magnet-material-exploration.ipynb
   examples/mammos/hard-magnet-tutorial.ipynb
   examples/mammos/sensor.ipynb
   examples/mammos-analysis/quickstart.ipynb
   examples/mammos-dft/quickstart.ipynb
   examples/mammos-entity/quickstart.ipynb
   examples/mammos-entity/io.ipynb
   examples/mammos-mumag/quickstart.ipynb
   examples/mammos-spindynamics/quickstart.ipynb
   examples/mammos-units/example.ipynb
   examples/mammos-units/quickstart.ipynb
