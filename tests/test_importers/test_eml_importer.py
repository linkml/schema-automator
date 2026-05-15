"""Tests for the EML XML → LinkML schema importer."""

from __future__ import annotations

import os
import tempfile

import pytest
from linkml_runtime import SchemaView
from linkml_runtime.dumpers import yaml_dumper

from schema_automator.importers.eml_import_engine import EmlImportEngine
from tests import INPUT_DIR, OUTPUT_DIR

GLBRC_193 = os.path.join(INPUT_DIR, "eml", "glbrc-193.eml")
OUT = os.path.join(OUTPUT_DIR, "glbrc-193.yaml")


@pytest.fixture(scope="module")
def converted_schema():
    schema = EmlImportEngine().convert(GLBRC_193)
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    with open(OUT, "w") as f:
        f.write(yaml_dumper.dumps(schema))
    return schema


def test_top_level_metadata(converted_schema):
    assert converted_schema.id == "knb-lter-kbs.193.123"
    assert converted_schema.name == "knb-lter-kbs.193.123"
    assert "Marginal Land Rainfall Exclusion Experiment" in converted_schema.title


def test_class_per_data_table(converted_schema):
    """glbrc-193.eml has 9 <dataTable> blocks → 9 classes."""
    assert len(converted_schema.classes) == 9


def test_attribute_totals(converted_schema):
    """glbrc-193.eml has 96 <attribute> elements across all tables."""
    total = sum(len(c.attributes) for c in converted_schema.classes.values())
    assert total == 96


def test_measurementscale_dispatch(converted_schema):
    """case() dispatch maps each variant to a LinkML range.

    The test resource has: 42 nominal (textDomain) + 9 dateTime → 51
    string ranges; 7 numeric attributes with numberType ∈
    {integer, natural, whole} → integer; the remaining 38 numeric
    attributes → float.
    """
    ranges = {}
    for c in converted_schema.classes.values():
        for slot in c.attributes.values():
            ranges[slot.range] = ranges.get(slot.range, 0) + 1
    assert ranges == {"string": 51, "integer": 7, "float": 38}


def test_no_unnamed_classes_or_slots(converted_schema):
    """Every class and slot must have a derived name."""
    for cls in converted_schema.classes.values():
        assert cls.name, "class missing name"
        for slot in cls.attributes.values():
            assert slot.name, f"slot in class {cls.name} missing name"


def test_schema_loads_back_via_schemaview(converted_schema):
    """Output must be parseable as a real LinkML schema."""
    sv = SchemaView(converted_schema)
    assert len(sv.all_classes()) == 9


def test_class_name_collision_raises_with_both_sources():
    """Two dataTables whose entityNames sanitize to the same LinkML
    class name must raise rather than silently overwrite, and the
    error must name both colliding source values.
    """
    eml = """<?xml version="1.0" encoding="UTF-8"?>
<eml:eml packageId="example.collision.classes"
         system="example"
         xmlns:eml="https://eml.ecoinformatics.org/eml-2.2.0">
  <dataset>
    <title>Class-name collision fixture</title>
    <dataTable>
      <entityName>Soil moisture (auto)</entityName>
      <entityDescription>Automated readings</entityDescription>
      <attributeList>
        <attribute><attributeName>x</attributeName>
          <measurementScale><nominal><nonNumericDomain><textDomain><definition>x</definition></textDomain></nonNumericDomain></nominal></measurementScale>
        </attribute>
      </attributeList>
    </dataTable>
    <dataTable>
      <entityName>Soil moisture, auto</entityName>
      <entityDescription>Same thing, different punctuation</entityDescription>
      <attributeList>
        <attribute><attributeName>y</attributeName>
          <measurementScale><nominal><nonNumericDomain><textDomain><definition>y</definition></textDomain></nonNumericDomain></nominal></measurementScale>
        </attribute>
      </attributeList>
    </dataTable>
  </dataset>
</eml:eml>"""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".eml", delete=False) as f:
        f.write(eml)
        path = f.name
    with pytest.raises(ValueError) as exc:
        EmlImportEngine().convert(path)
    msg = str(exc.value)
    assert "Soil moisture (auto)" in msg
    assert "Soil moisture, auto" in msg
    assert "linkml-map#242" in msg


def test_attribute_name_collision_raises_with_both_sources():
    """Two attributes in the same dataTable that sanitize to the same
    name must raise and name both colliding source values.
    """
    eml = """<?xml version="1.0" encoding="UTF-8"?>
<eml:eml packageId="example.collision.attrs"
         system="example"
         xmlns:eml="https://eml.ecoinformatics.org/eml-2.2.0">
  <dataset>
    <title>Attr-name collision fixture</title>
    <dataTable>
      <entityName>SampleTable</entityName>
      <entityDescription>...</entityDescription>
      <attributeList>
        <attribute><attributeName>depth (m)</attributeName>
          <measurementScale><ratio><unit><standardUnit>meter</standardUnit></unit><numericDomain><numberType>real</numberType></numericDomain></ratio></measurementScale>
        </attribute>
        <attribute><attributeName>depth m</attributeName>
          <measurementScale><ratio><unit><standardUnit>meter</standardUnit></unit><numericDomain><numberType>real</numberType></numericDomain></ratio></measurementScale>
        </attribute>
      </attributeList>
    </dataTable>
  </dataset>
</eml:eml>"""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".eml", delete=False) as f:
        f.write(eml)
        path = f.name
    with pytest.raises(ValueError) as exc:
        EmlImportEngine().convert(path)
    msg = str(exc.value)
    assert "depth (m)" in msg
    assert "depth m" in msg
    assert "linkml-map#242" in msg


def test_metadata_only_eml_produces_empty_classes_map():
    """An EML document with no ``<dataTable>`` elements is valid and
    should convert to a schema carrying the top-level metadata with an
    empty ``classes`` map, not raise.
    """
    eml = """<?xml version="1.0" encoding="UTF-8"?>
<eml:eml packageId="example.metadata.only.1"
         system="example"
         xmlns:eml="https://eml.ecoinformatics.org/eml-2.2.0">
  <dataset>
    <title>A metadata-only dataset</title>
  </dataset>
</eml:eml>"""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".eml", delete=False) as f:
        f.write(eml)
        path = f.name

    schema = EmlImportEngine().convert(path)
    assert schema.id == "example.metadata.only.1"
    assert schema.title == "A metadata-only dataset"
    assert len(schema.classes) == 0
