Command Line Usage
------------------

Annotating Enums
~~~~~~~~~~~~~~~~

This toolkit allows automated annotation of LinkML enums, mapping text
strings to ontology terms.

The command line tool ``annotate-enums`` takes a LinkML schema, with
enums and fills in the ``meaning`` slots.

See the `annotators <schema_automator/annotators/>`__ folder for docs

Converting TSVs
~~~~~~~~~~~~~~~

The ``tsv2linkml`` command infers a single-class schema from a TSV
datafile

.. code:: bash

   tsv2linkml --help
   Usage: tsv2linkml [OPTIONS] TSVFILE

     Infer a model from a TSV

   Options:
     -o, --output TEXT        Output file
     -c, --class_name TEXT    Core class name in schema
     -n, --schema_name TEXT   Schema name
     -s, --sep TEXT           separator
     -E, --enum-columns TEXT  column that is forced to be an enum
     --robot / --no-robot     set if the TSV is a ROBOT template
     --help                   Show this message and exit.

Example:

.. code:: bash

   tsv2linkml tests/resources/biobank-specimens.tsv 

The ``tsvs2linkml`` command infers a multi-class schema from multiple
TSV datafiles

.. code:: bash

   tsvs2linkml --help
   Usage: tsvs2linkml [OPTIONS] [TSVFILES]...

     Infer a model from multiple TSVs

   Options:
     -o, --output TEXT         Output file
     -n, --schema_name TEXT    Schema name
     -s, --sep TEXT            separator
     -E, --enum-columns TEXT   column(s) that is forced to be an enum
     --enum-mask-columns TEXT  column(s) that are excluded from being enums
     --max-enum-size INTEGER   do not create an enum if more than max distinct
                               members

     --enum-threshold FLOAT    if the number of distinct values / rows is less
                               than this, do not make an enum

     --robot / --no-robot      set if the TSV is a ROBOT template
     --help                    Show this message and exit.

Converting OWL
~~~~~~~~~~~~~~

.. code:: bash

   owl2linkml --help
   Usage: owl2linkml [OPTIONS] OWLFILE

     Infer a model from OWL Ontology

     Note: input must be in functional syntax

   Options:
     -n, --name TEXT  Schema name
     --help           Show this message and exit.

Example:

.. code:: bash

   owl2linkml -n prov tests/resources/prov.ofn > prov.yaml

Note this works best on schema-style ontologies such as Prov

**NOT** recommended for terminological-style ontologies such as OBO

Converting RDF instance graphs
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code:: bash

   rdf2linkml --help
   Usage: rdf2linkml [OPTIONS] RDFFILE

     Infer a model from RDF instance data

   Options:
     -d, --dir TEXT  [required]
     --help          Show this message and exit.

Converting JSON Instance Data
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code:: bash

   jsondata2linkml --help
   Usage: jsondata2linkml [OPTIONS] INPUT

     Infer a model from JSON instance data



   Options:
     --container-class-name TEXT   name of root class
     -f, --format TEXT             json or yaml (or json.gz or yaml.gz)
     --omit-null / --no-omit-null  if true, ignore null values
     --help                        Show this message and exit.

Converting JSON-Schema
~~~~~~~~~~~~~~~~~~~~~~

.. code:: bash

   jsonschema2linkml --help
   Usage: jsonschema2linkml [OPTIONS] INPUT

     Infer a model from JSON Schema

   Options:
     -n, --name TEXT    ID of schema  [required]
     -f, --format TEXT  JSON Schema format - yaml or json
     -o, --output TEXT  output path
     --help             Show this message and exit.

jsonschema2linkml example
~~~~~~~~~~~~~~~~~~~~~~~~~

.. code:: bash

   poetry run jsonschema2linkml -n test-model -f yaml -o vrs-linkml.yaml cp tests/resources/jsonschema/vrs.schema.json