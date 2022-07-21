# -*- coding: utf-8 -*-

"""Test the module can be imported."""

import unittest

from schema_automator.generalizers.generalizer import DEFAULT_CLASS_NAME
from schema_automator.generalizers.pandas_generalizer import PandasDataGeneralizer
import pandas as pd

from schema_automator.utils import write_schema


class TestPandasDataGeneralizer(unittest.TestCase):
    """Tests generalization from RDF triples """

    def test_from_pandas(self):
        ie = PandasDataGeneralizer()
        expected = [
            ([5, 10, 20], 'integer'),
            (["a", "b", "c"], 'string'),
            (pd.to_datetime(["2010", "2011", "2012"]), 'datetime'),
            ([5.5, 10, 20], 'float')
        ]
        n = 1
        items = {}
        expected_types = {}
        for vals, expected_type in expected:
            col_name = f"column{n}"
            items[col_name] = vals
            expected_types[col_name] = expected_type
            n += 1
        df = pd.DataFrame(items)
        schema = ie.convert(df, schema_name='my_schema')
        #write_schema(schema)
        c = schema.classes[DEFAULT_CLASS_NAME]
        for col_name, expected_type in expected_types.items():
            self.assertEqual(expected_type, c.attributes[col_name].range)


