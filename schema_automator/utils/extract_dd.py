"""Project a LinkML schema into the canonical data dictionary format.

The inverse of the adapter family (foreign DD → canonical DD) and the
enricher (canonical DD → LinkML schema): this takes any LinkML schema —
including the output of the importers (XSD, JSON Schema, OWL, RDFS, SQL
DDL, EML) — and projects each class into a canonical Data Dictionary
matching ``schema_automator/metamodels/data_dictionary.yaml``.

Each class becomes a ``DataDictionary``; each (induced) slot becomes a
``DataDictionaryEntry``. See issue #209.

Mapping:

- ``slot.range`` → DD ``type`` via :data:`_RANGE_TO_DD_TYPE`; enum ranges
  become ``type: permissible_values`` with ``codes`` always present (an
  empty list for a value-less enum).
- ``description`` is always emitted (``""`` when the slot has none, since
  the canonical DD requires it); ``title`` → ``label``, ``slot_uri`` →
  ``uri``, ``pattern``, ``multivalued``, ``required`` (when True),
  ``see_also``, and ``examples`` → ``example_values`` carry through.
- ``unit`` / ``min`` / ``max`` are emitted only for numeric entries
  (``integer`` / ``decimal``) — where the canonical DD both permits and
  requires them — using the literal ``none`` sentinel for anything not
  declared. ``unit`` collapses best-effort from its UCUM-flavored object.
- Slots whose range is a class are skipped — they aren't flat columns.
"""

from __future__ import annotations

from typing import Any, Optional

from linkml_runtime.utils.schemaview import SchemaView

from schema_automator.adapters.codes import serialize_codes


# LinkML built-in range → canonical DD type vocabulary. Ranges absent
# from this map (and not an enum or class) fall back to ``string``.
_RANGE_TO_DD_TYPE = {
    "string": "string",
    "integer": "integer",
    "float": "decimal",
    "double": "decimal",
    "decimal": "decimal",
    "boolean": "boolean",
    "date": "date",
    "datetime": "datetime",
    "time": "time",
    "uri": "uri",
    "uriorcurie": "uri",
    "curie": "curie",
}

_NUMERIC_DD_TYPES = {"integer", "decimal"}

# Column order for the canonical DD TSV serialization.
_TSV_COLUMNS = [
    "name", "type", "description", "codes", "unit", "min", "max",
    "label", "multivalued", "required", "pattern", "uri", "see_also",
    "example_values",
]


def schema_to_dd(schemaview: SchemaView, class_name: str) -> dict[str, Any]:
    """Project one class of a LinkML schema into a canonical DD dict.

    Parameters
    ----------
    schemaview : SchemaView
        A SchemaView over the source schema.
    class_name : str
        The class to project. Its induced slots (inherited + local)
        become the DD entries.

    Returns
    -------
    dict
        ``{"entries": [...]}`` matching
        ``schema_automator/metamodels/data_dictionary.yaml``.
    """
    if schemaview.get_class(class_name) is None:
        raise ValueError(
            f"extract_dd: class {class_name!r} not in schema "
            f"(known: {sorted(schemaview.all_classes())})"
        )
    entries = []
    for slot in schemaview.class_induced_slots(class_name):
        entry = _slot_to_entry(schemaview, slot)
        if entry is not None:
            entries.append(entry)
    return {"entries": entries}


def projectable_classes(schemaview: SchemaView) -> list[str]:
    """Return the names of classes worth projecting in batch mode.

    Excludes mixins and abstract classes — they describe structure for
    reuse rather than concrete datasets.
    """
    return [
        name
        for name, cls in schemaview.all_classes().items()
        if not cls.abstract and not cls.mixin
    ]


def dd_to_tsv(data_dictionary: dict[str, Any]) -> str:
    """Serialize a canonical DD dict to the canonical TSV grammar.

    Multivalued cells (``see_also``, ``example_values``) are pipe-joined;
    ``codes`` uses the ``code, label | ...`` codes grammar.
    """
    lines = ["\t".join(_TSV_COLUMNS)]
    for entry in data_dictionary.get("entries", []):
        row = []
        for col in _TSV_COLUMNS:
            value = entry.get(col)
            if col == "codes" and isinstance(value, list):
                value = serialize_codes(value)
            elif isinstance(value, bool):
                value = "true" if value else "false"
            elif isinstance(value, list):
                value = "|".join(str(v) for v in value)
            row.append("" if value is None else str(value))
        lines.append("\t".join(row))
    return "\n".join(lines) + "\n"


def _slot_to_entry(schemaview: SchemaView, slot) -> Optional[dict[str, Any]]:
    """Project one induced slot into a DataDictionaryEntry dict, or None
    if the slot has no flat-column representation (class-ranged)."""
    rng = slot.range
    if rng and rng in schemaview.all_classes():
        return None

    entry: dict[str, Any] = {"name": slot.name}

    if rng and rng in schemaview.all_enums():
        entry["type"] = "permissible_values"
        # codes is required whenever type is permissible_values — emit
        # the key unconditionally (empty list for a value-less enum).
        entry["codes"] = _enum_codes(schemaview, rng)
    else:
        entry["type"] = _RANGE_TO_DD_TYPE.get(rng, "string")

    # description is required by the canonical DD; emit "" when the slot
    # has none (also a clean signal for a later enrichment pass to fill).
    entry["description"] = slot.description or ""
    if slot.title:
        entry["label"] = slot.title
    if slot.slot_uri:
        entry["uri"] = slot.slot_uri
    if slot.pattern:
        entry["pattern"] = slot.pattern
    if slot.multivalued:
        entry["multivalued"] = True
    if slot.required:
        entry["required"] = True

    see_also = list(slot.see_also or [])
    if see_also:
        entry["see_also"] = see_also

    example_values = [
        ex.value for ex in (slot.examples or []) if getattr(ex, "value", None)
    ]
    if example_values:
        entry["example_values"] = example_values

    # unit/min/max are permitted only on numeric types per the canonical
    # DD rules, and required there — carry declared values through, else
    # the explicit `none` sentinel. Non-numeric slots never emit them.
    if entry["type"] in _NUMERIC_DD_TYPES:
        unit = _unit_to_str(slot.unit)
        entry["unit"] = unit if unit else "none"
        entry["min"] = (
            slot.minimum_value if slot.minimum_value is not None else "none"
        )
        entry["max"] = (
            slot.maximum_value if slot.maximum_value is not None else "none"
        )

    return entry


def _enum_codes(schemaview: SchemaView, enum_name: str) -> list[dict[str, Any]]:
    """Project an enum's permissible values into DD code records."""
    enum = schemaview.get_enum(enum_name)
    codes = []
    for pv in (enum.permissible_values or {}).values():
        code: dict[str, Any] = {"code": pv.text}
        if pv.title:
            code["label"] = pv.title
        if pv.description:
            code["description"] = pv.description
        if pv.meaning:
            code["uri"] = pv.meaning
        codes.append(code)
    return codes


def _unit_to_str(unit) -> Optional[str]:
    """Collapse LinkML's UCUM-flavored unit object to a freeform string.

    Best-effort: prefer ``symbol``, then ``ucum_code``, then
    ``descriptive_name``. Returns None when no unit is set.
    """
    if not unit:
        return None
    for attr in ("symbol", "ucum_code", "descriptive_name"):
        value = getattr(unit, attr, None)
        if value:
            return value
    return None
