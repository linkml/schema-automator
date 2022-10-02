import logging
from typing import Union, Dict, Tuple, List, Any, Optional

from dataclasses import dataclass

from linkml.utils.schema_builder import SchemaBuilder
from linkml_runtime.linkml_model.meta import SchemaDefinition, SlotDefinition, EnumDefinition, \
    PermissibleValue, UniqueKey, ClassDefinition
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


def _add_unique_keys(cls: ClassDefinition, name: str, slot_names: List[str]):
    uk = UniqueKey(name, unique_key_slots=slot_names)
    cls.unique_keys[name] = uk


@dataclass
class FrictionlessImportEngine(ImportEngine):
    """
    An ImportEngine that imports Frictionless data packages with schema information

    See:

     `Frictionless specs <https://specs.frictionlessdata.io/>`_
     `Patterns <https://specs.frictionlessdata.io/patterns/>`_

    """

    def convert(self, file: str, id: str,name: str, **kwargs) -> SchemaDefinition:
        """
        Converts one or more JSON files into a Schema

        :param files:
        :param kwargs:
        :return:
        """
        package: fl.Package = json_loader.load(file, target_class=fl.Package)
        sb = SchemaBuilder()
        schema = sb.schema
        if id:
            schema.id = id
            if name:
                sb.add_prefix(name, f"{id}/")
        if not name:
            name = package.name
        if name:
            schema.name = name
        schema.description = package.title
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
                        _add_unique_keys(cls, f"{slot.name}_unique_key", [slot.name])
                if field.enum:
                    e = self.add_enum(sb, field)
                    slot.range = e.name
                elif field.type:
                    t = str(field.type)
                    if field.type == fl.TypeEnum(fl.TypeEnum.array):
                        slot.multivalued = True
                    else:
                        slot.range = TYPE_MAPPING[t]
            if tbl.primaryKey:
                pks = tbl.primaryKey
                if len(pks) > 1:
                    _add_unique_keys(cls, f"{cls.name}_primary_key", [pks])
                else:
                    cls.attributes[pks[0]].identifier = True
            if tbl.foreignKeys:
                for fk in tbl.foreignKeys:
                    fk_fields = fk.fields
                    if isinstance(fk_fields, list) and len(fk_fields) > 1:
                        logging.warning(f"Cannot handle compound FKs: {cls.name}.[{fk_fields}]")
                    else:
                        if isinstance(fk_fields, list):
                            fk_field = fk_fields[0]
                        else:
                            fk_field = fk_fields
                        if fk_field:
                            fk_slot = cls.attributes[fk_field]
                            fk_slot.range = fk.reference.resource
                            # assume fk.fields is the PK
        sb.add_defaults()
        if name:
            schema.default_prefix = name
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




