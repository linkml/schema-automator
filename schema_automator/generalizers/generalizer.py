from abc import ABC
from collections.abc import Collection, Set
from dataclasses import dataclass, field
from typing import List

import inflect
from linkml_runtime.linkml_model import SchemaDefinition, Prefix

DEFAULT_CLASS_NAME = 'Observation'
DEFAULT_SCHEMA_NAME = 'MySchema'


@dataclass
class Generalizer(ABC):
    """
    Abstract Base Class for all Generalization Engines.

    Generalization Engines take example data in some format and generalizes to a new SchemaDefinition
    """

    identifier_slots: List[str] = field(default_factory=lambda: [])
    """Slots asserted to be identifiers"""

    depluralize_class_names: bool = field(default_factory=lambda: False)

    inflect_engine: inflect.engine = field(default_factory=lambda: inflect.engine())


    def convert(self, file: str, **kwargs) -> SchemaDefinition:
        raise NotImplementedError

    def add_prefix(self, schema: SchemaDefinition, prefix: str, url: str):
        schema.prefixes[prefix] = Prefix(prefix, url)

    def add_default_prefixes(self, schema: SchemaDefinition):
        self.add_prefix(schema, 'linkml', 'https://w3id.org/linkml/')

    def add_additional_info(self, schema: SchemaDefinition) -> None:
        for s in self.identifier_slots:
            schema.slots[s].identifier = True