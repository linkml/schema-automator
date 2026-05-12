"""Tests for the dbGaP variable digest adapter."""

from pathlib import Path

import pytest

from schema_automator.adapters.dbgap import dbgap_to_dd, parse_dbgap_digest


_FIXTURES = Path(__file__).resolve().parents[1] / "resources" / "dbgap"
_JHS_DD = _FIXTURES / "JHS_Subject.data_dict.xml"
_JHS_VR = _FIXTURES / "JHS_Subject.var_report.xml"
_SYNTH_DD = _FIXTURES / "synthetic_numeric.data_dict.xml"
_SYNTH_VR = _FIXTURES / "synthetic_numeric.var_report.xml"


def _entry(dd: dict, name: str) -> dict:
    """Look up an entry in a DD by name."""
    matches = [e for e in dd["entries"] if e["name"] == name]
    assert len(matches) == 1, f"expected one entry for {name!r}, got {len(matches)}"
    return matches[0]


class TestParseDbgapDigest:
    def test_data_dict_only(self):
        merged = parse_dbgap_digest(_JHS_DD)
        assert merged["study_id"] == "phs000286.v7"
        assert merged["data_table_id"] == "pht001920.v6"
        # JHS_Subject has 7 variables
        assert len(merged["variables"]) == 7
        # All values populated as lists (possibly empty)
        assert all(isinstance(v["values"], list) for v in merged["variables"])

    def test_with_var_report(self):
        merged = parse_dbgap_digest(_JHS_DD, _JHS_VR)
        # Var-report enrichment: calculated_type fills in
        consent = next(v for v in merged["variables"] if v["name"] == "CONSENT")
        assert consent["calculated_type"] == "enum_integer"
        # And reported_type from data_dict is preserved
        assert consent["reported_type"] == "encoded value"

    def test_per_consent_group_rows_filtered(self):
        """var_report has phv...c1, phv...c2, ... per-consent-group rows;
        only the total-set rows should appear in the merge."""
        merged = parse_dbgap_digest(_JHS_DD, _JHS_VR)
        # JHS_Subject has 7 phvs in data_dict; var_report has 7*5=35 rows
        # (one total + 4 consent groups per phv). Merge collapses to 7.
        assert len(merged["variables"]) == 7


class TestDbgapToDdJhs:
    """End-to-end on the real JHS_Subject fixture."""

    @pytest.fixture(scope="class")
    def dd(self):
        return dbgap_to_dd(_JHS_DD, _JHS_VR)

    def test_top_level_structure(self, dd):
        assert "entries" in dd
        assert isinstance(dd["entries"], list)
        names = [e["name"] for e in dd["entries"]]
        assert names == [
            "SUBJECT_ID",
            "CONSENT",
            "SUBJECT_SOURCE",
            "SOURCE_SUBJECT_ID",
            "SUBJECT_SOURCE2",
            "SOURCE_SUBJECT_ID2",
            "SEX",
        ]

    def test_per_variable_uri_curie(self, dd):
        # Every entry should carry a dbgap: CURIE retaining the phv id.
        for entry in dd["entries"]:
            assert "uri" in entry
            assert entry["uri"].startswith("dbgap:phv")

    def test_subject_id_is_string(self, dd):
        entry = _entry(dd, "SUBJECT_ID")
        assert entry["type"] == "string"
        assert "codes" not in entry

    def test_consent_is_permissible_values(self, dd):
        entry = _entry(dd, "CONSENT")
        assert entry["type"] == "permissible_values"
        codes = entry["codes"]
        assert len(codes) == 5
        # Codes preserve dbGaP ordering and carry the labels verbatim.
        code_values = [c["code"] for c in codes]
        assert code_values == ["0", "1", "2", "3", "4"]
        # HMB-IRB-NPU label is verbatim — no _sanitize_label-style replacement.
        hmb_irb_npu = next(c for c in codes if c["code"] == "1")
        assert "Health/Medical/Biomedical" in hmb_irb_npu["label"]
        assert "(IRB, NPU)" in hmb_irb_npu["label"]  # comma preserved

    def test_calculated_type_overrides_reported(self, dd):
        # SOURCE_SUBJECT_ID: data_dict says "String", var_report's
        # calculated_type is "integer". Trans-spec prefers calculated_type.
        entry = _entry(dd, "SOURCE_SUBJECT_ID")
        assert entry["type"] == "integer"

    def test_description_carries_through(self, dd):
        entry = _entry(dd, "CONSENT")
        assert entry["description"] == "Consent group as determined by DAC"


class TestDbgapToDdSynthetic:
    """Cases the JHS_Subject fixture doesn't exercise."""

    @pytest.fixture(scope="class")
    def dd(self):
        return dbgap_to_dd(_SYNTH_DD, _SYNTH_VR)

    def test_numeric_min_max_from_var_report(self, dd):
        age = _entry(dd, "age_years")
        assert age["type"] == "integer"
        # Integer columns get int min/max (not strings) so the DD output
        # conforms to the schema's any_of(decimal, "none") on min/max.
        assert age["min"] == 18
        assert age["max"] == 89

    def test_decimal_min_max(self, dd):
        weight = _entry(dd, "weight_kg")
        assert weight["type"] == "decimal"
        # Decimal columns get float min/max.
        assert weight["min"] == 42.5
        assert weight["max"] == 178.3

    def test_num_type_normalizes_to_integer_via_calculated_type(self, dd):
        # data_dict says "num" (non-canonical); var_report calculated_type is
        # "integer" — calculated_type wins.
        height = _entry(dd, "height_cm")
        assert height["type"] == "integer"

    def test_composite_type_with_codes_collapses_to_permissible_values(self, dd):
        # data_dict type "decimal, encoded" with codes — codes win.
        entry = _entry(dd, "composite_type_demo")
        assert entry["type"] == "permissible_values"
        assert {c["code"] for c in entry["codes"]} == {"-9", "-3"}

    def test_empty_type_falls_back_to_calculated_type(self, dd):
        entry = _entry(dd, "missing_type")
        # var_report calculated_type is "string"
        assert entry["type"] == "string"

    def test_typo_in_reported_type_normalizes(self, dd):
        # "sting" is a known dbGaP typo cataloged in the corpus survey;  # codespell:ignore
        # the trans-spec collapses it to "string".
        entry = _entry(dd, "typo_type")
        assert entry["type"] == "string"


class TestDbgapToDdNoVarReport:
    """data_dict.xml alone — no var_report enrichment available."""

    def test_basic_pass(self):
        dd = dbgap_to_dd(_JHS_DD)  # no var_report
        # CONSENT has codes in data_dict, so type promotes regardless.
        entry = _entry(dd, "CONSENT")
        assert entry["type"] == "permissible_values"
        # SUBJECT_ID has reported_type "String" → string (no calculated_type
        # fallback available).
        entry = _entry(dd, "SUBJECT_ID")
        assert entry["type"] == "string"

    def test_subject_id_no_min_max_without_var_report(self):
        dd = dbgap_to_dd(_JHS_DD)
        for entry in dd["entries"]:
            assert "min" not in entry
            assert "max" not in entry
