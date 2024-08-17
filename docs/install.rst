Installation
============

Direct Installation
-------------------

``schema-automator`` and its components require Python 3.9 or greater.

.. code:: bash

   pip install schema-automator

To check this works:

.. code:: bash

   schemauto --help

Running via Docker
------------------

You can use the `Schema Automator Docker Container <https://hub.docker.com/r/linkml/schema-automator>`_

To start a shell

.. code:: bash

    docker run  -v $PWD:/work -w /work -ti linkml/schema-automator

Within the shell you should see all your files, and you should have access:

.. code:: bash

   schemauto --help
