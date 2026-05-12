# Data Dictionary Adapters

This directory hosts adapters that translate between schema-automator's
canonical data dictionary format (defined in
`schema_automator/metamodels/data_dictionary.yaml`) and existing
third-party data dictionary formats. The adapter approach is uniform:
each format has a LinkML source schema, a `linkml-map` trans-spec
mapping it to/from the canonical DD, and any small per-format helpers.

See umbrella issue [#202](https://github.com/linkml/schema-automator/issues/202)
for design context.

## Adapters

- `frictionless/` — Frictionless Table Schema ↔ canonical DD (issue [#203](https://github.com/linkml/schema-automator/issues/203)).
- `dbgap/` — dbGaP variable digest XML (data_dict.xml + optional var_report.xml) → canonical DD (issue [#206](https://github.com/linkml/schema-automator/issues/206)). Forward-only for v1; dbGaP isn't really a writable target format. Pairs with dm-bip's fetcher (dm-bip PR #320).
- `redcap/` — REDCap data dictionary ↔ canonical DD (issue [#204](https://github.com/linkml/schema-automator/issues/204), open).

## Layout

- `codes.py` — utility for serializing the canonical `codes` list to
  the TSV grammar and parsing it back. Used by adapters that consume
  TSV-form codes, and by canonical-format TSV ↔ YAML conversion.
- `<format>/` — one subdirectory per source format. Source-format
  LinkML schemas live in `schema_automator/metamodels/` (alongside
  cadsr, frictionless, etc.), keeping the metamodel directory as the
  canonical home for declarative schema artifacts. The format directory
  holds:
  - `<format>_to_dd.transform.yaml` — `linkml-map` trans-spec, foreign
    format → DD.
  - `dd_to_<format>.transform.yaml` — `linkml-map` trans-spec, DD →
    foreign format.
  - `adapter.py` — thin Python wrappers that wire the trans-specs to
    `linkml-map`'s `ObjectTransformer` and post-process (strip nulls,
    drop empty constraint blocks).

## Idiom: type predicates filter the null sentinel

`linkml-map` binds unset source slots to a callable wrapper rather
than `None`, to allow chained attribute access without raising.
That sentinel is callable and truthy, so naive `if x:` and
`x is not None` checks let it through.

The clean filter is `linkml-map`'s `is_*` type predicates
(`is_str`, `is_int`, `is_float`, `is_bool`, `is_list`, `is_numeric`).
The wrapper isn't an instance of any concrete type, so all of these
return False on it. Each target slot in the trans-spec has a known
semantic type, so the predicate doubles as both sentinel-filter and
type-correctness check:

```yaml
constraints:
  expr: >
    {
      'required': case((is_bool(required), required)),
      'pattern':  case((is_str(pattern),   pattern)),
      'enum':     case((is_list(codes),    [c.code for c in codes])),
      'minimum':  case((is_numeric(min),   str(min))),
      'maximum':  case((is_numeric(max),   str(max))),
    }
```

`case((cond, value))` returns `None` when `cond` is False, and the
post-processing in `adapter.py` strips nulls. This idiom is preferred
over reaching for `callable(x)` (which would couple to a `linkml-map`
implementation detail) and over a Python-side fallback.

The full set of `is_*` predicates is available in `linkml-map` 0.5.3
and later. The currently released version (0.5.2) only has
`is_numeric`. The Frictionless adapter's *forward* direction works on
0.5.2 (it uses only `is_numeric`); the *reverse* direction needs 0.5.3
and raises a clear `RuntimeError` on earlier versions. The
reverse-direction tests are marked `xfail` until the dep can be bumped
to `>= 0.5.3`.

## Import boundary

Adapters import from `schema_automator.metamodels` and shared utilities.
Nothing else in `schema_automator` imports from `adapters/`. This keeps
later extraction to a dedicated repository cheap if/when adapter count
or external contribution justifies it.
