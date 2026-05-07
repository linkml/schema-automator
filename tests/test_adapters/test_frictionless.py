"""Tests for the Frictionless ↔ DD adapter."""

import json
from pathlib import Path

import pytest

from schema_automator.adapters.frictionless.adapter import (
    dd_to_frictionless,
    frictionless_to_dd,
)


# ----------------------------------------------------------------------
# Forward direction (Frictionless → DD) — driven by the trans-spec.
# ----------------------------------------------------------------------


class TestFrictionlessToDD:
    def test_minimal_field(self):
        source = {
            "fields": [
                {"name": "subject_id", "type": "string"},
            ]
        }
        result = frictionless_to_dd(source)
        assert result == {"entries": [{"name": "subject_id", "type": "string"}]}

    def test_title_maps_to_label(self):
        source = {"fields": [{"name": "x", "title": "The X", "type": "string"}]}
        result = frictionless_to_dd(source)
        assert result["entries"][0]["label"] == "The X"

    def test_description_passes_through(self):
        source = {
            "fields": [
                {"name": "x", "type": "string", "description": "An X column."},
            ]
        }
        result = frictionless_to_dd(source)
        assert result["entries"][0]["description"] == "An X column."

    def test_rdfType_maps_to_uri(self):
        source = {
            "fields": [
                {"name": "x", "type": "string", "rdfType": "http://example.org/concept/1"},
            ]
        }
        result = frictionless_to_dd(source)
        assert result["entries"][0]["uri"] == "http://example.org/concept/1"

    def test_type_vocabulary_translation(self):
        cases = {
            "string": "string",
            "number": "decimal",
            "integer": "integer",
            "year": "integer",  # collapses
            "boolean": "boolean",
            "date": "date",
            "time": "time",
            "datetime": "datetime",
            "object": "string",  # collapses
            "array": "string",  # collapses
            "yearmonth": "string",
            "duration": "string",
            "geopoint": "string",
            "geojson": "string",
            "any": "string",
        }
        for fts_type, dd_type in cases.items():
            source = {"fields": [{"name": "x", "type": fts_type}]}
            result = frictionless_to_dd(source)
            assert result["entries"][0]["type"] == dd_type, f"{fts_type} → expected {dd_type}"

    def test_enum_promotes_type_to_permissible_values(self):
        source = {
            "fields": [
                {"name": "x", "type": "string", "constraints": {"enum": ["A", "B", "C"]}},
            ]
        }
        result = frictionless_to_dd(source)
        entry = result["entries"][0]
        assert entry["type"] == "permissible_values"
        assert entry["codes"] == [{"code": "A"}, {"code": "B"}, {"code": "C"}]

    def test_enum_promotes_even_when_source_type_is_integer(self):
        source = {
            "fields": [
                {"name": "x", "type": "integer", "constraints": {"enum": ["1", "0"]}},
            ]
        }
        result = frictionless_to_dd(source)
        assert result["entries"][0]["type"] == "permissible_values"

    def test_numeric_min_max_coerce_to_numbers(self):
        source = {
            "fields": [
                {
                    "name": "age",
                    "type": "integer",
                    "constraints": {"minimum": "0", "maximum": "120"},
                },
            ]
        }
        result = frictionless_to_dd(source)
        entry = result["entries"][0]
        assert entry["min"] == 0
        assert entry["max"] == 120

    def test_decimal_min_max_coerce_to_floats(self):
        source = {
            "fields": [
                {
                    "name": "weight",
                    "type": "number",
                    "constraints": {"minimum": "0.5", "maximum": "500.0"},
                },
            ]
        }
        result = frictionless_to_dd(source)
        entry = result["entries"][0]
        assert entry["min"] == 0.5
        assert entry["max"] == 500.0

    def test_non_numeric_min_max_dropped(self):
        # Frictionless date-typed minimum/maximum aren't expressible in DD.
        source = {
            "fields": [
                {
                    "name": "event",
                    "type": "date",
                    "constraints": {"minimum": "2020-01-01", "maximum": "2030-12-31"},
                },
            ]
        }
        result = frictionless_to_dd(source)
        entry = result["entries"][0]
        assert "min" not in entry
        assert "max" not in entry

    def test_required_pattern_carry_through(self):
        source = {
            "fields": [
                {
                    "name": "id",
                    "type": "string",
                    "constraints": {"required": True, "pattern": "^X[0-9]+$"},
                },
            ]
        }
        result = frictionless_to_dd(source)
        entry = result["entries"][0]
        assert entry["required"] is True
        assert entry["pattern"] == "^X[0-9]+$"

    def test_example_wraps_to_list(self):
        source = {"fields": [{"name": "x", "type": "string", "example": "foo"}]}
        result = frictionless_to_dd(source)
        assert result["entries"][0]["example_values"] == ["foo"]

    def test_real_world_finance_vix(self):
        """Validate against a real public Frictionless data package."""
        pkg_path = Path("/tmp/finance-vix/datapackage.json")
        if not pkg_path.exists():
            pytest.skip("finance-vix fixture not present at /tmp")
        pkg = json.load(open(pkg_path))
        schema = next(r["schema"] for r in pkg["resources"] if r["name"] == "vix-daily")
        result = frictionless_to_dd(schema)
        names = [e["name"] for e in result["entries"]]
        assert names == ["DATE", "OPEN", "HIGH", "LOW", "CLOSE"]
        assert result["entries"][0]["type"] == "date"
        assert all(e["type"] == "decimal" for e in result["entries"][1:])


# ----------------------------------------------------------------------
# Reverse direction (DD → Frictionless) — Python helper.
# ----------------------------------------------------------------------


class TestDDToFrictionless:
    def test_minimal_field(self):
        source = {"entries": [{"name": "x", "type": "string", "description": "y"}]}
        result = dd_to_frictionless(source)
        assert result == {
            "fields": [{"name": "x", "type": "string", "description": "y"}]
        }

    def test_label_maps_to_title(self):
        source = {"entries": [{"name": "x", "type": "string", "label": "X Label"}]}
        result = dd_to_frictionless(source)
        assert result["fields"][0]["title"] == "X Label"

    def test_uri_maps_to_rdfType(self):
        source = {"entries": [{"name": "x", "type": "string", "uri": "X:1"}]}
        result = dd_to_frictionless(source)
        assert result["fields"][0]["rdfType"] == "X:1"

    def test_type_vocabulary_translation(self):
        cases = {
            "string": "string",
            "integer": "integer",
            "decimal": "number",
            "boolean": "boolean",
            "date": "date",
            "time": "time",
            "datetime": "datetime",
            "uri": "string",  # collapses
            "curie": "string",  # collapses
            "permissible_values": "string",  # base type
        }
        for dd_type, fts_type in cases.items():
            source = {"entries": [{"name": "x", "type": dd_type}]}
            result = dd_to_frictionless(source)
            assert result["fields"][0]["type"] == fts_type, (
                f"{dd_type} → expected {fts_type}"
            )

    def test_codes_become_enum_constraint(self):
        source = {
            "entries": [
                {
                    "name": "sex",
                    "type": "permissible_values",
                    "codes": [
                        {"code": "F", "label": "Female"},
                        {"code": "M", "label": "Male"},
                    ],
                }
            ]
        }
        result = dd_to_frictionless(source)
        # Labels are dropped (Frictionless enum is just values).
        assert result["fields"][0]["constraints"]["enum"] == ["F", "M"]

    def test_min_max_serialize_as_strings(self):
        source = {
            "entries": [
                {"name": "age", "type": "integer", "min": 0, "max": 120, "unit": "years"}
            ]
        }
        result = dd_to_frictionless(source)
        c = result["fields"][0]["constraints"]
        assert c["minimum"] == "0"
        assert c["maximum"] == "120"

    def test_none_sentinel_dropped(self):
        source = {
            "entries": [
                {"name": "x", "type": "decimal", "min": "none", "max": "none", "unit": "kg"}
            ]
        }
        result = dd_to_frictionless(source)
        c = result["fields"][0].get("constraints", {})
        assert "minimum" not in c
        assert "maximum" not in c

    def test_unit_dropped(self):
        # DD `unit` has no Frictionless equivalent.
        source = {"entries": [{"name": "x", "type": "integer", "unit": "kg", "min": 0, "max": 1}]}
        result = dd_to_frictionless(source)
        assert "unit" not in result["fields"][0]
        assert "unit" not in result["fields"][0].get("constraints", {})

    def test_example_values_first_becomes_example(self):
        source = {
            "entries": [
                {"name": "x", "type": "string", "example_values": ["A", "B"]}
            ]
        }
        result = dd_to_frictionless(source)
        # Frictionless example is scalar — first wins.
        assert result["fields"][0]["example"] == "A"
