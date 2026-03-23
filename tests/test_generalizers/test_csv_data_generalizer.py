# -*- coding: utf-8 -*-

"""Test the module can be imported."""

import unittest
import os
import yaml
from linkml_runtime.linkml_model import SchemaDefinition

from schema_automator.generalizers.csv_data_generalizer import CsvDataGeneralizer, infer_range
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

    def test_infer_range(self):
        """
        Tests inference of ranges
        """
        cases = [
            ([1, 2, 3], "integer"),
            ([1, 2, "x"], "string"),
            ([1, 2, "-3"], "integer"),
            (["100", "200", "300"], "integer"),
            ([], "string"),
            ([None], "string"),
            ([1, None], "integer"),
            ([1, ""], "integer"),
            (['5.99', '7.95', '7.99', '6.99'], "float"),
            (['5.999', '7.955', '7.990', '6.990'], "float"),
            (["2mm", "3m", "4 mm"], "measurement"),
            (["true", "false"], "boolean"),
            (["2024-01-01", "2023-12-31"], "date"),
            (["2024-01-01T12:30:00", "2023-12-31T08:15:00"], "datetime"),
            (["2024-01-01", "2023-12-31T08:15:00"], "datetime"),
            (["2024-01-01", "not-a-date"], "string"),
        ]
        for values, expected in cases:
            self.assertEqual(infer_range({}, values, {}), expected, f"Failed on {values}")

    def test_metadata_rows(self):
        """
        Tests TSVs that include additional metadata
        """
        ie = CsvDataGeneralizer(data_dictionary_row_count=1,
                                enum_threshold=0.5,)
        rows = [
            {"id": "identifier",
             "name": "name of pet",
             "description": "A description of the pet",
             "age": "age of pet",
            "species": "species of pet"},
            {"id": "1", "name": "Fido", "age": "3", "species": "dog"},
            {"id": "2", "name": "Rover", "age": "3", "species": "dog"},
            {"id": "3", "name": "Buster", "age": "2", "species": "dog"},
            {"id": "4", "name": "MrTickles", "age": "6", "species": "dog"},
            {"id": "5", "name": "Violet", "age": "4", "species": "cat"},
            {"id": "6", "name": "MrFurry", "age": "1", "species": "cat"},
            {"id": "7", "name": "X", "age": "3", "species": "cat"},
            {"id": "8", "name": "Z", "age": "3", "species": "cat"},
            {"id": "9", "name": "A", "age": "3", "species": "cat"},
        ]
        schema = ie.convert_dicts(rows, "test", "Pet")
        slots = schema.slots
        self.assertEqual(slots["name"].description, "name of pet")
        self.assertEqual(slots["age"].description, "age of pet")
        self.assertEqual(slots["species"].description, "species of pet")
        self.assertEqual(slots["id"].description, "identifier")
        self.assertTrue(slots["id"].identifier)
        # ensure that the first metadata row was not counted as a data row
        # (if it is, then the range would be inferred to be string,
        #  and the description would be an enum value)
        self.assertEqual(slots["age"].range, "integer")
        species = list(schema.enums["species_enum"].permissible_values.keys())
        self.assertCountEqual(species, ["dog", "cat"])
        write_schema(schema)


    def test_infer_optional(self):
        rows = [
            {"id": "1", "name": "Fido", "age": "3", "notes": "friendly"},
            {"id": "2", "name": "Rover", "age": "", "notes": ""},
            {"id": "3", "name": "Buster", "age": "2", "notes": None},
        ]
        ie = CsvDataGeneralizer(infer_optional=True)
        schema = ie.convert_dicts(rows, "test", "Pet")
        slots = schema.slots
        self.assertFalse(slots["age"].required)
        self.assertFalse(slots["notes"].required)
        self.assertIsNone(slots["name"].required)
        self.assertIsNone(slots["id"].required)

    def test_infer_optional_off_by_default(self):
        rows = [
            {"id": "1", "name": "Fido", "age": "3"},
            {"id": "2", "name": "Rover", "age": ""},
        ]
        ie = CsvDataGeneralizer()
        schema = ie.convert_dicts(rows, "test", "Pet")
        self.assertIsNone(schema.slots["age"].required)

    def test_infer_mixed_types(self):
        rows = [
            {"id": "1", "name": "Fido", "score": "3"},
            {"id": "2", "name": "Rover", "score": "high"},
            {"id": "3", "name": "Buster", "score": "5"},
        ]
        ie = CsvDataGeneralizer(infer_mixed_types=True)
        schema = ie.convert_dicts(rows, "test", "Pet")
        slot = schema.slots["score"]
        self.assertIsNone(slot.range)
        any_of_ranges = [expr.range for expr in slot.any_of]
        self.assertCountEqual(any_of_ranges, ["integer", "string"])

    def test_infer_mixed_types_homogeneous(self):
        rows = [
            {"id": "1", "val": "10"},
            {"id": "2", "val": "20"},
        ]
        ie = CsvDataGeneralizer(infer_mixed_types=True)
        schema = ie.convert_dicts(rows, "test", "Pet")
        self.assertEqual(schema.slots["val"].range, "integer")
        self.assertEqual(len(schema.slots["val"].any_of), 0)

    def test_infer_mixed_types_off_by_default(self):
        rows = [
            {"id": "1", "score": "3"},
            {"id": "2", "score": "high"},
        ]
        ie = CsvDataGeneralizer()
        schema = ie.convert_dicts(rows, "test", "Pet")
        self.assertEqual(schema.slots["score"].range, "string")
        self.assertEqual(len(schema.slots["score"].any_of), 0)

    def test_infer_enum_from_integers(self):
        rows = [
            {"id": "1", "name": "Alice", "status": "1"},
            {"id": "2", "name": "Bob", "status": "2"},
            {"id": "3", "name": "Carol", "status": "1"},
            {"id": "4", "name": "Dave", "status": "2"},
            {"id": "5", "name": "Eve", "status": "1"},
            {"id": "6", "name": "Frank", "status": "2"},
            {"id": "7", "name": "Grace", "status": "1"},
            {"id": "8", "name": "Hank", "status": "2"},
            {"id": "9", "name": "Ivy", "status": "1"},
            {"id": "10", "name": "Jack", "status": "2"},
        ]
        ie = CsvDataGeneralizer(infer_enum_from_integers=True, enum_threshold=0.5)
        schema = ie.convert_dicts(rows, "test", "Pet")
        # status has 2 distinct values out of 10 rows => ratio 0.18 < 0.5 threshold
        self.assertEqual(schema.slots["status"].range, "status_enum")
        pvs = list(schema.enums["status_enum"].permissible_values.keys())
        self.assertCountEqual(pvs, ["1", "2"])

    def test_infer_enum_from_integers_high_cardinality_stays_integer(self):
        rows = [{"id": str(i), "val": str(i)} for i in range(1, 21)]
        ie = CsvDataGeneralizer(infer_enum_from_integers=True, enum_threshold=0.1)
        schema = ie.convert_dicts(rows, "test", "Thing")
        # 20 distinct out of 20 rows => ratio 1.0, well above threshold
        self.assertEqual(schema.slots["val"].range, "integer")

    def test_infer_enum_from_integers_off_by_default(self):
        rows = [
            {"id": "1", "status": "1"},
            {"id": "2", "status": "2"},
            {"id": "3", "status": "1"},
            {"id": "4", "status": "2"},
            {"id": "5", "status": "1"},
            {"id": "6", "status": "2"},
            {"id": "7", "status": "1"},
            {"id": "8", "status": "2"},
            {"id": "9", "status": "1"},
            {"id": "10", "status": "2"},
        ]
        ie = CsvDataGeneralizer()
        schema = ie.convert_dicts(rows, "test", "Pet")
        self.assertEqual(schema.slots["status"].range, "integer")

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