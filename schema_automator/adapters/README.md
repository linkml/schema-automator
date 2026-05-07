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
- `<format>/` — one subdirectory per source format. Source-format
  LinkML schemas live in `schema_automator/metamodels/` (alongside
  cadsr, frictionless, etc.), keeping the metamodel directory as the
  canonical home for declarative artifacts. The format directory holds:
  - `<format>_to_dd.transform.yaml` — `linkml-map` trans-spec for the
    forward direction (foreign format → DD).
  - `adapter.py` — Python entry points: forward function (driven by
    the trans-spec) and reverse function (DD → foreign format).

## Why the reverse is Python rather than a trans-spec

The forward direction maps cleanly to a `linkml-map` trans-spec —
`linkml-map` handles structural conversion, type-vocabulary translation
via `case()`, and nested-class population well.

The reverse direction (DD → foreign format) is implemented as a Python
helper instead. `linkml-map`'s expression evaluator is built on
simpleeval with a curated function set that doesn't expose `callable`
or `isinstance`, making it hard to disambiguate "slot is unbound"
(bound as a `_null_safe.wrapper`) from "slot is None" or "slot is 0"
when constructing nested target objects from flat DD slots. The
reverse mapping is structurally simple, so a Python function is
cleaner than 30 lines of escaped guard expressions. Forward is the
more common adapter use case (importing existing format data) and
where the trans-spec wins are biggest.

If a future `linkml-map` exposes richer type introspection, reverse
adapters can migrate to trans-specs without changing public APIs.

## Import boundary

Adapters import from `schema_automator.metamodels` and shared utilities.
Nothing else in `schema_automator` imports from `adapters/`. This keeps
later extraction to a dedicated repository cheap if/when adapter count
or external contribution justifies it.
