"""Unit tests for the data-dictionary enricher."""

from __future__ import annotations

import logging

import pytest
from linkml_runtime.linkml_model import (
    Annotation,
    ClassDefinition,
    EnumDefinition,
    PermissibleValue,
    SchemaDefinition,
    SlotDefinition,
)

from schema_automator.enrichers import (
    EnrichmentReport,
    enrich_with_data_dictionary,
)


def _schema_with_slots(**slots: SlotDefinition) -> SchemaDefinition:
    s = SchemaDefinition(id="ex", name="ex")
    s.slots = dict(slots)
    return s


# ----------------------------------------------------------------------
# Metadata layer: DD fills in what inference can't see.
# ----------------------------------------------------------------------


class TestMetadataOverlay:
    def test_description_applied_when_absent(self):
        schema = _schema_with_slots(age=SlotDefinition("age", range="integer"))
        dd = {"entries": [{"name": "age", "type": "integer", "description": "Age in years"}]}
        enrich_with_data_dictionary(schema, dd)
        assert schema.slots["age"].description == "Age in years"

    def test_label_applied_as_title(self):
        schema = _schema_with_slots(age=SlotDefinition("age", range="integer"))
        dd = {"entries": [{"name": "age", "type": "integer", "label": "Age"}]}
        enrich_with_data_dictionary(schema, dd)
        assert schema.slots["age"].title == "Age"

    def test_uri_applied_as_slot_uri(self):
        schema = _schema_with_slots(age=SlotDefinition("age", range="integer"))
        dd = {"entries": [{"name": "age", "type": "integer", "uri": "dbgap:phv00012345.v1"}]}
        enrich_with_data_dictionary(schema, dd)
        assert schema.slots["age"].slot_uri == "dbgap:phv00012345.v1"

    def test_unit_applied(self):
        schema = _schema_with_slots(weight=SlotDefinition("weight", range="float"))
        dd = {"entries": [{"name": "weight", "type": "decimal", "unit": "kg"}]}
        enrich_with_data_dictionary(schema, dd)
        unit = schema.slots["weight"].unit
        assert unit is not None
        # `unit` is a UnitOfMeasure structure with ucum_code on the inside.
        assert getattr(unit, "ucum_code", None) == "kg"

    def test_unit_none_sentinel_skipped(self):
        schema = _schema_with_slots(count=SlotDefinition("count", range="integer"))
        dd = {"entries": [{"name": "count", "type": "integer", "unit": "none"}]}
        enrich_with_data_dictionary(schema, dd)
        assert schema.slots["count"].unit is None

    def test_pattern_applied(self):
        schema = _schema_with_slots(sid=SlotDefinition("sid", range="string"))
        dd = {"entries": [{"name": "sid", "type": "string", "pattern": "^S[0-9]+$"}]}
        enrich_with_data_dictionary(schema, dd)
        assert schema.slots["sid"].pattern == "^S[0-9]+$"

    def test_min_max_applied(self):
        schema = _schema_with_slots(age=SlotDefinition("age", range="integer"))
        dd = {"entries": [{"name": "age", "type": "integer", "min": 0, "max": 120}]}
        enrich_with_data_dictionary(schema, dd)
        slot = schema.slots["age"]
        assert slot.minimum_value == 0
        assert slot.maximum_value == 120

    def test_min_max_none_sentinel_skipped(self):
        schema = _schema_with_slots(age=SlotDefinition("age", range="integer"))
        dd = {"entries": [{"name": "age", "type": "integer", "min": "none", "max": "none"}]}
        enrich_with_data_dictionary(schema, dd)
        slot = schema.slots["age"]
        assert slot.minimum_value is None
        assert slot.maximum_value is None

    def test_multivalued_applied(self):
        schema = _schema_with_slots(tags=SlotDefinition("tags", range="string"))
        dd = {"entries": [{"name": "tags", "type": "string", "multivalued": True}]}
        enrich_with_data_dictionary(schema, dd)
        assert schema.slots["tags"].multivalued is True

    def test_existing_metadata_not_overwritten(self):
        # If inference / a prior pass set a description, the enricher
        # should not overwrite it.
        schema = _schema_with_slots(
            age=SlotDefinition("age", range="integer", description="prior")
        )
        dd = {"entries": [{"name": "age", "type": "integer", "description": "from DD"}]}
        enrich_with_data_dictionary(schema, dd)
        assert schema.slots["age"].description == "prior"


# ----------------------------------------------------------------------
# Constraint layer: required handling with conflict detection.
# ----------------------------------------------------------------------


class TestRequired:
    def test_dd_required_applied(self):
        schema = _schema_with_slots(rid=SlotDefinition("rid", range="string"))
        dd = {"entries": [{"name": "rid", "type": "string", "required": True}]}
        report = enrich_with_data_dictionary(schema, dd)
        assert schema.slots["rid"].required is True
        assert report.required_conflicts == []

    def test_dd_required_conflicts_with_inferred_optional(self):
        schema = _schema_with_slots(
            x=SlotDefinition("x", range="string", required=False)
        )
        dd = {"entries": [{"name": "x", "type": "string", "required": True}]}
        report = enrich_with_data_dictionary(schema, dd)
        assert schema.slots["x"].required is True
        assert "x" in report.required_conflicts


# ----------------------------------------------------------------------
# Type layer: inference wins on conflict.
# ----------------------------------------------------------------------


class TestTypeConsistency:
    def test_matching_types_no_conflict(self):
        schema = _schema_with_slots(age=SlotDefinition("age", range="integer"))
        dd = {"entries": [{"name": "age", "type": "integer"}]}
        report = enrich_with_data_dictionary(schema, dd)
        assert report.type_conflicts == []

    def test_dd_says_integer_inference_says_string_logs_conflict(self, caplog):
        schema = _schema_with_slots(sid=SlotDefinition("sid", range="string"))
        dd = {"entries": [{"name": "sid", "type": "integer"}]}
        with caplog.at_level(logging.WARNING):
            report = enrich_with_data_dictionary(schema, dd)
        assert report.type_conflicts == [("sid", "string", "integer")]
        # Inference wins — range is unchanged.
        assert schema.slots["sid"].range == "string"
        assert any("Type conflict on 'sid'" in r.message for r in caplog.records)

    def test_decimal_dd_matches_float_range(self):
        # DD's 'decimal' maps to LinkML 'float' in this codebase.
        schema = _schema_with_slots(w=SlotDefinition("w", range="float"))
        dd = {"entries": [{"name": "w", "type": "decimal"}]}
        report = enrich_with_data_dictionary(schema, dd)
        assert report.type_conflicts == []

    def test_non_enum_suffix_enum_range_skipped(self):
        # Importers don't all suffix enum names with ``_enum``;
        # ``jsonschema_import_engine``, for instance, uses ``_options``.
        # The check that "this slot's range is an enum" must use
        # schema.enums membership, not name-suffix heuristics.
        schema = SchemaDefinition(id="ex", name="ex")
        schema.slots["color"] = SlotDefinition("color", range="color_options")
        schema.enums["color_options"] = EnumDefinition(
            name="color_options",
            permissible_values={"red": PermissibleValue(text="red")},
        )
        # DD declares the slot as 'string'. Old suffix-based check
        # would log a spurious type conflict; new membership-based
        # check correctly recognizes the range as an enum.
        dd = {"entries": [{"name": "color", "type": "string"}]}
        report = enrich_with_data_dictionary(schema, dd)
        assert report.type_conflicts == []


# ----------------------------------------------------------------------
# Permissible-value layer: union with logged diffs.
# ----------------------------------------------------------------------


class TestPermissibleValues:
    def _schema_with_enum(self, slot_name: str, codes: list[str]) -> SchemaDefinition:
        enum_name = f"{slot_name}_enum"
        schema = SchemaDefinition(id="ex", name="ex")
        schema.slots[slot_name] = SlotDefinition(slot_name, range=enum_name)
        schema.enums[enum_name] = EnumDefinition(
            name=enum_name,
            permissible_values={c: PermissibleValue(text=c) for c in codes},
        )
        return schema

    def test_dd_labels_merged_into_inferred_enum(self):
        schema = self._schema_with_enum("sex", ["0", "1"])
        dd = {
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
        report = enrich_with_data_dictionary(schema, dd)
        pvs = schema.enums["sex_enum"].permissible_values
        assert pvs["0"].title == "Female"
        assert pvs["1"].title == "Male"
        assert report.is_clean

    def test_codes_in_dd_not_in_data_kept_and_logged(self):
        schema = self._schema_with_enum("sex", ["0", "1"])
        dd = {
            "entries": [
                {
                    "name": "sex",
                    "type": "permissible_values",
                    "codes": [
                        {"code": "0", "label": "Female"},
                        {"code": "1", "label": "Male"},
                        {"code": "9", "label": "Unknown"},
                    ],
                }
            ]
        }
        report = enrich_with_data_dictionary(schema, dd)
        pvs = schema.enums["sex_enum"].permissible_values
        assert "9" in pvs  # Kept in enriched enum.
        assert pvs["9"].title == "Unknown"
        assert report.extra_dd_codes == [("sex", ["9"])]

    def test_codes_in_data_not_in_dd_kept_and_logged(self, caplog):
        schema = self._schema_with_enum("sex", ["0", "1", "9"])
        dd = {
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
        with caplog.at_level(logging.WARNING):
            report = enrich_with_data_dictionary(schema, dd)
        pvs = schema.enums["sex_enum"].permissible_values
        assert "9" in pvs
        assert report.extra_data_codes == [("sex", ["9"])]
        assert any("'sex'" in r.message and "['9']" in r.message for r in caplog.records)

    def test_permissible_values_dd_on_inferred_string_creates_enum(self):
        # No enum exists, no num_distinct_values annotation: fall back
        # to the "upgrade primitive to enum" path.
        schema = _schema_with_slots(consent=SlotDefinition("consent", range="string"))
        dd = {
            "entries": [
                {
                    "name": "consent",
                    "type": "permissible_values",
                    "codes": [
                        {"code": "0", "label": "Did not participate"},
                        {"code": "1", "label": "Consented"},
                    ],
                }
            ]
        }
        enrich_with_data_dictionary(schema, dd)
        slot = schema.slots["consent"]
        assert slot.range == "consent_enum"
        assert "consent_enum" in schema.enums
        pvs = schema.enums["consent_enum"].permissible_values
        # JsonObj wraps the dict on read; use __contains__ rather than .keys().
        assert "0" in pvs
        assert "1" in pvs
        assert pvs["0"].title == "Did not participate"

    def test_per_code_uri_becomes_meaning(self):
        schema = self._schema_with_enum("term", ["A"])
        dd = {
            "entries": [
                {
                    "name": "term",
                    "type": "permissible_values",
                    "codes": [{"code": "A", "label": "Apple", "uri": "OBO:0001"}],
                }
            ]
        }
        enrich_with_data_dictionary(schema, dd)
        pv = schema.enums["term_enum"].permissible_values["A"]
        assert pv.meaning == "OBO:0001"


# ----------------------------------------------------------------------
# Incomplete-DD heuristic: when inference recorded num_distinct_values
# and DD declares fewer codes than were observed, the enricher refuses
# to collapse the inferred primitive range into the DD's enum.
# ----------------------------------------------------------------------


def _slot_with_distinct(
    name: str, range_: str, num_distinct: int
) -> SlotDefinition:
    """Helper: build a slot annotated as if inference observed
    ``num_distinct`` distinct values."""
    slot = SlotDefinition(name, range=range_)
    slot.annotations["num_distinct_values"] = Annotation(
        tag="num_distinct_values", value=str(num_distinct)
    )
    return slot


class TestIncompleteDdHeuristic:
    def test_dd_smaller_than_observed_refuses_upgrade(self):
        # Inference saw 6 distinct values; DD declares 5 codes.
        # Provably incomplete by count — keep primitive range.
        schema = SchemaDefinition(id="ex", name="ex")
        schema.slots["consent"] = _slot_with_distinct("consent", "integer", 6)
        dd = {
            "entries": [
                {
                    "name": "consent",
                    "type": "permissible_values",
                    "codes": [
                        {"code": "0", "label": "C0"},
                        {"code": "1", "label": "C1"},
                        {"code": "2", "label": "C2"},
                        {"code": "3", "label": "C3"},
                        {"code": "4", "label": "C4"},
                    ],
                }
            ]
        }
        report = enrich_with_data_dictionary(schema, dd)
        slot = schema.slots["consent"]
        assert slot.range == "integer"  # not upgraded
        assert "consent_enum" not in schema.enums
        # DD codes stashed on the slot as annotation.
        ann = slot.annotations["declared_permissible_values"]
        assert ann.tag == "declared_permissible_values"
        assert [c["code"] for c in ann.value] == ["0", "1", "2", "3", "4"]
        # Report records the incompleteness.
        assert ("consent", 5, 6) in report.incomplete_dd_enums

    def test_dd_equal_to_observed_treated_as_incomplete(self):
        # Equality is conservative: same code count doesn't guarantee
        # the sets match, so treat as could-be-incomplete.
        schema = SchemaDefinition(id="ex", name="ex")
        schema.slots["x"] = _slot_with_distinct("x", "integer", 3)
        dd = {
            "entries": [
                {
                    "name": "x",
                    "type": "permissible_values",
                    "codes": [
                        {"code": "a"},
                        {"code": "b"},
                        {"code": "c"},
                    ],
                }
            ]
        }
        report = enrich_with_data_dictionary(schema, dd)
        assert schema.slots["x"].range == "integer"
        assert ("x", 3, 3) in report.incomplete_dd_enums

    def test_dd_larger_than_observed_upgrades(self):
        # DD declares more codes than were observed — DD plausibly
        # covers the data; do the upgrade.
        schema = SchemaDefinition(id="ex", name="ex")
        schema.slots["sex"] = _slot_with_distinct("sex", "integer", 2)
        dd = {
            "entries": [
                {
                    "name": "sex",
                    "type": "permissible_values",
                    "codes": [
                        {"code": "0", "label": "Female"},
                        {"code": "1", "label": "Male"},
                        {"code": "9", "label": "Unknown"},
                    ],
                }
            ]
        }
        report = enrich_with_data_dictionary(schema, dd)
        slot = schema.slots["sex"]
        assert slot.range == "sex_enum"
        assert "sex_enum" in schema.enums
        assert report.incomplete_dd_enums == []

    def test_no_distinct_value_annotation_falls_back_to_upgrade(self):
        # Without the annotation, the enricher can't apply the
        # heuristic and keeps backwards-compatible upgrade behavior.
        schema = _schema_with_slots(x=SlotDefinition("x", range="string"))
        dd = {
            "entries": [
                {
                    "name": "x",
                    "type": "permissible_values",
                    "codes": [{"code": "a"}, {"code": "b"}],
                }
            ]
        }
        report = enrich_with_data_dictionary(schema, dd)
        assert schema.slots["x"].range == "x_enum"
        assert report.incomplete_dd_enums == []

    def test_existing_enum_range_unaffected_by_heuristic(self):
        # If inference already produced an enum, we still merge (the
        # heuristic only governs the upgrade decision for primitive
        # ranges).
        schema = SchemaDefinition(id="ex", name="ex")
        schema.slots["c"] = SlotDefinition("c", range="c_enum")
        # Annotate as if 3 distinct values were observed, even though
        # DD declares only 2 codes. With an existing enum, the
        # heuristic shouldn't fire.
        schema.slots["c"].annotations["num_distinct_values"] = Annotation(
            tag="num_distinct_values", value="3"
        )
        schema.enums["c_enum"] = EnumDefinition(
            name="c_enum",
            permissible_values={
                "x": PermissibleValue(text="x"),
                "y": PermissibleValue(text="y"),
                "z": PermissibleValue(text="z"),
            },
        )
        dd = {
            "entries": [
                {
                    "name": "c",
                    "type": "permissible_values",
                    "codes": [{"code": "x", "label": "Ex"}, {"code": "y", "label": "Why"}],
                }
            ]
        }
        report = enrich_with_data_dictionary(schema, dd)
        # Existing enum is retained and merged.
        assert schema.slots["c"].range == "c_enum"
        # The 'z' code (observed, not in DD) is logged as extra_data_codes.
        assert ("c", ["z"]) in report.extra_data_codes
        # No incomplete-DD log — that's only for primitive→enum upgrades.
        assert report.incomplete_dd_enums == []


# ----------------------------------------------------------------------
# Unmatched entries (DD declares a column that's not in the data).
# ----------------------------------------------------------------------


class TestUnmatched:
    def test_unmatched_dd_entry_logged(self, caplog):
        schema = _schema_with_slots(x=SlotDefinition("x", range="string"))
        dd = {
            "entries": [
                {"name": "x", "type": "string"},
                {"name": "missing", "type": "string"},
            ]
        }
        with caplog.at_level(logging.WARNING):
            report = enrich_with_data_dictionary(schema, dd)
        assert report.unmatched_dd_entries == ["missing"]
        assert any("'missing'" in r.message for r in caplog.records)

    def test_pandera_shape_short_circuits_with_single_warning(self, caplog):
        # PandasDataGeneralizer leaves schema.slots empty and puts
        # inferred slots on each class's `attributes` inline. The
        # enricher should detect this shape, emit one explanatory
        # warning, and return without enrichment — not log "unmatched"
        # warnings for every DD entry.
        schema = SchemaDefinition(id="ex", name="ex")
        cls = ClassDefinition(name="Obs")
        cls.attributes["age"] = SlotDefinition("age", range="integer")
        cls.attributes["sex"] = SlotDefinition("sex", range="integer")
        schema.classes["Obs"] = cls
        dd = {
            "entries": [
                {"name": "age", "type": "integer", "description": "Age"},
                {"name": "sex", "type": "integer", "description": "Sex"},
            ]
        }
        with caplog.at_level(logging.WARNING):
            report = enrich_with_data_dictionary(schema, dd)
        # Empty report — no entries were processed.
        assert report.unmatched_dd_entries == []
        assert report.is_clean
        # One warning, not per-entry noise.
        warns = [r for r in caplog.records if r.levelname == "WARNING"]
        assert len(warns) == 1
        assert "pandera" in warns[0].message.lower() or "attributes" in warns[0].message.lower()


# ----------------------------------------------------------------------
# Report.
# ----------------------------------------------------------------------


class TestEnrichmentReport:
    def test_is_clean_when_no_discrepancies(self):
        schema = _schema_with_slots(age=SlotDefinition("age", range="integer"))
        dd = {"entries": [{"name": "age", "type": "integer", "description": "Age"}]}
        report = enrich_with_data_dictionary(schema, dd)
        assert report.is_clean

    def test_is_not_clean_when_discrepancies(self):
        schema = _schema_with_slots(sid=SlotDefinition("sid", range="string"))
        dd = {"entries": [{"name": "sid", "type": "integer"}]}
        report = enrich_with_data_dictionary(schema, dd)
        assert not report.is_clean
