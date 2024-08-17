Introduction
============

This is a toolkit that assists with generating and enhancing schemas and data models from a variety
of sources.

The primary end target is a `LinkML <https://linkml.io>`_ schema, but the framework can be used
to generate JSON-Schema, SHACL, SQL DDL etc via the `LinkML Generator <https://linkml.io/linkml/generators>`_ framework.

All functionality is available via a :ref:`CLI <cli>`. In future there will be a web-based interface.
The functionality is also available by using the relevant Python :ref:`packages`.

Generalization from Instance Data
---------------------------------

See :ref:`generalizers`

Generalizers allow you to *bootstrap* a schema by generalizing from existing data files

* TSVs and spreadsheets
* SQLite databases
* RDF instance graphs

Importing from alternative modeling frameworks
----------------------------------------------

See :ref:`importers`

* OWL (but this only works for schema-style OWL)
* JSON-Schema
* SQL DDL

In future other frameworks will be supported

Annotating schemas
------------------

See :ref:`annotators`

Annotators to provide ways to automatically add metadata to your schema, including

* Assigning class or slot URIs to schema elements
* Mapping enums to ontologies and vocabularies
* Annotate using Large Language Models (LLMs)

General Utilities
-----------------

See :ref:`utilities`

