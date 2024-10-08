import os
import pytest

from linkml_runtime import SchemaView

from schema_automator.importers.shacl_import_engine import ShaclImportEngine
from linkml.generators.yamlgen import YAMLGenerator

from schema_automator.utils.schemautils import write_schema
from tests import INPUT_DIR, OUTPUT_DIR

# TODO - Write tests (this is a copy of test_rdfs_importer)

REPRO = os.path.join(INPUT_DIR, 'shacl_simple.ttl')
OUTSCHEMA = os.path.join(OUTPUT_DIR, 'user_from_shacl_simple2.yaml')


def test_from_shacl():
    """Test Shacl conversion."""
    sie = ShaclImportEngine()
    
    schema = sie.convert(REPRO, default_prefix='usr', identifier='id')
    write_schema(schema, OUTSCHEMA)
    return
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
