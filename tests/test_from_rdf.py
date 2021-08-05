# -*- coding: utf-8 -*-

"""Test the module can be imported."""

import unittest
import os
import yaml
from linkml_model_enrichment.importers.rdf_instance_import_engine import RdfInstanceImportEngine
from linkml.generators.yamlgen import YAMLGenerator
from tests import INPUT_DIR, OUTPUT_DIR

PROV = os.path.join(INPUT_DIR, 'prov.ttl')
DIR = os.path.join(OUTPUT_DIR, 'prov')
OUTSCHEMA = os.path.join(OUTPUT_DIR, 'prov.yaml')
OUTSCHEMA_ENHANCED = os.path.join(OUTPUT_DIR, 'prov.enhanced.yaml')

class TestRdfImport(unittest.TestCase):
    """PROV """

    def test_from_rdf(self):
        """Test that expando can be imported."""
        sie = RdfInstanceImportEngine()
        if not os.path.exists(DIR):
            os.makedirs(DIR)
        schema_dict = sie.convert(PROV, dir=DIR, format='ttl')
        ys = yaml.dump(schema_dict, default_flow_style=False, sort_keys=False)
        print(ys)
        with open(OUTSCHEMA, 'w') as stream:
            stream.write(ys)
        s = YAMLGenerator(ys).serialize()
        with open(OUTSCHEMA_ENHANCED, 'w') as stream:
            stream.write(s)

