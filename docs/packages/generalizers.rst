Generalizers
============

Generalizers take example data and *generalizes* to a schema

.. warning::

   Generalization is inherently a heuristic process, this should be viewed as a bootstrapping process
   that *semi*-automates the creation of a new schema for you.

Generalizing from a single TSV
------------------------------

.. code-block::

    schemauto  generalize-tsv tests/resources/NWT_wildfires_biophysical_2016.tsv -o wildfire.yaml

The schema will have a slot for every column, e,g:

.. code-block:: yaml

    classes:
      Observation:
        slots:
        - site
        - plot
        - plot_size
        - date
        - observer

Ranges will be auto-inferred, e.g.:

.. code-block:: yaml

    slots:
      site:
        examples:
        - value: ZF20-105
        range: string
      plot:
        examples:
        - value: '6'
        range: integer
      plot_size:
        examples:
        - value: 10X10
        range: plot_size_enum
      date:
        examples:
        - value: '2016-07-09'
        range: datetime

Enums will be automatically inferred:

.. code-block:: yaml

    enums:
      plot_size_enum:
        permissible_values:
          10X10:
            description: 10X10
          5x5:
            description: 5x5
          2.5X2.5:
            description: 2.5X2.5
          5X5:
            description: 5X5
          3x3:
            description: 3x3
      ecosystem_enum:
        permissible_values:
          Open Fen:
            description: Open Fen
          Treed Fen:
            description: Treed Fen
          Black Spruce:
            description: Black Spruce
          Poor Fen:
            description: Poor Fen
          Fen:
            description: Fen
          Lowland:
            description: Lowland
          Upland:
            description: Upland
          Bog:
            description: Bog
          Lowland Black Spruce:
            description: Lowland Black Spruce


Generalizing from multiple TSVs
-------------------------------

You can use the ``generalize-tsvs`` command to generalize from *multiple* TSVs, with
foreign key linkages auto-inferred.

For example, given a file ``envo.tsv``:

.. csv-table:: environments
    :header: envo term id, envo term label

    ENVO_01000752,area of barren land
    ENVO_01001570,terrestrial ecoregion
    ENVO_01001581,sea surface layer
    ENVO_01001582,forest floor

And a file file ``samples.tsv``:

.. csv-table:: samples
    :header: BIOSAMPLE_ID,BIOSAMPLE_NAME,ENVO_BIOME_ID,ENVO_FEATURE_ID,ENVO_MATERIAL_ID

    156554,"Enriched cells from forest soil in Barre Woods Harvard Forest LTER site, Petersham, Massachusetts, United States - Alteio_BWOrgControl_Nextera2",ENVO_01000174,ENVO_01000159,ENVO_00002261
    156649,"Enriched cells from forest soil in Barre Woods Harvard Forest LTER site, Petersham, Massachusetts, United States - Alteio_BWOrgHeat_Nextera5",ENVO_01000174,ENVO_01000159,ENVO_00005781
    156728,"Enriched cells from forest soil in Barre Woods Harvard Forest LTER site, Petersham, Massachusetts, United States - Alteio_BWOrgHeat_Nextera84",ENVO_01000174,ENVO_01000159,ENVO_00005781
    156738,"Enriched cells from forest soil in Barre Woods Harvard Forest LTER site, Petersham, Massachusetts, United States - Alteio_BWMinControl_Nextera2",ENVO_01000174,ENVO_01001275,ENVO_00002261

We can create a multi-class schema, with foreign keys inferred:

.. code-block::

    schemauto generalize-tsvs --infer-foreign-keys sample.tsv envo.tsv

This will generate a schema with two classes, where the join between the sample table and the term table
is inferred:

.. code-block:: yaml

classes:
  sample:
    slots:
    - BIOSAMPLE_ID
    - BIOSAMPLE_NAME
    - ENVO_BIOME_ID
    - ENVO_FEATURE_ID
    - ENVO_MATERIAL_ID
  envo:
    slots:
    - ENVO_ID
    - ENVO_LABEL

slots:
  BIOSAMPLE_ID:
    range: integer
  BIOSAMPLE_NAME:
    range: string
  ENVO_BIOME_ID:
    examples:
    - value: ENVO_01000022
    range: envo
  ENVO_FEATURE_ID:
    range: envo
  ENVO_MATERIAL_ID:
    range: envo
  ENVO_ID:
    identifier: true
    range: string
  ENVO_LABEL:
    range: string

Generalizing from tables on the web
-----------------------------------

You can use ``generalize-htmltable``

.. code-block::

    schemauto  generalize-htmltable  https://www.nature.com/articles/s41467-022-31626-4/tables/1

Will generate:

.. code-block:: yaml

    name: example
    description: example
    id: https://w3id.org/example
    imports:
    - linkml:types
    prefixes:
      linkml: https://w3id.org/linkml/
      example: https://w3id.org/example
    default_prefix: example
    slots:
      GWAS trait:
        examples:
        - value: "\xC2"
        range: string
      Peak GWAS SNP:
        examples:
        - value: rs2974298
        range: string
      Gene:
        examples:
        - value: SMIM19
        range: string
      NK cell cis eSNP:
        examples:
        - value: rs2974348
        range: string
      TWAS Z score:
        examples:
        - value: '3.809'
        range: string
      TWAS P value:
        examples:
        - value: '0.0001'
        range: string
    classes:
      example:
        slots:
        - GWAS trait
        - Peak GWAS SNP
        - Gene
        - NK cell cis eSNP
        - TWAS Z score
        - TWAS P value

Generalizing from JSON
----------------------

tbw

Chaining an annotator
---------------------

If you provide an ``--annotator`` option you can auto-annotate enums:

.. code-block::

    schemauto  generalize-tsv \
        --annotator bioportal:envo \
        tests/resources/NWT_wildfires_biophysical_2016.tsv \
        -o wildfire.yaml

.. code-block:: yaml

      ecosystem_enum:
        from_schema: https://w3id.org/MySchema
        permissible_values:
          Open Fen:
            description: Open Fen
            meaning: ENVO:00000232
            exact_mappings:
            - ENVO:00000232
          Treed Fen:
            description: Treed Fen
            meaning: ENVO:00000232
            exact_mappings:
            - ENVO:00000232
          Black Spruce:
            description: Black Spruce
          Poor Fen:
            description: Poor Fen
            meaning: ENVO:00000232
            exact_mappings:
            - ENVO:00000232
          Fen:
            description: Fen
            meaning: ENVO:00000232
          Lowland:
            description: Lowland
          Upland:
            description: Upland
            meaning: ENVO:00000182
          Bog:
            description: Bog
            meaning: ENVO:01000534
            exact_mappings:
            - ENVO:01000535
            - ENVO:00000044
            - ENVO:01001209
            - ENVO:01000527
          Lowland Black Spruce:
            description: Lowland Black Spruce

The annotation can also be run as a separate step

See :ref:`annotators`

Packages for generalizing
-------------------------

.. currentmodule:: schema_automator.generalizers

.. autoclass:: CsvDataGeneralizer
    :members:

.. autoclass:: JsonDataGeneralizer
    :members:

.. autoclass:: RdfDataGeneralizer
    :members:
