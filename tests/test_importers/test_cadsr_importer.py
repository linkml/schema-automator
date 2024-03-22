import os

from linkml.generators import PythonGenerator, OwlSchemaGenerator
from linkml_runtime import SchemaView

from schema_automator.importers.cadsr_import_engine import CADSRImportEngine
from schema_automator.utils import write_schema
from tests import INPUT_DIR, OUTPUT_DIR

IDS = ["996", "12137353", "2724331", "2721353", "2179609"]
OUT = os.path.join(OUTPUT_DIR, "cadsr-cde-example.yaml")
OWL_OUT = os.path.join(OUTPUT_DIR, "cadsr-cde-example.owl.ttl")


def test_cadsr_import():
    ie = CADSRImportEngine()
    paths = [os.path.join(INPUT_DIR, f"cadsr-cde-{i}.json") for i in IDS]
    schema = ie.convert(paths, id="https://w3id.org/linkml/cadsr", name="cadsr_schema")
    assert schema
    write_schema(schema, OUT)
    py_str = PythonGenerator(OUT).serialize()
    assert py_str
    _sv = SchemaView(schema)
    with open(OWL_OUT, "w", encoding="utf-8") as stream:
        owlgen = OwlSchemaGenerator(OUT, add_root_classes=True, metaclasses=False, type_objects=False)
        stream.write(owlgen.serialize())


def test_cadsr_to_table():
    ie = CADSRImportEngine()
    paths = [os.path.join(INPUT_DIR, f"cadsr-cde-{i}.json") for i in IDS]
    rows = list(ie.as_rows(paths))
    assert rows
    for row in rows:
        print(row)
