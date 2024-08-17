LinkML Schema Automator
=======================

Schema Automator is a toolkit for bootstrapping and automatically enhancing schemas from a variety of sources.

The project is open source (BSD 3-clause license) and hosted on `GitHub <https://github.com/linkml/schema-automator>`_.

Use cases include:

1. Inferring an initial schema or data dictionary from a dataset that is a collection of TSVs
2. Automatically annotating schema elements and enumerations using the BioPortal annotator
3. Importing from a language like RDFS/OWL/SQL

The primary output of Schema Automator is a `LinkML Schema <https://linkml.io/linkml>`_. This can be converted to other
schema frameworks, including:

* JSON-Schema
* SQL DDL
* SHACL
* ShEx
* RDFS/OWL
* Python dataclasses or Pydantic

.. toctree::
   :maxdepth: 3
   :caption: Contents:

   introduction
   install
   cli
   packages/index
   metamodels/index


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
