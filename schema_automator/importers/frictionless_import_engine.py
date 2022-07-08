from typing import Union, Dict, Tuple, List, Any, Optional

from dataclasses import dataclass

from linkml.utils.schema_builder import SchemaBuilder
from linkml_runtime.linkml_model.meta import SchemaDefinition, SlotDefinition, EnumDefinition, \
    PermissibleValue, UniqueKey
from linkml_runtime.loaders import json_loader
from linkml_runtime.utils.formatutils import camelcase

from schema_automator.importers.import_engine import ImportEngine
import schema_automator.metamodels.frictionless as fl


TYPE_MAPPING = {
    "string": "string",
    "datetime": "datetime",
    "boolean": "boolean",
    "integer": "integer",
    "number": "decimal",
}


def _desc(elt: Union[fl.Field, fl.Resource]) -> Optional[str]:
    if elt.description:
        return elt.description[0]
    else:
        return None


@dataclass
class FrictionlessImportEngine(ImportEngine):
    """
    An ImportEngine that imports Frictionless data packages with schema information

    See:

     `Frictionless specs <https://specs.frictionlessdata.io/>`_
     `Patterns <https://specs.frictionlessdata.io/patterns/>`_

    """

    def convert(self, file: str, **kwargs) -> SchemaDefinition:
        """
        Converts one or more JSON files into a Schema

        :param files:
        :param kwargs:
        :return:
        """
        package: fl.Package = json_loader.load(file, target_class=fl.Package)
        sb = SchemaBuilder()
        schema = sb.schema
        for resource in package.resources:
            sb.add_class(resource.name)
            cls = schema.classes[resource.name]
            cls.description = _desc(resource)
            cls.title = resource.title
            tbl = resource.schema
            for field in tbl.fields:
                slot = SlotDefinition(field.name, description=_desc(field))
                cls.attributes[slot.name] = slot
                constraints = field.constraints
                if constraints:
                    slot.required = constraints.required
                    slot.pattern = constraints.pattern
                    if constraints.unique is True:
                        n = f"{slot.name}_unique_key"
                        uk = UniqueKey(n, unique_key_slots=[slot.name])
                        cls.unique_keys[n] = uk
                if field.enum:
                    e = self.add_enum(sb, field)
                    slot.range = e.name
                elif field.type:
                    t = str(field.type)
                    if field.type == fl.TypeEnum(fl.TypeEnum.array):
                        slot.multivalued = True
                    else:
                        slot.range = TYPE_MAPPING[t]
        sb.add_defaults()
        for c in schema.classes.values():
            c.from_schema = 'http://example.org/'
        return sb.schema

    def add_enum(self, sb: SchemaBuilder, field: fl.Field) -> EnumDefinition:
        name = camelcase(f"{field.name}_enum")
        e = EnumDefinition(name)
        for code in field.enum:
            pv = PermissibleValue(code)
            # TODO: this behavior may be specific to C2M2, make this configurable
            if ":" in code:
                toks = code.split(":")
                if len(toks) == 2:
                    [prefix, short] = toks
                    pv = PermissibleValue(short, meaning=code)
                    sb.add_prefix(prefix, f"{sb.schema.id}/{prefix}/")
            e.permissible_values[pv.text] = pv
        if e.name is sb.schema:
            raise NotImplementedError(f"Cannot yet merge enums")
        sb.schema.enums[e.name] = e
        return e




