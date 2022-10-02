import json

import click
import yaml
import logging
from copy import copy
from typing import Any, Tuple, Dict, Union, List, Optional

from linkml_runtime.linkml_model import SchemaDefinition, Element, ClassDefinition, \
    SlotDefinition, EnumDefinition, \
    ClassDefinitionName, \
    SlotDefinitionName, Prefix
from linkml_runtime.utils.formatutils import underscore

from schema_automator.importers.import_engine import ImportEngine
from schema_automator.utils.schemautils import minify_schema, write_schema

# TODO: move to core. https://github.com/linkml/linkml/issues/104
RESERVED = ['in', 'not', 'def']

class JsonSchemaImportEngine(ImportEngine):
    """
    A :ref:`ImportEngine` that imports a JSON-Schema representation to a LinkML Schema
    """

    def convert(self, input: str, name=None, format = 'json', **kwargs):
        """
        Converts a JSON-Schema json file into a LinkML schema

        :param input:
        :param name:
        :param format:
        :param kwargs:
        :return:
        """
        if format == 'json':
            with open(input) as stream:
                obj = json.load(stream)
        elif format == 'yaml':
            with open(input) as stream:
                obj = yaml.safe_load(stream)
        else:
            raise Exception(f'Bad format: {format}')
        return self.loads(obj, name, **kwargs)

    def load(self, input: str, name=None, format = 'json', **kwargs):
        return self.convert(input, name=name, format=format, **kwargs)

    def loads(self, obj: Any, name=None, **kwargs) -> SchemaDefinition:
        return self.translate_schema(obj, name, **kwargs)

    def get_id(self, obj) -> str:
        if 'id' in obj:
            id = obj['id']
        elif '$ref' in obj:
            id = obj['$ref']
        else:
            raise Exception(f'No id {obj}')
        return self.split_name(id)[0]

    def split_name(self, name) -> Tuple[str, str]:
        name = name.replace('#/definitions/', '')
        parts = name.split('.')
        name = parts.pop()
        pkg = '.'.join(parts)
        if pkg == '':
            pkg = None
        return name, pkg


    def translate_schema(self, obj: Dict, id_val=None, name=None, root_class_name=None) -> SchemaDefinition:
        if id_val is None and '$id' in obj:
            id_val = obj['$id']
        if id_val is None and '$schema' in obj:
            id_val = obj['$schema']
        if name is None and 'title' in obj:
            name = obj['title'].replace(' ','-')
        jsonschema_version = obj.get('$schema', None)
        if id_val is None and name is None:
            raise Exception(f'Must pass name OR id, or these must be present in the jsonschema')
        if name is None:
            name = id_val
        if id_val is None or not id_val.startswith('http'):
            id_val = f'https://example.org/{name}'
        name = underscore(name)
        self.schema = SchemaDefinition(id=id_val, name=name)
        if '$defs' in obj:
            self.translate_definitions(obj.get('$defs', {}))
        else:
            self.translate_definitions(obj.get('definitions', {}))
        if root_class_name is None:
            root_class_name = obj.get('title', None)
        if 'properties' in obj:
            root_class = ClassDefinition(root_class_name)
            self.translate_properties(obj, root_class)
            self.schema.classes[root_class_name] = root_class
        self.schema.default_prefix = name
        self.schema.prefixes[name] = Prefix(name, id_val)
        self.schema.prefixes['linkml'] = Prefix('linkml', 'https://w3id.org/linkml/')
        self.schema.imports.append('linkml:types')
        return self.schema

    def translate_definitions(self, obj: Dict):
        for k, v in obj.items():
            self.translate_object(v, k)

    def translate_array(self, obj: Dict, name: str) -> SlotDefinition:
        if 'items' in obj:
            items_obj = obj['items']
            uniqueItems = obj.get('uniqueItems', False)
            if isinstance(items_obj, str):
                # found in DOSDP: TODO: check
                items_obj = {'type': 'string'}
            if 'properties' in items_obj:
                slot = SlotDefinition(name)
                slot.range = self.translate_object(items_obj)
            else:
                slot = self.translate_property(items_obj, name)
            if 'description' in items_obj:
                slot.description = items_obj['description']
            slot.multivalued = True
            return slot
        elif 'properties' in obj:
            c = ClassDefinition(f'{name}Class')
            self.translate_properties(obj, c)
            self.schema.classes[c.name] = c
            slot = SlotDefinition(name)
            slot.range = c.name
            slot.multivalued = True
            return slot
        else:
            logging.error(f'NOT HANDLED: {obj} in array context')
            return None

    def translate_ref(self, obj: dict) -> ClassDefinitionName:
        return ClassDefinitionName(self.get_id(obj))

    def translate_oneOf(self, oneOfList: List) -> Optional[ClassDefinition]:
        if all('$ref' in x for x in oneOfList):
            cns = [self.translate_ref(x) for x in oneOfList]
            n = '_'.join(cns)
            c = ClassDefinition(n, union_of=cns)
            return c
        else:
            logging.warning(f'Cannot yet handle oneOfs without refs: {oneOfList}')
            return None

    def translate_property(self, obj: Dict, name: str) -> SlotDefinition:
        #print(f'Translating property {name}: {obj}')
        if name is None:
            raise ValueError(f'Name not set for {obj}')
        schema = self.schema
        aliases = []
        if name in RESERVED:
            aliases.append(name)
            name = f'_{name}'
        s = SlotDefinition(name)
        t = obj.get('type', None)
        s.description = obj.get('description', None)
        if s.description is not None:
            s.description = s.description.strip()
        default = obj.get('default', None)
        if '$ref' in obj:
            s.range = self.translate_ref(obj)
        elif t == 'array':
            s = self.translate_array(obj, name)
            if s is None:
                raise ValueError(f'Cannot translate array {name} {obj}')
        elif t == 'number':
            s.range = 'float'
        elif t == 'boolean':
            s.range = 'boolean'
        elif t == 'float':
            s.range = 'float'
        elif t == 'integer':
            s.range = 'integer'
            s.minimum_value = obj.get('minimum_value', None)
            s.maximum_value = obj.get('maximum_value', None)
        elif t == 'string':
            if 'enum' in obj:
                pvs = obj['enum']
                ename = f'{name}_options'
                schema.enums[ename] = EnumDefinition(name=ename, permissible_values=pvs)
                s.range = ename
        else:
            logging.error(f'Cannot translate type {t} in {obj}')
        if s.name is schema.slots:
            logging.warning(f'TODO: unify alternate slots')
        schema.slots[s.name] = s
        return s

    def translate_object(self, obj: Dict, name: str = None) -> ClassDefinitionName:
        """
        Translates jsonschema obj of type object

        Generates a ClassDefinition, inserts it into the schema, and returns the name
        """
        schema = self.schema
        t = obj.get('type', None)
        desc = obj.get('description', None)
        additional = obj.get('additionalProperties', False) ## TODO
        if 'oneOf' in obj:
            unionCls = self.translate_oneOf(obj.get('oneOf'))
        else:
            unionCls = None
        allOf = obj.get('allOf', None)
        title = obj.get('title', None)
        required = obj.get('required', [])

        properties = obj.get('properties', {})
        discriminator = obj.get('discriminator', None)  # In OpenAPI but not JSON-Schema
        pkg = None
        if name is None:
            name = obj.get('title', None)
        else:
            name, pkg = self.split_name(name)
            if name is None:
                raise ValueError(f'Problem splitting name from package')
        if name is None:
            name = 'TODO'
        c = ClassDefinition(name, description=desc, from_schema=pkg)
        if unionCls:
            c.union_of = unionCls.union_of
        for k, v in properties.items():
            # TODO: reuse below
            #print(f'  PROP {k} = {v}')
            slot = self.translate_property(v, k)
            if slot.name in required:
                slot.required = True
            c.slots.append(slot.name)
            c.slot_usage[slot.name] = slot
        schema.classes[c.name] = c
        return c.name


    def translate_properties(self, obj: dict, parent_class: ClassDefinition):
        required = obj.get('required', [])
        for k, v in obj.get('properties',{}).items():
            slot = self.translate_property(v, k)
            if slot.name in required:
                slot.required = True
            parent_class.slots.append(slot.name)
            parent_class.slot_usage[slot.name] = slot


@click.command()
@click.argument('input')
@click.option('--name', '-n', required=True, help='ID of schema')
@click.option('--format', '-f', default='json', help='JSON Schema format - yaml or json')
@click.option('--output', '-o', help='output path')
def jsonschema2model(input, output, name, format, **args):
    """ Infer a model from JSON Schema """
    ie = JsonSchemaImportEngine()
    schema = ie.load(input, name=name, format=format)
    write_schema(schema, output)


if __name__ == '__main__':
    jsonschema2model()




