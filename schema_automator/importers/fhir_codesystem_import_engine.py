import json
from typing import Dict, Any

from linkml_runtime.linkml_model import SchemaDefinition, EnumDefinition, PermissibleValue
from schema_automator.importers.import_engine import ImportEngine

class FHIRCodeSystemImportEngine(ImportEngine):
    def load(self, input: str) -> SchemaDefinition:
        # Parse the JSON input
        data = json.loads(input)

        # Create a new SchemaDefinition
        schema = SchemaDefinition(
            name=data.get('name', 'FHIRCodeSystem'),
            id=data.get('url', 'http://example.org/FHIRCodeSystem')
        )

        # Define the Enum for the CodeSystem
        code_system_enum = EnumDefinition(
            name='CodeSystemEnum',
            description=data.get('description', 'A FHIR CodeSystem resource')
        )

        # Process the concepts and create permissible values
        if 'concept' in data:
            code_system_enum.permissible_values = self._process_concepts(data['concept'])

        # Add the Enum to the schema
        schema.enums = {
            'CodeSystemEnum': code_system_enum
        }

        return schema

    def _process_concepts(self, concepts: Dict[str, Any]) -> Dict[str, PermissibleValue]:
        permissible_values = {}

        for concept in concepts:
            code = concept['code']
            pv = PermissibleValue(
                text=code,
                title=concept.get('display', None),
                description=concept.get('definition', None),
            )

            # Check for parent relationships in properties
            for prop in concept.get('property', []):
                if prop['code'] == 'subsumedBy':
                    pv.is_a = prop['valueCode']
                if prop['code'] == 'status':
                    pv.status = prop['valueCode']

            permissible_values[code] = pv

        return permissible_values

