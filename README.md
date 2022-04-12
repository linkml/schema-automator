# LinkML Schema Automator

[![DOI](https://zenodo.org/badge/13996/linkml/schema_automator.svg)](https://zenodo.org/badge/latestdoi/13996/linkml/schema_automator)


This is a toolkit that assists with:

 1. Bootstrapping LinkML models from instance data
    - TSVs and spreadsheets
    - SQLite databases
    - RDF instance graphs
 2. Bootstrapping a LinkML model from a different schema representation (i.e. opposite of a linkml.generator)
    - OWL (RDFS-like subset)
    - TODO: JSON-Schema, XSD, ShEx, SHACL, SQL DDL, FHIR, Python dataclasses/pydantic, etc
 3. Using automated methods to enhance a model
    - Using text mining and concept annotator APIs to enrich semantic enums
    - TODO: querying sparql endpoints to retrieve additional metadata

These can be composed together. For example, run `tsvs2linkml` followed by `annotate-enums`

The toolkit is still experimental. It is intended as an aid to schema creation rather than act as a formal conversion tool

## Installation

`linkml-model-enrichment` and its components require Python 3.9 or greater.

```bash
chmod 755 environment.sh
. environment.sh
pip install -r requirements.txt
pip install -e . 
```

## Command Line Usage

### Annotating Enums

This toolkit allows automated annotation of LinkML enums, mapping text strings to ontology terms.

The command line tool `annotate-enums` takes a LinkML schema, with enums and fills in the `meaning` slots.

See the [annotators](schema_automator/annotators/) folder for docs

### Converting TSVs

The `tsv2linkml` command infers a single-class schema from a TSV datafile

```bash
$ tsv2linkml --help
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
```

Example:

```bash
tsv2linkml tests/resources/biobank-specimens.tsv 
```

The `tsvs2linkml` command infers a multi-class schema from multiple TSV datafiles

```
$ tsvs2linkml --help
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
```


### Converting OWL

```bash
$ owl2linkml --help
Usage: owl2linkml [OPTIONS] OWLFILE

  Infer a model from OWL Ontology

  Note: input must be in functional syntax

Options:
  -n, --name TEXT  Schema name
  --help           Show this message and exit.
```

Example:

```bash
owl2linkml -n prov tests/resources/prov.ofn > prov.yaml
```

Note this works best on schema-style ontologies such as Prov

**NOT** recommended for terminological-style ontologies such as OBO

### Converting RDF instance graphs

```bash
$ rdf2linkml --help
Usage: rdf2linkml [OPTIONS] RDFFILE

  Infer a model from RDF instance data

Options:
  -d, --dir TEXT  [required]
  --help          Show this message and exit.
```

### Converting JSON Instance Data

```bash
$ jsondata2linkml --help
Usage: jsondata2linkml [OPTIONS] INPUT

  Infer a model from JSON instance data



Options:
  --container-class-name TEXT   name of root class
  -f, --format TEXT             json or yaml (or json.gz or yaml.gz)
  --omit-null / --no-omit-null  if true, ignore null values
  --help                        Show this message and exit.
```

### Converting JSON-Schema


```
$ jsonschema2linkml --help
Usage: jsonschema2linkml [OPTIONS] INPUT

  Infer a model from JSON Schema

Options:
  -n, --name TEXT    ID of schema  [required]
  -f, --format TEXT  JSON Schema format - yaml or json
  -o, --output TEXT  output path
  --help             Show this message and exit.
```
