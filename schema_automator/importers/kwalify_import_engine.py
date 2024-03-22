from typing import Union, Dict, Tuple, List, Any, Optional

from dataclasses import dataclass

import yaml
from linkml.utils.schema_builder import SchemaBuilder
from linkml_runtime.linkml_model.meta import SchemaDefinition, SlotDefinition, EnumDefinition, \
    PermissibleValue, UniqueKey, ClassDefinition
from linkml_runtime.utils.formatutils import camelcase

from schema_automator.importers.import_engine import ImportEngine
import schema_automator.metamodels.frictionless as fl


# maps from kwalify to linkml
TYPE_MAPPING = {
    "str": "string",
    "int": "integer",
    "float": "float",
    "bool": "boolean",
    "timestamp": "datetime",
}



@dataclass
class KwalifyImportEngine(ImportEngine):
    """
    An ImportEngine that imports Kwalify schemas
    """

    def convert(self, file: str, id: str=None, name: str=None, class_name: str=None, **kwargs) -> SchemaDefinition:
        """
        Converts one or more Kwalify files into a Schema

        :param files:
        :param kwargs:
        :return:
        """
        sb = SchemaBuilder()
        schema = sb.schema
        if id:
            schema.id = id
        if not name:
            name = "example"
        if name:
            schema.name = name
        kwalify = yaml.safe_load(open(file))
        if kwalify["type"] != "map":
            raise ValueError(f"Expected map, got {kwalify['type']}")
        if class_name is None:
            class_name = camelcase(name)
        self.convert_to_class(sb, kwalify["mapping"], class_name)
        sb.add_defaults()
        if name:
            schema.default_prefix = name
        return sb.schema

    def convert_to_class(self, sb: SchemaBuilder, kwalify_map: Dict[str, Any], name: str):
        """
        Convert a Kwalify map to a class

        :param sb:
        :param kwalify:
        :param name:
        :return:
        """
        cls = ClassDefinition(name=name)
        sb.schema.classes[name] = cls
        for slot_name, v in kwalify_map.items():
            if isinstance(v, list):
                if len(v) != 1:
                    raise ValueError(f"Expected single element in list, got {v}")
                v = v[0]
            slot = SlotDefinition(name=slot_name, required=v.get('required', False))
            pattern = v.get('pattern', None)
            if pattern:
                # remove outer /..../
                slot.pattern = pattern[1:-1]

            typ = v['type']
            if typ == 'seq':
                slot.multivalued = True
                seq = v['sequence']
                if len(seq) != 1:
                    raise ValueError(f"Expected single element in sequence, got {seq}")
                v = seq[0]
                typ = v['type']
            if typ == 'map':
                range_cls_name = camelcase(slot_name)
                self.convert_to_class(sb, v["mapping"], range_cls_name)
                slot.range = range_cls_name
            elif typ == 'seq':
                raise NotImplementedError("Sequences of sequences not supported")
            else:
                slot.range = TYPE_MAPPING.get(typ, "string")
            pvs = v.get('enum', None)
            if pvs:
                enum_name = f"{name}_{slot_name}_enum"
                sb.add_enum(EnumDefinition(name=enum_name, permissible_values=pvs))
                slot.range = enum_name
            cls.attributes[slot_name] = slot







