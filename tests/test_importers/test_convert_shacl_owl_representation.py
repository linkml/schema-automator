# -*- coding: utf-8 -*-

"""Test the module can be imported."""

import unittest
import os
import yaml
from schema_automator.importers.owl_import_engine import OwlImportEngine
from linkml.generators.yamlgen import YAMLGenerator

from schema_automator.utils.schemautils import write_schema
from tests import INPUT_DIR, OUTPUT_DIR

SHACL = os.path.join(INPUT_DIR, 'shacl.ofn')
DIR = os.path.join(OUTPUT_DIR, 'shacl')
OUTSCHEMA = os.path.join(OUTPUT_DIR, 'shacl-from-owl.yaml')
OUTSCHEMA_ENHANCED = os.path.join(OUTPUT_DIR, 'shacl-from-owl-enhanced.yaml')

class TestShaclOwlImport(unittest.TestCase):
    """Tests conversion of shacl metamodel (in OWL) to LinkML
    """

    def test_convert_shacl_owl(self):
        oie = OwlImportEngine()
        schema = oie.convert(SHACL, name='shacl')
        write_schema(schema, OUTSCHEMA)
        s = YAMLGenerator(OUTSCHEMA).serialize()
        with open(OUTSCHEMA_ENHANCED, 'w') as stream:
            stream.write(s)


