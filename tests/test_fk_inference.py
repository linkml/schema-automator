# -*- coding: utf-8 -*-

"""Test the module can be imported."""

import unittest
import os
import yaml
from linkml_model_enrichment.importers.csv_import_engine import CsvDataImportEngine
from linkml.generators.yamlgen import YAMLGenerator
from tests import INPUT_DIR, OUTPUT_DIR

SAMPLES = os.path.join(INPUT_DIR, 'sample.tsv')
ENVO = os.path.join(INPUT_DIR, 'envo.tsv')
SAMPLES_OUTSCHEMA = os.path.join(OUTPUT_DIR, 'sample-schema.yaml')

class TestForeignKeyInference(unittest.TestCase):
    """TSV """

    def test_fk_inference(self):
        """Test that expando can be imported."""
        ie = CsvDataImportEngine(downcase_header=True)
        fks = ie.infer_linkages([ENVO, SAMPLES])
        #fks = ie.infer_linkages([SAMPLES, ENVO])
        print('FKS:')
        for fk in fks:
            print(fk)

    def test_schema_with_fk_inference(self):
        """Test that expando can be imported."""
        ie = CsvDataImportEngine(downcase_header=True, infer_foreign_keys=True)
        schema_dict = ie.convert_multiple([ENVO, SAMPLES])
        ys = yaml.dump(schema_dict, default_flow_style=False, sort_keys=False)
        with open(SAMPLES_OUTSCHEMA, 'w') as stream:
            stream.write(ys)
