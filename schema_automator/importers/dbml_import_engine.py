from schema_automator.importers.import_engine import ImportEngine
from pydbml import PyDBML
from linkml_runtime.linkml_model import SchemaDefinition, ClassDefinition, SlotDefinition
from dataclasses import dataclass


def _map_dbml_type_to_linkml(dbml_type: str) -> str:
    """
    Maps DBML data types to LinkML types.

    :param dbml_type: The DBML column type.
    :return: Corresponding LinkML type.
    """
    type_mapping = {
        "int": "integer",
        "varchar": "string",
        "text": "string",
        "float": "float",
        "boolean": "boolean",
        "date": "date",
        "datetime": "datetime",
    }
    return type_mapping.get(dbml_type.lower(), "string")


@dataclass
class DbmlImportEngine(ImportEngine):
    """
    An ImportEngine that introspects a DBML schema to determine a corresponding LinkML schema.
    """

    def convert(
            self,
            file: str,
            name: str = None,
            model_uri: str = None,
            identifier: str = None,
            **kwargs
    ) -> SchemaDefinition:
        """
        Converts a DBML schema file into a LinkML SchemaDefinition.

        :param file: Path to the DBML schema file.
        :param name: Optional name for the generated LinkML schema.
        :param model_uri: Optional URI for the schema.
        :param identifier: Identifier field for the schema.
        :return: SchemaDefinition object representing the DBML schema.
        """
        # Initialize the schema definition
        schema_name = name or "GeneratedSchema"
        schema = SchemaDefinition(name=schema_name, id=model_uri or f"https://example.org/{schema_name}")

        # Parse the DBML file
        with open(file, 'r', encoding='utf-8') as f:
            dbml_content = f.read()
        parsed_dbml = PyDBML(dbml_content)

        # Process tables
        for table in parsed_dbml.tables:
            class_def = ClassDefinition(
                name=table.name,
                description=table.note or f"Auto-generated class for table '{table.name}'",
                slots=[],
                unique_keys=[],  # Initialize unique keys property
            )
            processed_slots = set()  # Track processed slot names to avoid duplicates

            # Handle primary key and unique constraints
            primary_key_columns = [col for col in table.columns if col.pk]
            unique_columns = [col for col in table.columns if col.unique and not col.pk]

            # Process columns
            for column in table.columns:

                slot_name = column.name
                slot_def = SlotDefinition(
                    name=slot_name,
                    range=_map_dbml_type_to_linkml(column.type),
                    description=column.note or f"Column '{slot_name}'",
                    required=column in primary_key_columns or column.unique,
                    identifier=column in primary_key_columns,  # Mark primary key columns as identifiers
                )
                schema.slots[slot_name] = slot_def
                class_def.slots.append(slot_name)
                processed_slots.add(slot_name)

            # Handle single unique column as primary key if no explicit primary key exists
            if not primary_key_columns and len(unique_columns) == 1:
                unique_column = unique_columns[0]
                schema.slots[unique_column.name].identifier = True
                schema.slots[unique_column.name].required = True

            schema.classes[table.name] = class_def

        return schema
