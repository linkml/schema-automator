# -*- coding: utf-8 -*-

"""Test the module can be imported."""

import unittest
import os
import yaml
from linkml_model_enrichment.importers.csv_import_engine import CsvDataImportEngine
from linkml.generators.yamlgen import YAMLGenerator
from tests import INPUT_DIR, OUTPUT_DIR

BIOBANK_SPECIMENS = os.path.join(INPUT_DIR, 'biobank-specimens.tsv')
OUTSCHEMA = os.path.join(OUTPUT_DIR, 'biobank.yaml')
OUTSCHEMA_ENHANCED = os.path.join(OUTPUT_DIR, 'biobank.enhanced.yaml')

class TestRobotTemplateImport(unittest.TestCase):
    """tests import from a robot template """

    def test_from_robot_template(self):
        """Test that expando can be imported."""
        ie = CsvDataImportEngine(robot=True)
        schema_dict = ie.convert(BIOBANK_SPECIMENS, class_name='BiobankSpecimen', name='biobank')
        ys = yaml.dump(schema_dict, default_flow_style=False, sort_keys=False)
        #print(ys)
        with open(OUTSCHEMA, 'w') as stream:
            stream.write(ys)
        s = YAMLGenerator(ys).serialize()
        with open(OUTSCHEMA_ENHANCED, 'w') as stream:
            stream.write(s)

