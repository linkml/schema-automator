# -*- coding: utf-8 -*-

import os
from pathlib import Path

import pytest
from linkml.generators.pythongen import PythonGenerator
from linkml_runtime import SchemaView
from schema_automator.importers.kwalify_import_engine import KwalifyImportEngine
from schema_automator.utils import write_schema
from tests import INPUT_DIR, OUTPUT_DIR


EXPECTED_TEST1 = """
      status:
        range: MySchema_status_enum
        required: true
      description:
        range: string
        required: true
      taxon:
        range: Taxon
        required: false
"""


@pytest.mark.parametrize('test_input,schema_id, schema_name,class_name,expected', [
    ("test2", None, None, None, None),
    ("test", None, None, None, None),
    ("test", None, "my_schema", None, [EXPECTED_TEST1]),
])
def test_kwalify_import(test_input, schema_id, schema_name, class_name, expected):
    """
    Test importing kwalify
    """
    ie = KwalifyImportEngine()
    in_path = Path(INPUT_DIR) / f"{test_input}.kwalify.yaml"
    out_path = str(Path(OUTPUT_DIR) / f"{test_input}-from-kwalify.yaml")
    schema = ie.convert(in_path,
                            id=schema_id, name=schema_name,
                            class_name=class_name)
    write_schema(schema, out_path)
    schema_str = open(out_path).read()
    py_str = PythonGenerator(out_path).serialize()
    assert py_str is not None
    _sv = SchemaView(schema)
    if expected:
        for e in expected:
            assert e in schema_str




