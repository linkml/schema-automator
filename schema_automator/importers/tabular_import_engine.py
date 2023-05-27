import logging

from dataclasses import dataclass
from tempfile import NamedTemporaryFile
from typing import List

from linkml_runtime.linkml_model.meta import SchemaDefinition
from schemasheets.schemamaker import SchemaMaker

from schema_automator.importers.import_engine import ImportEngine
import pandas as pd


@dataclass
class TableImportEngine(ImportEngine):
    """
    An ImportEngine that imports tabular data via schemasheets

    """
    element_type: str = None
    parent: str = None
    columns: List[str] = None

    def convert(self, file: str) -> SchemaDefinition:
        """
        Converts one or more JSON files into a Schema

        :param files:
        :param kwargs:
        :return:
        """
        df = pd.read_csv(file, sep='\t')
        self.import_from_dataframe(df)

    def import_from_dataframe(self, df: pd.DataFrame):
        """
        Imports a dataframe into a schema

        :param df:
        :return:
        """
        tf = NamedTemporaryFile(delete=False)
        if not self.columns:
            raise ValueError("Must specify columns")
        logging.info(f"Using columns: {self.columns}")
        ix = 1
        line = pd.DataFrame(dict(zip(df.head(), self.columns)), index=[ix])
        df = pd.concat([df.iloc[:ix-1], line, df.iloc[ix-1:]]).reset_index(drop=True)
        if self.parent:
            df.insert(0,
                      column="parent",
                      value=[f">{self.element_type}"] + [self.parent] * (len(df) - 1))
        df.to_csv(tf.name, sep='\t', index=False)
        #print(open(tf.name, 'r').read())
        #element_map = dict(zip(df.head(), self.columns))
        sm = SchemaMaker()
        return sm.create_schema([tf.name])
