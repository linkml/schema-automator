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

Importing from SHACL
--------------------

You can import from a SHACL shapes graph. SHACL expresses a data model the way
LinkML does -- classes with typed, cardinality-constrained slots -- so shapes map
onto classes and their ``sh:property`` shapes onto attributes.

.. code-block::

    schemauto import-shacl tests/resources/shacl_simple.ttl \
        --default-prefix usr --model-uri http://example.org/ -o user.yaml

Two conventions for relating shapes to classes are both supported, and the mode is
detected automatically.

*Explicit*, where a shape names the class it constrains. This is the style used by
DCAT-AP and by most hand-written shape files:

.. code-block:: turtle

    ex:UserShape a sh:NodeShape ; sh:targetClass ex:User ;
        sh:property [ sh:path schema:name ; sh:datatype xsd:string ] .

*Implicit*, where the shape is itself the class. This is the style used by large
published ontologies such as ASHRAE 223P and Brick, which declare a term
``rdfs:Class`` and ``sh:NodeShape`` at once and carry the hierarchy on
``rdfs:subClassOf``:

.. code-block:: turtle

    s223:Equipment a rdfs:Class, sh:NodeShape ;
        rdfs:subClassOf s223:Connectable ;
        sh:property [ sh:path s223:hasProperty ; sh:class s223:Property ] .

Options
^^^^^^^

``--default-prefix`` and ``--model-uri`` together say which namespace is the
schema's own. Terms from any other namespace are prefixed, so a vocabulary that
redeclares an imported name does not silently lose one of the two.

``--identifier`` adds an identifier slot to root classes. SHACL models no notion of
identity, so this is opt-in rather than assumed.

``--enum-root`` imports a subclass tree as enumerations. Some ontologies model
enumerations by punning class and instance -- a member is ``rdfs:subClassOf`` its
kind and typed as itself, never an ``rdf:type`` instance of the kind -- so
membership has to be read from the subclass closure:

.. code-block::

    schemauto import-shacl 223p.ttl --default-prefix s223 \
        --model-uri 'http://data.ashrae.org/standard223#' \
        --enum-root s223:EnumerationKind --identifier id -o s223.yaml

Limitations
^^^^^^^^^^^

``sh:sparql`` constraints, ``sh:severity`` and ``sh:message`` are not imported.
These are validation concerns with no LinkML equivalent, and a shape carrying only
``sh:sparql`` contributes neither a range nor a cardinality. Sequence and
alternative property paths are skipped for the same reason; ``sh:inversePath``
becomes an ``inverseOf_`` slot.


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