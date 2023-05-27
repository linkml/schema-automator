# -*- coding: utf-8 -*-

import unittest
import os
from pathlib import Path

import pandas as pd

from schema_automator.importers.tabular_import_engine import TableImportEngine
from schema_automator.utils import write_schema
from tests import INPUT_DIR, OUTPUT_DIR

OUT = os.path.join(OUTPUT_DIR, "BioMRLs.yaml")
INPUT_HTML = os.path.join(INPUT_DIR, "BioMRLs-table.html")


class TestTableImporter(unittest.TestCase):
    """Tests import from tables data packages """

    def setUp(self) -> None:
        pass

    def test_html_import(self):
        """
        Test importing a table from HTML via BS
        """
        ie = TableImportEngine(parent="BioMRL",
                               element_type="enum",
                               columns=["permissible_value", "description"])
        # this doesn't work on windows:
        dfs = pd.read_html(Path(f"{INPUT_HTML}").as_uri())
        schema = ie.import_from_dataframe(dfs[0])
        write_schema(schema, OUT)






