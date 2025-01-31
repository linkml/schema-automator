Importers
=========

Importers take either a representation of a schema in a different language or example data and bootstraps a schema.

Importers are the opposite of `Generators <https://linkml.io/linkml/generators/index.html>`_ in the core LinkML framework

.. warning::

   Generally importers take a *less expressive* language than LinkML and attempts to create the corresponding
   LinkML schema. This may be less optimal than a hand-crafted schema. For example, when converting to a
   representation that lacks `inheritance <https://linkml.io/linkml/schemas/inheritance.html>`_, no ``is_a`` slots
   will be created.

Importing from JSON-Schema
--------------------------

The ``import-json-schema`` command can be used:

.. code-block::

    schemauto import-json-schema tests/resources/model_card.schema.json

Importing from Kwalify
----------------------

The ``import-kwalify`` command can be used:

.. code-block::

    schemauto import-kwalify tests/resources/test.kwalify.yaml

Importing from OWL
------------------

You can import from a schema-style OWL ontology. This must be in functional syntax

Use robot to convert ahead of time:

.. code-block::

    robot convert -i schemaorg.ttl -o schemaorg.ofn
    schemauto import-owl schemaorg.ofn

Importing from SQL
------------------

You can import a schema from a SQL database

The default is to assume a SQLite database:

.. code-block::

    schemauto import-sql path/to/my.db

You can also connect to any database server provided you have the necessary client software
installed, using a SQL Alchemy connection path.

For example, for the `RNA Central public database <https://rnacentral.org/help/public-database>`_

.. code-block::

    schemauto import-sql postgresql+psycopg2://reader:NWDMCE5xdipIjRrp@hh-pgsql-public.ebi.ac.uk:5432/pfmegrnargs

Importing from caDSR
--------------------

caDSR is an ISO-11179 compliant metadata registry. The ISO-11179 conceptual model can be mapped to LinkML. The
canonical mapping maps a CDE onto a LinkML *slot*.

See `this entry in LinkML FAQ <https://linkml.io/linkml/faq/why-linkml.html#why-should-i-use-linkml-over-iso-11179>`_.

NCI implements a JSON serialization of ISO-11197. You can import this JSON and convert to LinkML:

.. code-block::

    schemauto import-cadsr "cdes/*.json"


Importing from DBML
--------------------

DBML is a simple DSL for defining database schemas. It is a subset of SQL DDL.



Packages for importing
----------------------  

.. currentmodule:: schema_automator.importers

.. autoclass:: JsonSchemaImportEngine
    :members:

.. autoclass:: OwlImportEngine
    :members:

.. autoclass:: FrictionlessImportEngine
    :members:

.. autoclass:: DOSDPImportEngine
    :members:

.. autoclass:: CADSRImportEngine
    :members: