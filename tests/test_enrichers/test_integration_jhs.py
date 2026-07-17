"""End-to-end enrichment tests against a realistic dbGaP fixture.

Pipeline for both tests:

1. Load a canonical DD produced by the dbGaP adapter (vendored as
   ``JHS_Subject.dd.yaml``).
2. Run inference on a synthesized JHS-shaped TSV.
3. Enrich.
4. Assert the right metadata flowed across and the right conflicts
   were surfaced.

Two scenarios exercise different branches of the enricher:

- :func:`test_union_path_with_forced_enum_threshold` — drives inference
  to enum-ify CONSENT (small fixture + bumped threshold), then the
  enricher merges DD labels into the existing enum and detects the
  CONSENT=9 value as data-not-in-DD.
- :func:`test_incomplete_dd_path_with_default_threshold` — uses
  inference at default settings, so CONSENT stays integer; the new
  count-based heuristic detects that the DD's 5 codes can't cover
  the 5 observed distinct values and refuses to upgrade. Also picks
  up SEX as a primitive type conflict (DD says string, inference saw
  integer).
"""

from __future__ import annotations

import logging
from pathlib import Path

import yaml

from schema_automator.enrichers import enrich_with_data_dictionary
from schema_automator.generalizers.csv_data_generalizer import CsvDataGeneralizer


_FIXTURES = Path(__file__).resolve().parents[1] / "resources" / "dbgap"


def _by_name(schema):
    return {sn: s for sn, s in schema.slots.items()}


def _load_dd():
    with (_FIXTURES / "JHS_Subject.dd.yaml").open() as f:
        return yaml.safe_load(f)


def test_union_path_with_forced_enum_threshold(caplog):
    """Inference enum-ifies CONSENT; enricher merges DD labels into the
    existing enum and surfaces CONSENT=9 (data-not-in-DD)."""
    dd = _load_dd()

    gen = CsvDataGeneralizer(
        column_separator="\t",
        infer_enum_from_integers=True,
        # Bump from the 0.1 default so the small fixture (10 rows, 5
        # distinct CONSENT values) still exercises the enum branch —
        # the same path a real-sized dbGaP table would take at the
        # default threshold.
        enum_threshold=1.0,
    )
    schema = gen.convert(
        str(_FIXTURES / "JHS_Subject.data.tsv"),
        class_name="Subject",
        schema_name="jhs",
    )

    inferred = _by_name(schema)
    assert inferred["CONSENT"].description in (None, "", "CONSENT")
    assert not inferred["CONSENT"].slot_uri

    with caplog.at_level(logging.WARNING):
        report = enrich_with_data_dictionary(schema, dd)

    enriched = _by_name(schema)

    # Metadata from the DD that inference can't see on its own.
    assert enriched["CONSENT"].description == "Consent group as determined by DAC"
    assert enriched["SUBJECT_ID"].description == "Subject ID"
    assert enriched["CONSENT"].slot_uri == "dbgap:phv00124546.v4"
    assert enriched["SUBJECT_ID"].slot_uri == "dbgap:phv00124545.v4"

    # CONSENT became (or stayed) an enum carrying the DD's long labels.
    consent_range = enriched["CONSENT"].range
    assert consent_range in schema.enums
    consent_pvs = schema.enums[consent_range].permissible_values
    assert consent_pvs["1"].title == "Health/Medical/Biomedical (IRB, NPU) (HMB-IRB-NPU)"
    assert "Disease-Specific" in consent_pvs["4"].title

    # The undeclared CONSENT=9 from the data is preserved in the enum
    # and surfaced in the report.
    assert "9" in consent_pvs
    assert ("CONSENT", ["9"]) in report.extra_data_codes
    assert any(
        "CONSENT" in r.message and "9" in r.message for r in caplog.records
    )

    # SUBJECT_ID's inferred string range matches DD's declared string —
    # no type conflict.
    assert "SUBJECT_ID" not in {tup[0] for tup in report.type_conflicts}


def test_incomplete_dd_path_with_default_threshold(caplog):
    """At default thresholds, CONSENT stays primitive integer. The
    count heuristic refuses to upgrade (DD declares 5 codes, inference
    saw 5 distinct values — by pigeonhole the DD can't cover all
    observed values without value-level verification). SEX surfaces as
    a primitive type conflict (DD says string, inference saw integer)."""
    dd = _load_dd()

    gen = CsvDataGeneralizer(
        column_separator="\t",
        infer_enum_from_integers=True,
    )
    schema = gen.convert(
        str(_FIXTURES / "JHS_Subject.data.tsv"),
        class_name="Subject",
        schema_name="jhs",
    )

    # Inference at default settings: CONSENT and SEX both stay
    # primitive (their distinct-value ratios exceed enum_threshold=0.1).
    assert schema.slots["CONSENT"].range == "integer"
    assert schema.slots["SEX"].range == "integer"

    with caplog.at_level(logging.WARNING):
        report = enrich_with_data_dictionary(schema, dd)

    # ---- Incomplete-DD heuristic on CONSENT. ----

    # The enricher kept CONSENT's primitive integer range and refused
    # to collapse the data into the DD's 5-code enum.
    assert schema.slots["CONSENT"].range == "integer"
    assert "CONSENT_enum" not in schema.enums
    # The DD's codes are stashed on the slot as a structured annotation
    # so reconciliation tools (and humans) can still see them.
    declared_ann = schema.slots["CONSENT"].annotations[
        "declared_permissible_values"
    ]
    declared_codes = [c["code"] for c in declared_ann.value]
    assert declared_codes == ["0", "1", "2", "3", "4"]
    # The report records the (slot, dd_count, observed_count) triple.
    assert ("CONSENT", 5, 5) in report.incomplete_dd_enums
    # And logged a clear warning.
    assert any(
        "CONSENT" in r.message and "5" in r.message for r in caplog.records
    )

    # ---- Type conflict surface on SEX (Finding #2). ----

    # DD declares SEX as string; inference observed integer values.
    # The conflict is captured in the report and logged; inference's
    # range is preserved unchanged.
    assert ("SEX", "integer", "string") in report.type_conflicts
    assert schema.slots["SEX"].range == "integer"
    assert any(
        "SEX" in r.message and "integer" in r.message and "string" in r.message
        for r in caplog.records
    )

    # ---- Metadata still flows for unconflicted slots. ----
    assert schema.slots["SUBJECT_ID"].description == "Subject ID"
    assert schema.slots["SUBJECT_ID"].slot_uri == "dbgap:phv00124545.v4"
