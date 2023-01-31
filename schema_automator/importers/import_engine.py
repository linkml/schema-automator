from abc import ABC
from dataclasses import dataclass

from linkml_runtime.linkml_model import SchemaDefinition, Prefix


@dataclass
class ImportEngine(ABC):
    """
    Abstract Base Class for all Import Engines.

    Import Engines take some kind of input and import into a new SchemaDefinition
    """

    def convert(self, file: str, **kwargs) -> SchemaDefinition:
        raise NotImplementedError

    def add_prefix(self, schema: SchemaDefinition, prefix: str, url: str):
        schema.prefixes[prefix] = Prefix(prefix, url)

    def add_default_prefixes(self, schema: SchemaDefinition):
        self.add_prefix(schema, 'linkml', 'https://w3id.org/linkml/')