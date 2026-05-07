"""Frictionless Table Schema ↔ canonical Data Dictionary adapter.

Both directions are driven by linkml-map trans-specs:

- ``frictionless_to_dd.transform.yaml`` — Frictionless → DD
- ``dd_to_frictionless.transform.yaml`` — DD → Frictionless

The reverse trans-spec uses linkml-map's ``is_*`` type predicates
(``is_str``, ``is_bool``, ``is_list``, ``is_numeric``) to filter
linkml-map's null-safe wrapper sentinel — each constraint slot has a
known semantic type, so the predicates double as sentinel-filter and
type-correctness check.

The full set of type predicates lands in linkml-map 0.5.3. The current
released version (0.5.2) only has ``is_numeric``. The forward adapter
and codes utility work on 0.5.2; the reverse adapter raises a clear
error on 0.5.2 and works on 0.5.3+.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from linkml_map.transformer.object_transformer import ObjectTransformer
from linkml_map.utils.eval_utils import FUNCTIONS as _LINKML_MAP_FUNCTIONS
from linkml_map.utils.loaders import load_specification
from linkml_runtime.utils.schemaview import SchemaView


_REVERSE_REQUIRED_PREDICATES = ("is_str", "is_bool", "is_list")


def _check_reverse_supported() -> None:
    """Raise a clear error if the installed linkml-map lacks the type
    predicates the reverse trans-spec depends on (i.e., on 0.5.2)."""
    missing = [p for p in _REVERSE_REQUIRED_PREDICATES if p not in _LINKML_MAP_FUNCTIONS]
    if missing:
        raise RuntimeError(
            "The DD → Frictionless reverse adapter requires linkml-map "
            f">= 0.5.3 for the {', '.join(missing)} type predicate(s). "
            "Installed linkml-map is missing those. Upgrade with "
            "`pip install --upgrade linkml-map` once 0.5.3 ships."
        )


_PKG_ROOT = Path(__file__).resolve().parents[2]
_DD_SCHEMA = _PKG_ROOT / "metamodels" / "data_dictionary.yaml"
_FRICTIONLESS_SCHEMA = _PKG_ROOT / "metamodels" / "frictionless.yaml"
_FRICTIONLESS_TO_DD_SPEC = (
    _PKG_ROOT / "adapters" / "frictionless" / "frictionless_to_dd.transform.yaml"
)
_DD_TO_FRICTIONLESS_SPEC = (
    _PKG_ROOT / "adapters" / "frictionless" / "dd_to_frictionless.transform.yaml"
)


def _strip_nulls(obj: Any) -> Any:
    """Recursively drop dict entries with None values and empty constraint dicts."""
    if isinstance(obj, dict):
        cleaned = {k: _strip_nulls(v) for k, v in obj.items() if v is not None}
        # Drop empty constraint dicts so consumers don't see noise.
        return {k: v for k, v in cleaned.items() if not (isinstance(v, dict) and not v)}
    if isinstance(obj, list):
        return [_strip_nulls(x) for x in obj]
    return obj


def _make_transformer(spec_path: Path, source_schema: Path, target_schema: Path) -> ObjectTransformer:
    spec = load_specification(str(spec_path))
    source_sv = SchemaView(str(source_schema))
    target_sv = SchemaView(str(target_schema))
    tr = ObjectTransformer(source_schemaview=source_sv, specification=spec)
    tr.target_schemaview = target_sv
    return tr


def frictionless_to_dd(table_schema: dict) -> dict:
    """Translate a Frictionless Table Schema into the canonical DD format.

    Parameters
    ----------
    table_schema : dict
        A Frictionless Table Schema document (the ``schema`` block of a
        Frictionless data resource, or a standalone ``tableschema.json``).

    Returns
    -------
    dict
        A canonical Data Dictionary matching
        ``schema_automator/metamodels/data_dictionary.yaml``.
    """
    tr = _make_transformer(_FRICTIONLESS_TO_DD_SPEC, _FRICTIONLESS_SCHEMA, _DD_SCHEMA)
    return _strip_nulls(tr.map_object(table_schema, source_type="TableSchema"))


def dd_to_frictionless(data_dictionary: dict) -> dict:
    """Translate a canonical DD into a Frictionless Table Schema.

    Requires linkml-map >= 0.5.3 (for the is_str / is_bool / is_list type
    predicates the reverse trans-spec uses). Raises ``RuntimeError`` on
    earlier linkml-map releases with a message pointing at the upgrade.

    Lossy in several places: per-code labels and per-code metadata are
    dropped (Frictionless ``enum`` is just an array of values); DD
    ``unit`` has no Frictionless equivalent; DD type values
    ``uri``/``curie``/``permissible_values`` all collapse to Frictionless
    ``string``.

    Parameters
    ----------
    data_dictionary : dict
        A canonical DD document with an ``entries`` list.

    Returns
    -------
    dict
        A Frictionless Table Schema document with ``fields``.
    """
    _check_reverse_supported()
    tr = _make_transformer(_DD_TO_FRICTIONLESS_SPEC, _DD_SCHEMA, _FRICTIONLESS_SCHEMA)
    return _strip_nulls(tr.map_object(data_dictionary, source_type="DataDictionary"))
