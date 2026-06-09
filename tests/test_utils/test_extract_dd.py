"""Tests for projecting a LinkML schema into the canonical DD format."""

from pathlib import Path
from textwrap import dedent

import pytest
from linkml_runtime.utils.schemaview import SchemaView

from schema_automator.utils.extract_dd import (
    dd_to_tsv,
    projectable_classes,
    schema_to_dd,
)


_SCHEMA = """
id: https://example.org/t
name: test_schema
prefixes:
  linkml: https://w3id.org/linkml/
  schema: http://schema.org/
  ex: https://example.org/
default_range: string
imports: [linkml:types]
classes:
  Base:
    slots: [record_id]
  Person:
    is_a: Base
    slots:
      - full_name
      - age
      - score
      - status
      - height
      - email
      - tags
      - homepage
      - address
  Address:
    slots: [city]
  Mixinish:
    mixin: true
  AbstractThing:
    abstract: true
slots:
  record_id:
    identifier: true
    range: string
  full_name:
    range: string
    description: The person's full name
    title: Full Name
  age:
    range: integer
    minimum_value: 0
    maximum_value: 120
  score:
    range: integer
  status:
    range: StatusEnum
  height:
    range: float
    unit:
      ucum_code: cm
  email:
    range: string
    pattern: "[a-z]+"
  tags:
    range: string
    multivalued: true
  homepage:
    range: uri
    slot_uri: schema:url
  address:
    range: Address
  city:
    range: string
enums:
  StatusEnum:
    permissible_values:
      ACTIVE:
        title: Active
        description: Currently active
        meaning: ex:Active
      INACTIVE:
        title: Inactive
"""


@pytest.fixture(scope="module")
def sv(tmp_path_factory) -> SchemaView:
    path = tmp_path_factory.mktemp("extract_dd") / "schema.yaml"
    path.write_text(dedent(_SCHEMA).strip() + "\n")
    return SchemaView(str(path))


@pytest.fixture(scope="module")
def person_entries(sv) -> dict:
    dd = schema_to_dd(sv, "Person")
    return {e["name"]: e for e in dd["entries"]}


def test_inherited_slot_included(person_entries):
    # record_id comes from Base via is_a; class_induced_slots picks it up.
    assert "record_id" in person_entries
    assert person_entries["record_id"]["type"] == "string"
    # description is required by the DD; a slot without one gets "".
    assert person_entries["record_id"]["description"] == ""


def test_metadata_carried(person_entries):
    e = person_entries["full_name"]
    assert e["type"] == "string"
    assert e["description"] == "The person's full name"
    assert e["label"] == "Full Name"
    # unit/min/max are numeric-only; a string slot must not carry them.
    assert "unit" not in e and "min" not in e and "max" not in e


def test_numeric_with_bounds_gets_none_unit(person_entries):
    e = person_entries["age"]
    assert e["type"] == "integer"
    assert e["min"] == 0
    assert e["max"] == 120
    # unit undeclared on a numeric slot → explicit `none` sentinel.
    assert e["unit"] == "none"


def test_numeric_bare_gets_all_none_sentinels(person_entries):
    e = person_entries["score"]
    assert e["type"] == "integer"
    assert e["unit"] == "none"
    assert e["min"] == "none"
    assert e["max"] == "none"


def test_enum_range_projects_to_permissible_values(person_entries):
    e = person_entries["status"]
    assert e["type"] == "permissible_values"
    codes = {c["code"]: c for c in e["codes"]}
    assert set(codes) == {"ACTIVE", "INACTIVE"}
    assert codes["ACTIVE"]["label"] == "Active"
    assert codes["ACTIVE"]["description"] == "Currently active"
    assert "Active" in codes["ACTIVE"]["uri"]


def test_float_maps_to_decimal_with_unit(person_entries):
    e = person_entries["height"]
    assert e["type"] == "decimal"
    assert e["unit"] == "cm"
    # decimal is numeric → undeclared bounds become `none`.
    assert e["min"] == "none"
    assert e["max"] == "none"


def test_pattern_and_multivalued_and_uri(person_entries):
    assert person_entries["email"]["pattern"] == "[a-z]+"
    assert person_entries["tags"]["multivalued"] is True
    assert person_entries["homepage"]["type"] == "uri"
    assert "url" in person_entries["homepage"]["uri"]


def test_class_ranged_slot_skipped(person_entries):
    # address has a class range — not a flat column.
    assert "address" not in person_entries


def test_projectable_classes_excludes_mixin_and_abstract(sv):
    classes = set(projectable_classes(sv))
    assert {"Base", "Person", "Address"} <= classes
    assert "Mixinish" not in classes
    assert "AbstractThing" not in classes


def test_unknown_class_raises(sv):
    with pytest.raises(ValueError, match="not in schema"):
        schema_to_dd(sv, "NotAClass")


def test_empty_enum_still_emits_codes_key(tmp_path):
    # codes is required whenever type is permissible_values — even a
    # value-less enum must emit the key (as an empty list).
    schema = """
    id: https://example.org/e
    name: e
    prefixes: {linkml: https://w3id.org/linkml/}
    imports: [linkml:types]
    classes:
      Thing:
        slots: [kind]
    slots:
      kind:
        range: EmptyEnum
    enums:
      EmptyEnum: {}
    """
    path = tmp_path / "e.yaml"
    path.write_text(dedent(schema).strip() + "\n")
    sv_e = SchemaView(str(path))
    entry = schema_to_dd(sv_e, "Thing")["entries"][0]
    assert entry["type"] == "permissible_values"
    assert entry["codes"] == []


def test_dd_to_tsv_header_and_codes(sv):
    dd = schema_to_dd(sv, "Person")
    tsv = dd_to_tsv(dd)
    lines = tsv.splitlines()
    header = lines[0].split("\t")
    assert header[:4] == ["name", "type", "description", "codes"]
    status_row = next(line for line in lines if line.startswith("status\t"))
    # codes serialized via the canonical `code, label | ...` grammar.
    assert "ACTIVE" in status_row and "Active" in status_row
    assert "|" in status_row
