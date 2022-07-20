from pathlib import Path

from typing import Union, Dict, Tuple, List, Any

from linkml.utils.schema_builder import SchemaBuilder
from linkml_runtime.linkml_model import SchemaDefinition, SlotDefinition

from dataclasses import dataclass

from sqlalchemy import create_engine, MetaData

from schema_automator.importers.import_engine import ImportEngine


@dataclass
class SqlImportEngine(ImportEngine):
    """
    An ImportEngine that takes a SQL database and introspects a schema

    Limitations:

    - Currently only works for SQLite
    - Only does the basic bare bones import - need to introspect properties
    """
    engine: Any = None   ## TODO: determine typing info for SQL Alchemy

    def convert(self, file: str, name: str = None, model_uri: str = None, identifier: str = None, **kwargs) -> \
            SchemaDefinition:
        path = Path(file).absolute()
        locator = f"sqlite:///{path}"
        engine = create_engine(locator)
        self.engine = engine
        metadata_obj = MetaData()
        metadata_obj.reflect(bind=engine)
        sb = SchemaBuilder()
        schema = sb.schema
        for table in metadata_obj.sorted_tables:
            sb.add_class(table.name)
            cls = schema.classes[table.name]
            for column in table.columns:
                slot = SlotDefinition(column.name)
                cls.attributes[slot.name] = slot
        return schema


