# -*- coding: utf-8 -*-

"""Test the module can be imported."""

import unittest
import os
import yaml
from linkml_runtime.linkml_model import SchemaDefinition

from schema_automator.generalizers.csv_data_generalizer import CsvDataGeneralizer
from linkml.generators.yamlgen import YAMLGenerator

from schema_automator.utils.schemautils import write_schema
from tests import INPUT_DIR, OUTPUT_DIR

BOOKS = os.path.join(INPUT_DIR, 'books.tsv')
BOOKS_OUTSCHEMA = os.path.join(OUTPUT_DIR, 'books.yaml')
BOOKS_OUTSCHEMA_ENHANCED = os.path.join(OUTPUT_DIR, 'books.enhanced.yaml')

NEWSLOTS = os.path.join(INPUT_DIR, 'data_to_import.tsv')
NEWSLOTS_OUTSCHEMA = os.path.join(OUTPUT_DIR, 'new_slots.yaml')

EXPECTED_SLOTS = ['id', 'book_category', 'name', 'price', 'inStock',
                  'author', 'series_t', 'sequence_i', 'genre_s', 'yesno', 'blah_b']


class TestCsvDataGeneralizer(unittest.TestCase):
    """TSV import """

    def test_tsv(self):
        """Test that TSVs can be imported to LinkML."""
        ie = CsvDataGeneralizer()
        schema = ie.convert(BOOKS, class_name='Book', schema_name='books')
        self.assertEqual(schema.name, 'books')
        self.assertEqual(list(schema.classes.keys()), ['Book'])
        c = schema.classes['Book']
        self.assertCountEqual(EXPECTED_SLOTS, list(schema.slots.keys()))
        self.assertCountEqual(EXPECTED_SLOTS, c.slots)
        write_schema(schema, BOOKS_OUTSCHEMA)
        s = YAMLGenerator(BOOKS_OUTSCHEMA).serialize()
        with open(BOOKS_OUTSCHEMA_ENHANCED, 'w') as stream:
            stream.write(s)

    def test_create_edge_slots(self):
        """
            Test we can create slots with descriptions from a TSV file
        """
        ie = CsvDataGeneralizer()
        schema_dict = ie.read_slot_tsv(NEWSLOTS, is_a="edge property")
        ys = yaml.dump(schema_dict, default_flow_style=False, sort_keys=False)
        with open(NEWSLOTS_OUTSCHEMA, 'w') as stream:
            stream.write(ys)

    def _convert(self, base_name: str, cn='Example', index_slot='examples') -> SchemaDefinition:
        ie = CsvDataGeneralizer()
        fn = f'{base_name}.tsv'
        infile = os.path.join(INPUT_DIR, fn)
        schema = ie.convert(infile, class_name=cn, name=index_slot)
        outfile = os.path.join(OUTPUT_DIR, f'{base_name}.yaml')
        write_schema(schema, outfile)
        s = YAMLGenerator(outfile).serialize()
        outfile2 = os.path.join(OUTPUT_DIR, f'{base_name}.enhanced.yaml')
        with open(outfile2, 'w', encoding='utf-8') as stream:
            stream.write(s)
        return s

    def test_tsv_dad_is_metadata(self):
        self._convert('dad-is-metadata')