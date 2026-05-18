"""REDCap data dictionary ↔ canonical Data Dictionary adapter.

Both directions are driven by linkml-map trans-specs:

- ``redcap_to_dd.transform.yaml`` — REDCap → DD
- ``dd_to_redcap.transform.yaml`` — DD → REDCap

REDCap's multi-purpose "Choices, Calculations, OR Slider Labels" column
is parsed into the structured ``choices`` slot on the source side before
the trans-spec runs, so the trans-spec operates on a clean structured
representation rather than reaching into Python from inside the spec.
``yesno`` and ``truefalse`` are synthesized to their standard two-code
sets at load time as well.

The reverse trans-spec uses linkml-map's ``is_*`` type predicates
(landing in linkml-map 0.5.3) to filter linkml-map's null-safe wrapper
sentinel. On the currently released 0.5.2, the reverse direction raises
``RuntimeError`` with a clear message; the forward direction works on
0.5.2.
"""

from __future__ import annotations

import csv
from pathlib import Path
from typing import Any

from linkml_map.transformer.object_transformer import ObjectTransformer
from linkml_map.utils.eval_utils import FUNCTIONS as _LINKML_MAP_FUNCTIONS
from linkml_map.utils.loaders import load_specification
from linkml_runtime.utils.schemaview import SchemaView

from schema_automator.adapters.codes import parse_codes, serialize_codes


_REVERSE_REQUIRED_PREDICATES = ("is_str", "is_bool", "is_list")


def _check_reverse_supported() -> None:
    """Raise a clear error if the installed linkml-map lacks the type
    predicates the reverse trans-spec depends on (i.e., on 0.5.2)."""
    missing = [p for p in _REVERSE_REQUIRED_PREDICATES if p not in _LINKML_MAP_FUNCTIONS]
    if missing:
        raise RuntimeError(
            "The DD → REDCap reverse adapter requires linkml-map >= 0.5.3 "
            f"for the {', '.join(missing)} type predicate(s). Installed "
            "linkml-map is missing those. Upgrade with `pip install "
            "--upgrade linkml-map` once 0.5.3 ships."
        )


_PKG_ROOT = Path(__file__).resolve().parents[2]
_DD_SCHEMA = _PKG_ROOT / "metamodels" / "data_dictionary.yaml"
_REDCAP_SCHEMA = _PKG_ROOT / "metamodels" / "redcap.yaml"
_REDCAP_TO_DD_SPEC = _PKG_ROOT / "adapters" / "redcap" / "redcap_to_dd.transform.yaml"
_DD_TO_REDCAP_SPEC = _PKG_ROOT / "adapters" / "redcap" / "dd_to_redcap.transform.yaml"


# Map REDCap CSV column headers to RedcapField slot names. REDCap's
# CSV column headers are stable across exports; we accept the documented
# canonical spellings.
_CSV_TO_SLOT = {
    "Variable / Field Name": "field_name",
    "Form Name": "form_name",
    "Section Header": "section_header",
    "Field Type": "field_type",
    "Field Label": "field_label",
    "Choices, Calculations, OR Slider Labels": "choices_calculations_or_slider_labels",
    "Field Note": "field_note",
    "Text Validation Type OR Show Slider Number": "text_validation_type",
    "Text Validation Min": "text_validation_min",
    "Text Validation Max": "text_validation_max",
    "Identifier?": "identifier",
    "Branching Logic (Show field only if...)": "branching_logic",
    "Required Field?": "required_field",
    "Custom Alignment": "custom_alignment",
    "Question Number (surveys only)": "question_number",
    "Matrix Group Name": "matrix_group_name",
    "Matrix Ranking?": "matrix_ranking",
    "Field Annotation": "field_annotation",
}

_CHOICE_FIELD_TYPES = {"radio", "dropdown", "checkbox"}

# REDCap exports yesno and truefalse with literal 1/0 data values. We
# synthesize the structured choice list so the trans-spec sees the same
# shape as radio / dropdown.
_YESNO_CHOICES = [{"code": "1", "label": "Yes"}, {"code": "0", "label": "No"}]
_TRUEFALSE_CHOICES = [{"code": "1", "label": "True"}, {"code": "0", "label": "False"}]


def _row_to_field(row: dict[str, str]) -> dict[str, Any] | None:
    """Convert one CSV row into a RedcapField dict.

    Returns ``None`` for ``descriptive`` rows (REDCap's non-data text
    blocks) — they aren't variables and shouldn't end up as DD entries.

    The multi-purpose choices column is parsed into the structured
    ``choices`` slot for choice-type fields, leaving the raw value on
    ``choices_calculations_or_slider_labels`` for calc / slider.
    """
    field: dict[str, Any] = {}
    for csv_col, slot_name in _CSV_TO_SLOT.items():
        raw = row.get(csv_col)
        if raw is None:
            continue
        raw = raw.strip()
        if raw == "":
            continue
        field[slot_name] = raw

    if "field_name" not in field:
        return None

    field_type = field.get("field_type")
    if field_type == "descriptive":
        return None

    if field_type in _CHOICE_FIELD_TYPES:
        choices_raw = field.get("choices_calculations_or_slider_labels")
        if choices_raw:
            field["choices"] = parse_codes(choices_raw)
    elif field_type == "yesno":
        field["choices"] = list(_YESNO_CHOICES)
    elif field_type == "truefalse":
        field["choices"] = list(_TRUEFALSE_CHOICES)

    return field


def load_redcap_csv(path: str | Path) -> dict[str, Any]:
    """Read a REDCap data dictionary CSV into the source structure.

    Parameters
    ----------
    path : str or Path
        Path to a REDCap data dictionary CSV (the file REDCap exports
        from Project Setup → Data Dictionary).

    Returns
    -------
    dict
        A ``RedcapDataDictionary`` dict ready to pass to
        :func:`redcap_to_dd`. ``descriptive`` rows are filtered out.
    """
    with open(path, newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        entries = []
        for row in reader:
            field = _row_to_field(row)
            if field is not None:
                entries.append(field)
    return {"entries": entries}


def _strip_nulls(obj: Any) -> Any:
    """Recursively drop dict entries with None values and empty dicts."""
    if isinstance(obj, dict):
        cleaned = {k: _strip_nulls(v) for k, v in obj.items() if v is not None}
        return {k: v for k, v in cleaned.items() if not (isinstance(v, dict) and not v)}
    if isinstance(obj, list):
        return [_strip_nulls(x) for x in obj]
    return obj


def _make_transformer(
    spec_path: Path, source_schema: Path, target_schema: Path
) -> ObjectTransformer:
    spec = load_specification(str(spec_path))
    source_sv = SchemaView(str(source_schema))
    target_sv = SchemaView(str(target_schema))
    tr = ObjectTransformer(source_schemaview=source_sv, specification=spec)
    tr.target_schemaview = target_sv
    return tr


def redcap_to_dd(redcap_dict: dict) -> dict:
    """Translate a REDCap data dictionary into the canonical DD format.

    Parameters
    ----------
    redcap_dict : dict
        A ``RedcapDataDictionary`` dict as produced by
        :func:`load_redcap_csv` — i.e., with the multi-purpose choices
        column already parsed into the structured ``choices`` slot.

    Returns
    -------
    dict
        A canonical Data Dictionary matching
        ``schema_automator/metamodels/data_dictionary.yaml``.
    """
    tr = _make_transformer(_REDCAP_TO_DD_SPEC, _REDCAP_SCHEMA, _DD_SCHEMA)
    return _strip_nulls(tr.map_object(redcap_dict, source_type="RedcapDataDictionary"))


def dd_to_redcap(data_dictionary: dict) -> dict:
    """Translate a canonical DD into a REDCap data dictionary structure.

    Requires linkml-map >= 0.5.3 (for the ``is_str`` / ``is_bool`` /
    ``is_list`` type predicates the reverse trans-spec uses). Raises
    ``RuntimeError`` on earlier linkml-map releases with a message
    pointing at the upgrade.

    Lossy in several places: DD ``unit`` / ``min`` / ``max`` for
    non-numeric validations are dropped; DD ``pattern`` has no native
    REDCap target; DD ``uri``, ``see_also``, ``example_values`` have no
    REDCap target.

    Returned structure mirrors the source schema (a
    ``RedcapDataDictionary`` dict with ``entries``). Each entry's
    ``choices`` list is serialized back into the canonical
    ``code, label | ...`` string under
    ``choices_calculations_or_slider_labels`` so the result can be
    written straight to CSV.

    Parameters
    ----------
    data_dictionary : dict
        A canonical DD document with an ``entries`` list.
    """
    _check_reverse_supported()
    tr = _make_transformer(_DD_TO_REDCAP_SPEC, _DD_SCHEMA, _REDCAP_SCHEMA)
    result = _strip_nulls(tr.map_object(data_dictionary, source_type="DataDictionary"))
    # Serialize structured choices back to REDCap's CSV string form.
    for entry in result.get("entries", []):
        choices = entry.pop("choices", None)
        if choices:
            entry["choices_calculations_or_slider_labels"] = serialize_codes(choices)
    return result


_REDCAP_CSV_COLUMNS = list(_CSV_TO_SLOT.keys())


def dump_redcap_csv(redcap_dict: dict, fp) -> None:
    """Serialize a RedcapDataDictionary dict to a file-like object as
    REDCap-format CSV.

    Unset slots become empty cells; column order matches REDCap's
    documented export order.
    """
    slot_to_csv = {slot: col for col, slot in _CSV_TO_SLOT.items()}
    writer = csv.DictWriter(fp, fieldnames=_REDCAP_CSV_COLUMNS)
    writer.writeheader()
    for entry in redcap_dict.get("entries", []):
        row = {slot_to_csv[k]: v for k, v in entry.items() if k in slot_to_csv}
        writer.writerow(row)


def write_redcap_csv(redcap_dict: dict, path: str | Path) -> None:
    """Write a RedcapDataDictionary dict to a REDCap-format CSV file."""
    with open(path, "w", newline="", encoding="utf-8") as f:
        dump_redcap_csv(redcap_dict, f)
