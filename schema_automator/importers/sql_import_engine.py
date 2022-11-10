import logging
from pathlib import Path

from typing import Union, Dict, Tuple, List, Any, Type

from linkml.utils.schema_builder import SchemaBuilder
from linkml_runtime.linkml_model import SchemaDefinition, SlotDefinition

from dataclasses import dataclass

from sqlalchemy import create_engine, MetaData
import sqlalchemy.sql.sqltypes as sqlt

from schema_automator.importers.import_engine import ImportEngine

TYPE_MAP = {
    sqlt.TEXT: 'string',
    sqlt.INTEGER: 'integer',
    sqlt.FLOAT: 'float',
}

def _map_type(typ: Type) -> str:
    for k, v in TYPE_MAP.items():
        if isinstance(typ, k):
            return v
    return 'string'


@dataclass
class SqlImportEngine(ImportEngine):
    """
    An ImportEngine that introspects an SQL schema to determine a corresponding LinkML schema
    """
    engine: Any = None   ## TODO: determine typing info for SQL Alchemy

    def convert(
            self,
            file: str,
            name: str = None,
            model_uri: str = None,
            identifier: str = None,
            **kwargs
    ) -> SchemaDefinition:
        """
        Converts a SQL database

        :param file: path to SQLite OR an SQL Alchemy locator
        :param name:
        :param model_uri:
        :param identifier:
        :param kwargs:
        :return:
        """
        if '://' not in file:
            path = Path(file).resolve()
            locator = f"sqlite:///{path}"
        else:
            locator = file
        logging.info(f"Connecting to {locator}")
        engine = create_engine(locator)
        self.engine = engine
        metadata_obj = MetaData()
        logging.info(f"Reflecting using {engine}")
        metadata_obj.reflect(bind=engine)
        sb = SchemaBuilder()
        schema = sb.schema
        for table in metadata_obj.sorted_tables:
            logging.info(f"Importing {table.name}")
            sb.add_class(table.name)
            cls = schema.classes[table.name]
            pks = [column for column in table.columns if column.primary_key]
            if len(pks) == 1:
                pk = pks.pop().name
            else:
                pk = None
            for column in table.columns:
                slot = SlotDefinition(column.name)
                cls.attributes[slot.name] = slot
                if pk and pk == column.name:
                    slot.identifier = True
                if column.foreign_keys:
                    for fk in column.foreign_keys:
                        [fk_table, fk_table_col] = str(fk.column).split('.')
                        slot.range = fk_table
                else:
                    slot.range = _map_type(column.type)
        return schema


