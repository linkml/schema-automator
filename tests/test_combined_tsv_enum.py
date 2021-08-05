# -*- coding: utf-8 -*-

"""Test the module can be imported."""

import unittest
import os
import yaml
from linkml_model_enrichment.importers.csv_import_engine import CsvDataImportEngine
from linkml_model_enrichment.annotators.enum_annotator import all_enums_to_ols
from linkml.generators.yamlgen import YAMLGenerator
from tests import INPUT_DIR, OUTPUT_DIR

IN = os.path.join(INPUT_DIR, 'biosamples.tsv')
OUTSCHEMA = os.path.join(OUTPUT_DIR, 'biosamples.yaml')
OUTSCHEMA_ROUNDTRIP = os.path.join(OUTPUT_DIR, 'biosamples.roundtrip.yaml')

class TestCombinedImport(unittest.TestCase):
    """
    Tests the combination of:
     - infer from tsv
     - annotate enums
    """

    def test_tsv(self):
        ie = CsvDataImportEngine()
        schema_dict = ie.convert(IN, class_name='Biosamples', name='biosamples')
        ys = yaml.dump(schema_dict, default_flow_style=False, sort_keys=False)
        with open(OUTSCHEMA, 'w') as stream:
            stream.write(ys)
        s = YAMLGenerator(ys).serialize()
        with open(OUTSCHEMA_ROUNDTRIP, 'w') as stream:
            stream.write(s)
        # M.A.M TODO
        #all_enums_to_ols(schema_dict, ['SPECIFIC_ECOSYSTEM_enum'])


