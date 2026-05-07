"""Frictionless Table Schema ↔ canonical Data Dictionary adapter.

The forward direction (Frictionless → DD) is driven by a linkml-map
trans-spec at ``frictionless_to_dd.transform.yaml`` — that's the
declarative core of the adapter. Forward output is a structured DD
matching ``schema_automator/metamodels/data_dictionary.yaml``.

The reverse direction (DD → Frictionless) is implemented as a Python
function rather than a trans-spec. Reasons (worth knowing for #202):

- ``linkml-map``'s expression evaluator (built on simpleeval with a
  curated function set) doesn't expose ``callable`` or ``isinstance``,
  which makes it hard to disambiguate "slot is unbound" (bound as a
  ``_null_safe.wrapper``) from "slot is None" or "slot is 0". The
  forward direction sidesteps this because Frictionless source data is
  consumed via standard linkml-map flow with native null handling; the
  reverse direction needs to construct nested Frictionless objects
  (``Constraints``) from flat DD slots, which exposes the wrapper.
- The reverse mapping is structurally simple enough that Python is
  cleaner than 30 lines of escaped guard expressions.

Forward is the more common adapter use case (importing existing
Frictionless DDs into our format). Reverse is a "just-in-case" path
and is best handled directly. If a future linkml-map adds richer
type-introspection, this can be migrated to a trans-spec.
"""

from __future__ import annotations

from importlib import resources
from pathlib import Path
from typing import Any, Optional, Union

from linkml_map.transformer.object_transformer import ObjectTransformer
from linkml_map.utils.loaders import load_specification
from linkml_runtime.utils.schemaview import SchemaView


_PKG_ROOT = Path(__file__).resolve().parents[2]
_DD_SCHEMA = _PKG_ROOT / "metamodels" / "data_dictionary.yaml"
_FRICTIONLESS_SCHEMA = _PKG_ROOT / "metamodels" / "frictionless.yaml"
_FRICTIONLESS_TO_DD_SPEC = (
    _PKG_ROOT / "adapters" / "frictionless" / "frictionless_to_dd.transform.yaml"
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
    spec = load_specification(str(_FRICTIONLESS_TO_DD_SPEC))
    source_sv = SchemaView(str(_FRICTIONLESS_SCHEMA))
    target_sv = SchemaView(str(_DD_SCHEMA))
    tr = ObjectTransformer(source_schemaview=source_sv, specification=spec)
    tr.target_schemaview = target_sv
    result = tr.map_object(table_schema, source_type="TableSchema")
    return _strip_nulls(result)


_DD_TYPE_TO_FRICTIONLESS = {
    "string": "string",
    "integer": "integer",
    "decimal": "number",
    "boolean": "boolean",
    "date": "date",
    "time": "time",
    "datetime": "datetime",
    "uri": "string",
    "curie": "string",
    "permissible_values": "string",
}


def _entry_to_field(entry: dict) -> dict:
    """Convert one DD entry to one Frictionless Field."""
    field: dict[str, Any] = {"name": entry["name"]}
    if entry.get("label"):
        field["title"] = entry["label"]
    if entry.get("description"):
        field["description"] = entry["description"]
    examples = entry.get("example_values")
    if examples:
        # Frictionless `example` is scalar; take the first.
        field["example"] = examples[0]
    if entry.get("uri"):
        field["rdfType"] = entry["uri"]

    dd_type = entry.get("type", "string")
    field["type"] = _DD_TYPE_TO_FRICTIONLESS.get(dd_type, "string")

    constraints: dict[str, Any] = {}
    if entry.get("required") is not None:
        constraints["required"] = entry["required"]
    if entry.get("pattern"):
        constraints["pattern"] = entry["pattern"]

    codes = entry.get("codes")
    if codes:
        constraints["enum"] = [c["code"] for c in codes]

    # min/max only emit if numeric and not the literal "none" sentinel.
    for src_key, tgt_key in (("min", "minimum"), ("max", "maximum")):
        v = entry.get(src_key)
        if v is None or v == "none":
            continue
        constraints[tgt_key] = str(v)

    if constraints:
        field["constraints"] = constraints

    return field


def dd_to_frictionless(data_dictionary: dict) -> dict:
    """Translate a canonical DD into a Frictionless Table Schema.

    Lossy in several places (per-code labels, description, URI;
    DD ``unit``; DD type values ``uri``/``curie``/``permissible_values``
    all collapse to Frictionless ``string``). See module docstring for
    why this is a Python function rather than a trans-spec.

    Parameters
    ----------
    data_dictionary : dict
        A canonical DD document with an ``entries`` list.

    Returns
    -------
    dict
        A Frictionless Table Schema document with ``fields``.
    """
    entries = data_dictionary.get("entries", [])
    return {"fields": [_entry_to_field(e) for e in entries]}
