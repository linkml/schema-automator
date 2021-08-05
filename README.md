# LinkML Model Enrichment (Beta)

This is a toolkit that assists with:

 1. Bootstrapping LinkML models from instance data
    - TSVs and spreadsheets
    - SQLite databases
    - RDF instance graphs
 2. Bootstrapping a LinkML model from a different schema representation
    - OWL (RDFS-like subset)
    - TODO: JSON-Schema, ShEx, SHACL, SQL DDL, Python dataclasses/pydantic, etc
 3. Using automated methods to enhance a model
    - Using text mining and concept annotator APIs to enrich semantic enums
    - TODO: querying sparql endpoints to retrieve additional metadata

The toolkit is still experimental. It is intended as an aid to schema creation rather than a formal conversion tool

## Installation

`linkml-model-enrichment` and its components require Python 3.9 or greater.

```bash
. environment.sh
pip install -r requirements.txt 
```

## Command Line Usage

### Converting TSVs

TODO - document this

### Converting OWL

```bash
$ owl2model --help
Usage: owl2model [OPTIONS] OWLFILE

  Infer a model from OWL Ontology

  Note: input must be in functional syntax

Options:
  -n, --name TEXT  Schema name
  --help           Show this message and exit.
```

Example:

```bash
owl2model -n prov tests/resources/prov.ofn > prov.yaml
```

Note this works best on schema-style ontologies such as Prov

**NOT** recommended for terminological-style ontologies such as OBO

### Converting RDF instance graphs

```bash
$ rdf2model --help
Usage: rdf2model [OPTIONS] RDFFILE

  Infer a model from RDF instance data

Options:
  -d, --dir TEXT  [required]
  --help          Show this message and exit.
```
