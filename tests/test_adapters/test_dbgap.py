"""Tests for the dbGaP variable digest adapter."""

from pathlib import Path

import pytest

from schema_automator.adapters.codes import serialize_codes
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


_DEMO_DD = _FIXTURES / "phs000280.v8.pht000001.v1.DEMO.data_dict.xml"
_DEMO_VR = _FIXTURES / "phs000280.v8.pht000001.v1.p2.DEMO.var_report.xml"


class TestDbgapToDdDemo:
    """Fixture pair from linkml/dm-bip#376 covering issue #231."""

    @pytest.fixture(scope="class")
    def dd(self):
        return dbgap_to_dd(_DEMO_DD, _DEMO_VR)

    def test_bare_value_becomes_code(self, dd):
        entry = _entry(dd, "YEAR")
        assert entry["type"] == "permissible_values"
        assert entry["codes"] == [{"code": "1986"}]

    def test_bare_value_serializes_to_tsv(self, dd):
        assert serialize_codes(_entry(dd, "YEAR")["codes"]) == "1986"

    def test_unit_carries_through(self, dd):
        assert _entry(dd, "HEIGHT")["unit"] == "cm"

    def test_undeclared_unit_is_left_empty(self, dd):
        assert "unit" not in _entry(dd, "BOUNDED")

    def test_unit_absent_on_non_numeric(self, dd):
        # SENTINEL declares <unit> but is typed permissible_values for now.
        assert "unit" not in _entry(dd, "SENTINEL")

    def test_logical_bounds_used_without_stats(self, dd):
        entry = _entry(dd, "BOUNDED")
        assert entry["type"] == "integer"
        assert entry["min"] == 10
        assert entry["max"] == 99

    def test_comment_carries_through(self, dd):
        assert _entry(dd, "HEIGHT")["comment"] == "Measured to the nearest cm."

    def test_duplicate_codes_pass_through(self, dd):
        codes = _entry(dd, "DUPCODE")["codes"]
        assert [c["code"] for c in codes] == ["1", "1"]

    def test_data_dict_only(self):
        dd = dbgap_to_dd(_DEMO_DD)
        entry = _entry(dd, "BOUNDED")
        assert (entry["min"], entry["max"]) == (10, 99)
        assert _entry(dd, "YEAR")["codes"] == [{"code": "1986"}]


_BOUNDS_DD = """<?xml version="1.0" encoding="UTF-8"?>
<data_table id="pht000002.v1" study_id="phs000280.v8">
  <variable id="phv00000010.v1">
    <name>AGE</name>
    <description>Age at exam.</description>
    <type>decimal</type>
    <logical_min>0</logical_min>
    <logical_max>120</logical_max>
  </variable>
  <variable id="phv00000012.v1">
    <name>WEIGHT</name>
    <description>Only a declared minimum.</description>
    <type>integer</type>
    <logical_min>1</logical_min>
  </variable>
  <variable id="phv00000011.v1">
    <name>CODE_TEXT</name>
    <description>Declared integer, calculated string.</description>
    <type>integer</type>
    <unit>mg</unit>
    <logical_min>1</logical_min>
  </variable>
</data_table>
"""

_BOUNDS_VR = """<?xml version="1.0" encoding="UTF-8"?>
<data_table name="BOUNDS" dataset_id="pht000002.v1" study_id="phs000280.v8">
  <variable id="phv00000010.v1.p1" var_name="AGE" calculated_type="decimal" reported_type="decimal">
    <total><stats><stat n="10" nulls="0" min="18.5" max="89.25" /></stats></total>
  </variable>
  <variable id="phv00000012.v1.p1" var_name="WEIGHT" calculated_type="integer" reported_type="integer">
    <total><stats><stat n="10" nulls="0" min="40" max="150" /></stats></total>
  </variable>
  <variable id="phv00000011.v1.p1" var_name="CODE_TEXT" calculated_type="string" reported_type="integer">
    <total><stats><stat n="10" nulls="0" min="1" max="9" /></stats></total>
  </variable>
</data_table>
"""


class TestDbgapBounds:
    @pytest.fixture(scope="class")
    def dd(self, tmp_path_factory):
        d = tmp_path_factory.mktemp("bounds")
        (d / "b.data_dict.xml").write_text(_BOUNDS_DD)
        (d / "b.var_report.xml").write_text(_BOUNDS_VR)
        return dbgap_to_dd(d / "b.data_dict.xml", d / "b.var_report.xml")

    def test_declared_bounds_win_over_observed(self, dd):
        entry = _entry(dd, "AGE")
        assert entry["min"] == 0.0
        assert entry["max"] == 120.0

    def test_observed_bound_fills_missing_declared_side(self, dd):
        entry = _entry(dd, "WEIGHT")
        assert entry["min"] == 1
        assert entry["max"] == 150

    def test_calculated_string_suppresses_numeric_fields(self, dd):
        # reported_type says integer, but calculated_type string wins for
        # `type`, so unit/min/max must not appear either.
        entry = _entry(dd, "CODE_TEXT")
        assert entry["type"] == "string"
        for field in ("unit", "min", "max"):
            assert field not in entry
