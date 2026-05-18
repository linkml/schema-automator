"""Tests for the REDCap ↔ DD adapter."""

from pathlib import Path

import pytest
from linkml_map.utils.eval_utils import FUNCTIONS as _LINKML_MAP_FUNCTIONS

from schema_automator.adapters.redcap.adapter import (
    dd_to_redcap,
    load_redcap_csv,
    redcap_to_dd,
)


# The reverse adapter's trans-spec uses linkml-map's is_str / is_bool /
# is_list type predicates, which land in linkml-map 0.5.3. On 0.5.2 (the
# current PyPI release) the reverse trans-spec raises at evaluation time.
# xfail the reverse-direction tests until the dep constraint can be
# bumped to >= 0.5.3 (mirrors the Frictionless adapter's pattern).
_HAS_TYPE_PREDICATES = "is_str" in _LINKML_MAP_FUNCTIONS
_REVERSE_REQUIRES_LINKML_MAP_053 = pytest.mark.xfail(
    not _HAS_TYPE_PREDICATES,
    reason="Reverse adapter trans-spec requires linkml-map >= 0.5.3 "
    "(is_str / is_bool / is_list type predicates)",
    strict=True,
    raises=Exception,
)


_FIXTURES = Path(__file__).resolve().parents[1] / "resources" / "redcap"


def _by_name(dd: dict) -> dict[str, dict]:
    return {e["name"]: e for e in dd["entries"]}


# ----------------------------------------------------------------------
# CSV loader (REDCap CSV → source structure).
# ----------------------------------------------------------------------


class TestLoadRedcapCsv:
    def test_minimal_loads(self):
        src = load_redcap_csv(_FIXTURES / "minimal.csv")
        names = [e["field_name"] for e in src["entries"]]
        # `intro_text` (descriptive) is filtered out.
        assert names == [
            "record_id",
            "first_name",
            "age",
            "sex",
            "races",
            "is_smoker",
            "consent",
            "bmi",
        ]

    def test_radio_choices_parsed_to_structured_form(self):
        src = load_redcap_csv(_FIXTURES / "minimal.csv")
        sex = next(e for e in src["entries"] if e["field_name"] == "sex")
        assert sex["choices"] == [
            {"code": "0", "label": "Female"},
            {"code": "1", "label": "Male"},
        ]

    def test_yesno_synthesizes_choices(self):
        src = load_redcap_csv(_FIXTURES / "minimal.csv")
        smoker = next(e for e in src["entries"] if e["field_name"] == "is_smoker")
        assert smoker["choices"] == [
            {"code": "1", "label": "Yes"},
            {"code": "0", "label": "No"},
        ]

    def test_truefalse_synthesizes_choices(self):
        src = load_redcap_csv(_FIXTURES / "minimal.csv")
        consent = next(e for e in src["entries"] if e["field_name"] == "consent")
        assert consent["choices"] == [
            {"code": "1", "label": "True"},
            {"code": "0", "label": "False"},
        ]

    def test_calc_keeps_raw_column(self):
        src = load_redcap_csv(_FIXTURES / "minimal.csv")
        bmi = next(e for e in src["entries"] if e["field_name"] == "bmi")
        # calc retains the formula on the raw slot; no structured choices.
        assert "choices" not in bmi
        assert (
            bmi["choices_calculations_or_slider_labels"]
            == "[weight] / ([height]*[height])"
        )

    def test_empty_cells_dropped(self):
        src = load_redcap_csv(_FIXTURES / "minimal.csv")
        record = next(e for e in src["entries"] if e["field_name"] == "record_id")
        # Empty cells (section_header etc.) shouldn't show up.
        assert "section_header" not in record
        assert "text_validation_type" not in record


# ----------------------------------------------------------------------
# Forward direction (REDCap → DD) — driven by the trans-spec.
# ----------------------------------------------------------------------


class TestRedcapToDD:
    def test_text_field_maps_to_string(self):
        src = load_redcap_csv(_FIXTURES / "minimal.csv")
        dd = redcap_to_dd(src)
        record = _by_name(dd)["record_id"]
        assert record["type"] == "string"
        assert record["label"] == "Record ID"
        assert record["required"] is True

    def test_field_label_maps_to_label(self):
        src = load_redcap_csv(_FIXTURES / "minimal.csv")
        dd = redcap_to_dd(src)
        assert _by_name(dd)["first_name"]["label"] == "First Name"

    def test_field_note_maps_to_description(self):
        src = load_redcap_csv(_FIXTURES / "minimal.csv")
        dd = redcap_to_dd(src)
        assert _by_name(dd)["first_name"]["description"] == "Given name"

    def test_text_integer_validation_maps_to_integer(self):
        src = load_redcap_csv(_FIXTURES / "minimal.csv")
        dd = redcap_to_dd(src)
        age = _by_name(dd)["age"]
        assert age["type"] == "integer"
        assert age["min"] == 0
        assert age["max"] == 120

    def test_radio_maps_to_permissible_values(self):
        src = load_redcap_csv(_FIXTURES / "minimal.csv")
        dd = redcap_to_dd(src)
        sex = _by_name(dd)["sex"]
        assert sex["type"] == "permissible_values"
        assert sex["codes"] == [
            {"code": "0", "label": "Female"},
            {"code": "1", "label": "Male"},
        ]
        # Single-select: not multivalued.
        assert "multivalued" not in sex

    def test_checkbox_carries_multivalued_true(self):
        src = load_redcap_csv(_FIXTURES / "minimal.csv")
        dd = redcap_to_dd(src)
        races = _by_name(dd)["races"]
        assert races["type"] == "permissible_values"
        assert races["multivalued"] is True
        assert [c["code"] for c in races["codes"]] == ["1", "2", "3", "4"]

    def test_yesno_synthesizes_permissible_values(self):
        src = load_redcap_csv(_FIXTURES / "minimal.csv")
        dd = redcap_to_dd(src)
        smoker = _by_name(dd)["is_smoker"]
        assert smoker["type"] == "permissible_values"
        assert smoker["codes"] == [
            {"code": "1", "label": "Yes"},
            {"code": "0", "label": "No"},
        ]
        assert "multivalued" not in smoker

    def test_truefalse_synthesizes_permissible_values(self):
        src = load_redcap_csv(_FIXTURES / "minimal.csv")
        dd = redcap_to_dd(src)
        consent = _by_name(dd)["consent"]
        assert consent["type"] == "permissible_values"
        assert consent["codes"] == [
            {"code": "1", "label": "True"},
            {"code": "0", "label": "False"},
        ]

    def test_calc_collapses_to_decimal(self):
        src = load_redcap_csv(_FIXTURES / "minimal.csv")
        dd = redcap_to_dd(src)
        bmi = _by_name(dd)["bmi"]
        assert bmi["type"] == "decimal"
        # The calculation expression is dropped (lossy).
        assert "codes" not in bmi

    def test_descriptive_rows_filtered_out(self):
        src = load_redcap_csv(_FIXTURES / "minimal.csv")
        dd = redcap_to_dd(src)
        assert "intro_text" not in _by_name(dd)

    def test_required_only_emitted_when_y(self):
        # `races` has empty Required Field; should not get required=False.
        src = load_redcap_csv(_FIXTURES / "minimal.csv")
        dd = redcap_to_dd(src)
        assert "required" not in _by_name(dd)["races"]

    def test_validation_number_maps_to_decimal_with_floats(self):
        src = load_redcap_csv(_FIXTURES / "validations.csv")
        dd = redcap_to_dd(src)
        weight = _by_name(dd)["weight_kg"]
        assert weight["type"] == "decimal"
        assert weight["min"] == 0.5
        assert weight["max"] == 500.0

    def test_validation_date_maps_to_date(self):
        src = load_redcap_csv(_FIXTURES / "validations.csv")
        dd = redcap_to_dd(src)
        assert _by_name(dd)["birth_date"]["type"] == "date"

    def test_validation_time_maps_to_time(self):
        src = load_redcap_csv(_FIXTURES / "validations.csv")
        dd = redcap_to_dd(src)
        assert _by_name(dd)["visit_time"]["type"] == "time"

    def test_validation_datetime_maps_to_datetime(self):
        src = load_redcap_csv(_FIXTURES / "validations.csv")
        dd = redcap_to_dd(src)
        assert _by_name(dd)["visit_dt"]["type"] == "datetime"

    def test_validation_email_collapses_to_string(self):
        src = load_redcap_csv(_FIXTURES / "validations.csv")
        dd = redcap_to_dd(src)
        assert _by_name(dd)["contact_email"]["type"] == "string"

    def test_validation_zipcode_collapses_to_string(self):
        src = load_redcap_csv(_FIXTURES / "validations.csv")
        dd = redcap_to_dd(src)
        assert _by_name(dd)["zip"]["type"] == "string"

    def test_notes_field_type_maps_to_string(self):
        src = load_redcap_csv(_FIXTURES / "validations.csv")
        dd = redcap_to_dd(src)
        assert _by_name(dd)["notes_free"]["type"] == "string"


# ----------------------------------------------------------------------
# Reverse direction (DD → REDCap) — Python helper.
# ----------------------------------------------------------------------


@_REVERSE_REQUIRES_LINKML_MAP_053
class TestDDToRedcap:
    def test_minimal_string(self):
        source = {
            "entries": [
                {"name": "x", "type": "string", "description": "y"},
            ]
        }
        result = dd_to_redcap(source)
        assert result["entries"][0] == {
            "field_name": "x",
            "field_type": "text",
            "field_note": "y",
        }

    def test_label_maps_to_field_label(self):
        source = {"entries": [{"name": "x", "type": "string", "label": "X"}]}
        result = dd_to_redcap(source)
        assert result["entries"][0]["field_label"] == "X"

    def test_integer_maps_to_text_with_validation(self):
        source = {
            "entries": [
                {"name": "age", "type": "integer", "min": 0, "max": 120, "unit": "years"}
            ]
        }
        entry = dd_to_redcap(source)["entries"][0]
        assert entry["field_type"] == "text"
        assert entry["text_validation_type"] == "integer"
        assert entry["text_validation_min"] == "0"
        assert entry["text_validation_max"] == "120"

    def test_decimal_maps_to_text_with_number(self):
        source = {
            "entries": [
                {"name": "w", "type": "decimal", "min": 0.5, "max": 500.0, "unit": "kg"}
            ]
        }
        entry = dd_to_redcap(source)["entries"][0]
        assert entry["field_type"] == "text"
        assert entry["text_validation_type"] == "number"

    def test_date_maps_to_text_date_ymd(self):
        source = {"entries": [{"name": "d", "type": "date"}]}
        entry = dd_to_redcap(source)["entries"][0]
        assert entry["field_type"] == "text"
        assert entry["text_validation_type"] == "date_ymd"

    def test_permissible_values_default_to_radio(self):
        source = {
            "entries": [
                {
                    "name": "sex",
                    "type": "permissible_values",
                    "codes": [
                        {"code": "0", "label": "Female"},
                        {"code": "1", "label": "Male"},
                    ],
                }
            ]
        }
        entry = dd_to_redcap(source)["entries"][0]
        assert entry["field_type"] == "radio"
        assert (
            entry["choices_calculations_or_slider_labels"]
            == "0, Female | 1, Male"
        )

    def test_multivalued_permissible_values_become_checkbox(self):
        source = {
            "entries": [
                {
                    "name": "races",
                    "type": "permissible_values",
                    "multivalued": True,
                    "codes": [
                        {"code": "1", "label": "White"},
                        {"code": "2", "label": "Black"},
                    ],
                }
            ]
        }
        entry = dd_to_redcap(source)["entries"][0]
        assert entry["field_type"] == "checkbox"

    def test_required_true_becomes_y(self):
        source = {
            "entries": [{"name": "x", "type": "string", "required": True}]
        }
        entry = dd_to_redcap(source)["entries"][0]
        assert entry["required_field"] == "y"

    def test_required_false_or_missing_omitted(self):
        source = {"entries": [{"name": "x", "type": "string"}]}
        entry = dd_to_redcap(source)["entries"][0]
        assert "required_field" not in entry
