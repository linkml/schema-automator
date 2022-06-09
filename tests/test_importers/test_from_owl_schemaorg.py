# -*- coding: utf-8 -*-

"""Test the module can be imported."""

import unittest
import os
import yaml
from schema_automator.importers.owl_import_engine import OwlImportEngine
from linkml.generators.yamlgen import YAMLGenerator
from tests import INPUT_DIR, OUTPUT_DIR

SDO = os.path.join(INPUT_DIR, 'schemaorg-robot.ofn')
OUTSCHEMA = os.path.join(OUTPUT_DIR, 'schemaorg.yaml')
OUTSCHEMA_ENHANCED = os.path.join(OUTPUT_DIR, 'schemaorg.enhanced.yaml')

class TestSchemaOrgOwlImport(unittest.TestCase):
    """PROV """

    @unittest.skip
    def test_from_owl(self):
        """Test OWL conversion."""
        oie = OwlImportEngine()
        schema_dict = oie.convert(SDO, name='schemaorg')
        ys = yaml.dump(schema_dict, default_flow_style=False, sort_keys=False)
        #print(ys)
        with open(OUTSCHEMA, 'w') as stream:
            stream.write(ys)
        s = YAMLGenerator(ys).serialize()
        with open(OUTSCHEMA_ENHANCED, 'w') as stream:
            stream.write(s)


