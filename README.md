# LinkML Schema Automator

This is a toolkit that assists with the generation and enhancement of [LinkML](https://linkml.io/linkml) schemas

## Install

```bash
pip install schema-automator
```

## Command Line

See [CLI docs](https://linkml.io/schema-automator/cli)

Generalizing:

```bash
schemauto generalize-tsv my-data.tsv > my-schema.yaml
```

Importing:

```bash
schemauto import-json-schema their.schema.json > my-schema.yaml
```

Annotating:

```bash
schemauto annotate-schema my-schema.yaml
```

## Full Documentation

[linkml.io/schema-automator](https://linkml.io/schema-automator/)
