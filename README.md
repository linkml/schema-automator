# LinkML Schema Automator

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

The toolkit is still experimental. It is intended as an aid to schema creation rather than as a formal conversion
tool.

[Full Documentation](https://linkml.io/schema-automator/)
