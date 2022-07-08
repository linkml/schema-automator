# -*- coding: utf-8 -*-

import unittest
import os

from linkml.generators.pythongen import PythonGenerator
from linkml_runtime.dumpers import yaml_dumper

from schema_automator.importers.frictionless_import_engine import FrictionlessImportEngine
from schema_automator.utils import write_schema
from tests import INPUT_DIR, OUTPUT_DIR

C2M2 = os.path.join(INPUT_DIR, "C2M2_datapackage.json")
OUT = os.path.join(OUTPUT_DIR, "C2M2.yaml")

class TestFrictionlessImporter(unittest.TestCase):
    """Tests import from Frictionless data packages """

    def setUp(self) -> None:
        pass

    def test_frictionless_import(self):
        """
        Test importing a package
        """
        ie = FrictionlessImportEngine()
        schema = ie.convert(C2M2)
        write_schema(schema, OUT)
        print("PYTHON")
        PythonGenerator(OUT).serialize()



