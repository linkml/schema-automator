# -*- coding: utf-8 -*-

"""Test the module can be imported."""

import unittest
import os
import yaml
from linkml_runtime.linkml_model import SchemaDefinition

from linkml_model_enrichment.importers.csv_import_engine import CsvDataImportEngine
from linkml.generators.yamlgen import YAMLGenerator
from tests import INPUT_DIR, OUTPUT_DIR

BOOKS = os.path.join(INPUT_DIR, 'books.tsv')
BOOKS_OUTSCHEMA = os.path.join(OUTPUT_DIR, 'books.yaml')
BOOKS_OUTSCHEMA_ENHANCED = os.path.join(OUTPUT_DIR, 'books.enhanced.yaml')

NEWSLOTS = os.path.join(INPUT_DIR, 'data_to_import.tsv')
NEWSLOTS_OUTSCHEMA = os.path.join(OUTPUT_DIR, 'new_slots.yaml')


class TestTsvmport(unittest.TestCase):
    """TSV import """

    def test_tsv(self):
        """Test that TSVs can be imported to LinkML."""
        ie = CsvDataImportEngine()
        schema_dict = ie.convert(BOOKS, class_name='Book', name='books')
        ys = yaml.dump(schema_dict, default_flow_style=False, sort_keys=False)
        with open(BOOKS_OUTSCHEMA, 'w') as stream:
            stream.write(ys)
        s = YAMLGenerator(ys).serialize()
        with open(BOOKS_OUTSCHEMA_ENHANCED, 'w') as stream:
            stream.write(s)

    def test_create_edge_slots(self):
        """
            Test we can create slots with descriptions from a TSV file
        """
        ie = CsvDataImportEngine()
        schema_dict = ie.read_slot_tsv(NEWSLOTS, is_a="edge property")
        ys = yaml.dump(schema_dict, default_flow_style=False, sort_keys=False)
        with open(NEWSLOTS_OUTSCHEMA, 'w') as stream:
            stream.write(ys)

    def _convert(self, base_name: str, cn='Example', index_slot='examples') -> SchemaDefinition:
        ie = CsvDataImportEngine()
        fn = f'{base_name}.tsv'
        infile = os.path.join(INPUT_DIR, fn)
        schema_dict = ie.convert(infile, class_name=cn, name=index_slot)
        ys = yaml.dump(schema_dict, default_flow_style=False, sort_keys=False)
        outfile = os.path.join(OUTPUT_DIR, f'{base_name}.yaml')
        with open(outfile, 'w') as stream:
            stream.write(ys)
        s = YAMLGenerator(ys).serialize()
        outfile2 = os.path.join(OUTPUT_DIR, f'{base_name}.enhanced.yaml')
        with open(outfile2, 'w') as stream:
            stream.write(s)
        return s

    def test_tsv_dad_is_metadata(self):
        self._convert('dad-is-metadata')