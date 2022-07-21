from abc import ABC
from dataclasses import dataclass

from linkml_runtime.linkml_model import SchemaDefinition, Prefix

DEFAULT_CLASS_NAME = 'Observation'
DEFAULT_SCHEMA_NAME = 'MySchema'


@dataclass
class Generalizer(ABC):
    """
    Abstract Base Class for all Generalization Engines.

    Generalization Engines take example data in some format and generalizes to a new SchemaDefinition
    """

    def convert(self, file: str, **kwargs) -> SchemaDefinition:
        raise NotImplementedError

    def add_prefix(self, schema: SchemaDefinition, prefix: str, url: str):
        schema.prefixes[prefix] = Prefix(prefix, url)

    def add_default_prefixes(self, schema: SchemaDefinition):
        self.add_prefix(schema, 'linkml', 'https://w3id.org/linkml/')