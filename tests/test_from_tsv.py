# -*- coding: utf-8 -*-

"""Test the module can be imported."""

import unittest
import os
import yaml
from linkml_model_enrichment.importers.csv_import_engine import CsvDataImportEngine
from linkml.generators.yamlgen import YAMLGenerator
from tests import INPUT_DIR, OUTPUT_DIR

BOOKS = os.path.join(INPUT_DIR, 'books.tsv')
BOOKS_OUTSCHEMA = os.path.join(OUTPUT_DIR, 'books.yaml')
BOOKS_OUTSCHEMA_ENHANCED = os.path.join(OUTPUT_DIR, 'books.enhanced.yaml')

class TestTsvmport(unittest.TestCase):
    """TSV """

    def test_tsv(self):
        """Test that expando can be imported."""
        ie = CsvDataImportEngine()
        schema_dict = ie.convert(BOOKS, class_name='Book', name='books')
        ys = yaml.dump(schema_dict, default_flow_style=False, sort_keys=False)
        with open(BOOKS_OUTSCHEMA, 'w') as stream:
            stream.write(ys)
        s = YAMLGenerator(ys).serialize()
        with open(BOOKS_OUTSCHEMA_ENHANCED, 'w') as stream:
            stream.write(s)


