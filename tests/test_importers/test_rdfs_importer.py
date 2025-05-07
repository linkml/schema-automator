# -*- coding: utf-8 -*-

"""Test the module can be imported."""

from io import StringIO
import unittest
import os
import yaml
from linkml_runtime import SchemaView

from schema_automator.importers.owl_import_engine import OwlImportEngine
from linkml.generators.yamlgen import YAMLGenerator
from schema_automator.importers.rdfs_import_engine import RdfsImportEngine

from schema_automator.utils.schemautils import write_schema
from tests import INPUT_DIR, OUTPUT_DIR

REPRO = os.path.join(INPUT_DIR, 'reproschema.ttl')
OUTSCHEMA = os.path.join(OUTPUT_DIR, 'reproschema-from-ttl.yaml')
FOAF = os.path.join(INPUT_DIR, 'foaf_snippet.ttl')


def test_import_foaf():
    engine = RdfsImportEngine()
    schema = engine.convert(FOAF)
    sv = SchemaView(schema)
    assert len(sv.all_classes()) == 3
    assert len(sv.all_slots()) == 1
    assert sv.get_slot("knows").range == "Person"
    assert sv.schema.default_prefix == "foaf"
    assert "foaf" in sv.schema.prefixes

def test_comment_description():
    """
    rdfs:comment should be converted to description
    """
    rdf = StringIO("""
    @prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .

    <http://example.org/Class> a rdfs:Class ;
        rdfs:comment "A class." .
    """)
    engine = RdfsImportEngine()
    schema = engine.convert(rdf)
    sv = SchemaView(schema)
    cls = sv.get_class("Class")
    assert cls.description == "A class."

def test_infer_prefix():
    """
    If the schema has no name, id or default prefix, the importer should infer them from prefix usage in the schema.
    """
    rdf = StringIO("""
    @prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
    @prefix foo: <https://foo.com> .

    foo:Class a rdfs:Class ;
        rdfs:comment "A class." .

    foo:prop a rdfs:Property ;
        rdfs:comment "A property." .
    """)
    engine = RdfsImportEngine()
    schema = engine.convert(rdf)
    # Although not explicitly provided, the importer should realise that the prefix is "foo"
    assert schema.default_prefix == "foo"
    assert schema.id == "https://foo.com"
    assert schema.name == "foo"

def test_from_rdfs():
    """Test OWL conversion."""
    oie = RdfsImportEngine()
    schema = oie.convert(REPRO, default_prefix='reproschema', identifier='id')
    write_schema(schema, OUTSCHEMA)
    # roundtrip
    s = YAMLGenerator(OUTSCHEMA).serialize()
    sv = SchemaView(OUTSCHEMA)
    activity = sv.get_class("Activity")
    assert activity
    assert activity.name == "Activity"
    assert activity.is_a == "CreativeWork"
    slots = sv.class_induced_slots(activity.name)
    assert len(slots) == 1
    slot = slots[0]
    assert slot.name == "id"
