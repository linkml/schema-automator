import os

from linkml.generators import PythonGenerator
from linkml_runtime import SchemaView

from schema_automator.importers.fhir_codesystem_import_engine import FHIRCodeSystemImportEngine
from schema_automator.utils import write_schema
from tests import INPUT_DIR, OUTPUT_DIR

INPUT_JSON = os.path.join(INPUT_DIR, "CodeSystem-v3-RoleCode.json")
OUT = os.path.join(OUTPUT_DIR, "CodeSystem-v3-RoleCode.linkml.yaml")


def test_fhir_code_system_import():
    with open(INPUT_JSON, "r", encoding="utf-8") as f:
        input_data = f.read()

    ie = FHIRCodeSystemImportEngine()
    schema = ie.load(input_data)
    assert schema
    write_schema(schema, OUT)

    py_str = PythonGenerator(OUT).serialize()
    assert py_str
    _sv = SchemaView(schema)