# -*- coding: utf-8 -*-

"""Test the module can be imported."""

import unittest
import os
import yaml
from linkml_model_enrichment.importers.json_instance_import_engine import JsonInstanceImportEngine
from linkml.generators.yamlgen import YAMLGenerator
from tests import INPUT_DIR, OUTPUT_DIR

IN = os.path.join(INPUT_DIR, 'synonymizer.yaml')
OUTSCHEMA = os.path.join(OUTPUT_DIR, 'syn-schema.yaml')
OUTSCHEMA_ENHANCED = os.path.join(OUTPUT_DIR, 'syn-schema2.yaml')

class TestJsonImport(unittest.TestCase):
    """JSON """

    def test_from_json(self):
        """Test that expando can be imported."""
        ie = JsonInstanceImportEngine()
        schema_dict = ie.convert(IN, format='yaml')
        ys = yaml.dump(schema_dict, default_flow_style=False, sort_keys=False)
        print(ys)
        with open(OUTSCHEMA, 'w') as stream:
            stream.write(ys)
        s = YAMLGenerator(ys).serialize()
        with open(OUTSCHEMA_ENHANCED, 'w') as stream:
            stream.write(s)

