import click
from typing import Union, Dict, List, Any, Type

import pandas as pd
import pandera as pa
from dataclasses import dataclass

from linkml.utils.schema_builder import SchemaBuilder
from linkml.utils.schema_fixer import SchemaFixer
from linkml_runtime.linkml_model import SchemaDefinition, ClassDefinition, SlotDefinition
from pandera import Column

from schema_automator import CsvDataGeneralizer
from schema_automator.generalizers.generalizer import DEFAULT_CLASS_NAME

DATA_TYPE_MAP = {
    pa.Int: 'integer',
    pa.Float: 'float',
    pa.String: 'string',
    pa.DateTime: 'datetime',
}

def map_dtype(t: Type) -> str:
    for type_cls, rng in DATA_TYPE_MAP.items():
        if isinstance(t, type_cls):
            return rng
    return 'string'


@dataclass
class PandasDataGeneralizer(CsvDataGeneralizer):
    """
    A generalizer that abstracts from Pandas data frames
    """

    def convert(self, input: Union[pd.DataFrame, str], format: str = 'tsv',
                container_class_name='Container',
                class_name=DEFAULT_CLASS_NAME,
                **kwargs) -> SchemaDefinition:
        if isinstance(input, str):
            df = pd.read_csv(input, sep=self.column_separator)
        elif isinstance(input, pd.DataFrame):
            df = input
        else:
            raise ValueError(f"{input} must be DataFrame or path to TSV")
        c = self.from_dataframe(df, class_name=class_name)
        sb = SchemaBuilder(self.schema_name)
        sb.add_defaults()
        schema = sb.schema
        schema.classes[c.name] = c
        sf = SchemaFixer()
        sf.add_container(schema, class_name=container_class_name)
        return schema

    def from_dataframe(self, df: pd.DataFrame, class_name=DEFAULT_CLASS_NAME) -> ClassDefinition:
        ps = pa.infer_schema(df)
        return self.from_dataframe_schema(ps, class_name=class_name)

    def from_dataframe_schema(self, ps: pa.DataFrameSchema, class_name=DEFAULT_CLASS_NAME) -> ClassDefinition:
        if ps.name:
            name = ps.name
        else:
            name = class_name
        c = ClassDefinition(name)
        for col_name, col in ps.columns.items():
            slot = self.from_column(col_name, col)
            c.attributes[slot.name] = slot
        return c

    def from_column(self, col_name: str, col: Column) -> SlotDefinition:
        return SlotDefinition(col_name,
                              range=map_dtype(col.dtype))

