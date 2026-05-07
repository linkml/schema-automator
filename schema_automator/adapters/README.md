# Data Dictionary Adapters

This directory hosts adapters that translate between schema-automator's
canonical data dictionary format (defined in
`schema_automator/metamodels/data_dictionary.yaml`) and existing
third-party data dictionary formats. The adapter approach is uniform:
each format has a LinkML source schema, a `linkml-map` trans-spec
mapping it to/from the canonical DD, and any small per-format helpers.

See umbrella issue [#202](https://github.com/linkml/schema-automator/issues/202)
for design context.

## Layout

- `codes.py` — utility for serializing the canonical `codes` list to
  the TSV grammar and parsing it back. Used by every adapter as the
  parse/serialize bookend, and by canonical-format TSV ↔ YAML
  conversion.
- `<format>/` — one subdirectory per source format:
  - `<format>.yaml` — LinkML schema describing the source format.
  - `<format>_to_dd.transform.yaml` — trans-spec source → canonical DD.
  - `dd_to_<format>.transform.yaml` — trans-spec canonical DD → source.
  - any per-format helpers (parsers, serializers).

## Import boundary

Adapters import from `schema_automator.metamodels` and shared utilities.
Nothing else in `schema_automator` imports from `adapters/`. This keeps
later extraction to a dedicated repository cheap if/when adapter count
or external contribution justifies it.
