# -*- coding: utf-8 -*-

"""Test the module can be imported."""

import unittest
import os
import yaml
from schema_automator.importers.owl_import_engine import OwlImportEngine
from linkml.generators.yamlgen import YAMLGenerator
from tests import INPUT_DIR, OUTPUT_DIR

PROV = os.path.join(INPUT_DIR, 'prov.ofn')
DIR = os.path.join(OUTPUT_DIR, 'prov')
OUTSCHEMA = os.path.join(OUTPUT_DIR, 'prov-from-owl.yaml')
OUTSCHEMA_ENHANCED = os.path.join(OUTPUT_DIR, 'prov-from-owl.enhanced.yaml')

class TestOwlImport(unittest.TestCase):
    """PROV """

    def test_from_owl(self):
        """Test OWL conversion."""
        oie = OwlImportEngine()
        schema_dict = oie.convert(PROV, name='prov')
        ys = yaml.dump(schema_dict, default_flow_style=False, sort_keys=False)
        #print(ys)
        with open(OUTSCHEMA, 'w') as stream:
            stream.write(ys)
        s = YAMLGenerator(ys).serialize()
        with open(OUTSCHEMA_ENHANCED, 'w') as stream:
            stream.write(s)


