# -*- coding: utf-8 -*-

"""Test the module can be imported."""

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



def test_from_rdfs():
    """Test OWL conversion."""
    oie = RdfsImportEngine()
    schema = oie.convert(REPRO, default_prefix='reproschema', identifier='id')
    write_schema(schema, OUTSCHEMA)
    # roundtrip
    s = YAMLGenerator(OUTSCHEMA).serialize()
    print(s[0:100])
    sv = SchemaView(OUTSCHEMA)
    activity = sv.get_class("Activity")
    assert activity
    assert activity.name == "Activity"
    assert activity.is_a == "CreativeWork"
    slots = sv.class_induced_slots(activity.name)
    assert len(slots) == 1
    slot = slots[0]
    assert slot.name == "id"




