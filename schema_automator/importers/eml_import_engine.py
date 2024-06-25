"""Import engine for importing EML files as LinkML schema."""

import logging

from dataclasses import dataclass

from linkml.utils.schema_builder import SchemaBuilder
from linkml_runtime.linkml_model.meta import (
    SchemaDefinition,
    SlotDefinition,
    EnumDefinition,
    PermissibleValue,
)
from linkml_runtime.loaders import json_loader
from linkml_runtime.utils.formatutils import camelcase

from schema_automator.importers.import_engine import ImportEngine
import schema_automator.metamodels.eml as eml


TYPE_MAPPING = {
    "string": "string",
    "datetime": "datetime",
    "boolean": "boolean",
    "integer": "integer",
    "number": "decimal",
}


@dataclass
class EMLImportEngine(ImportEngine):
    """
    An ImportEngine that imports Environmental Metadata Language (EML) files into LinkML schemas.

    See:

     `EML documentation <https://eml.ecoinformatics.org/>`_
     `EML xml schema <https://eml.ecoinformatics.org/eml-schema>`_

    """

    def convert(
        self, file: str, id: str = None, name: str = None, **kwargs
    ) -> SchemaDefinition:
        """
        Converts EML data and metadata into a Schema

        :param files:
        :param kwargs:
        :return:
        """
        package: eml.Document = json_loader.load(file, target_class=eml.Document)
        sb = SchemaBuilder()
        schema = sb.schema
        return sb.schema
