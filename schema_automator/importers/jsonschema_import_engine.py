import json
from dataclasses import dataclass
from pathlib import Path

import click
import yaml
import logging
from typing import Any, Tuple, Dict, List, Optional

from linkml.utils.schema_builder import SchemaBuilder
from linkml_runtime.linkml_model import SchemaDefinition, ClassDefinition, \
    SlotDefinition, EnumDefinition, \
    ClassDefinitionName, Prefix
from linkml_runtime.linkml_model.meta import ReachabilityQuery, AnonymousEnumExpression
from linkml_runtime.utils.formatutils import underscore, camelcase

from schema_automator.importers.import_engine import ImportEngine
from schema_automator.utils.schemautils import write_schema

# TODO: move to core. https://github.com/linkml/linkml/issues/104
RESERVED = ['in', 'not', 'def']


def json_schema_from_open_api(oa: Dict) -> Dict:
    """
    Convert an OpenAPI schema to a JSON-Schema schema

    :param oa:
    :return:
    """
    schemas = oa.get('components', {}).get('schemas', {})
    schema = {'$defs': schemas}
    return schema

@dataclass
class JsonSchemaImportEngine(ImportEngine):
    """
    An ImportEngine that imports a JSON-Schema representation to a LinkML Schema
    """
    use_attributes: bool = False
    is_openapi: bool = False

    def convert(self, input: str, name=None, format = 'json', **kwargs) -> SchemaDefinition:
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
        return self.loads(obj, name, input_path=input, **kwargs)

    def import_project(self, import_directory: str, export_directory: str, match_suffix=".json", name=None, **kwargs) -> str:
        path = Path(import_directory)
        export_path = Path(export_directory)
        imports_list = []
        importer_name = "main.yaml"
        if name is None:
            name = "imported"
        path_to_schema_map = {}
        class_name_to_module_map = {}
        for item in path.rglob("*"):
            if str(item).endswith(match_suffix):
                relpath = item.relative_to(path)
                module_name = str(relpath.with_suffix("").as_posix())
                module_name_safe = "-".join(relpath.with_suffix("").parts)
                logging.info(f"Converting {item} => {module_name_safe}")
                schema = self.convert(str(item), name=module_name_safe, **kwargs)
                output_path = export_path / relpath
                output_path = output_path.with_suffix(".yaml")
                output_path.parent.mkdir(parents=True, exist_ok=True)
                path_to_schema_map[output_path] = schema
                if str(output_path) == importer_name:
                    raise ValueError(f"Must choose new importer_name: {output_path}")
                imports_list.append(module_name)
                for cn in schema.classes:
                    if cn in class_name_to_module_map:
                        raise ValueError(f"Class name clash; {cn} is in {module_name} and {class_name_to_module_map[cn]}")
                    class_name_to_module_map[cn] = module_name
        # add imports based on ranges
        for this_module, schema in path_to_schema_map.items():
            relpath = this_module.relative_to(export_path)
            logging.debug(f"Relative path {relpath} for module at: {this_module}")
            depth = len(relpath.parts) - 1
            rel = "../" * depth
            for cls in schema.classes.values():
                for a in cls.attributes.values():
                    rng = a.range
                    if rng not in class_name_to_module_map:
                        continue
                    if rng in schema.classes:
                        # no need to self-import
                        continue
                    import_module_name = class_name_to_module_map[rng]
                    if import_module_name not in schema.imports:
                        logging.info(f"Adding import to {import_module_name} in {schema.name} for {rng}")
                        schema.imports.append(import_module_name)
        for output_path, schema in path_to_schema_map.items():
            write_schema(schema, output_path)
        sb = SchemaBuilder(name=name)
        sb.add_defaults()
        s = sb.schema
        for i in imports_list:
            s.imports.append(i)
        importer_path = export_path / importer_name
        write_schema(s, importer_path)
        return str(importer_path)


    def load(self, input: str, name=None, format = 'json', **kwargs):
        return self.convert(input, name=name, format=format, **kwargs)

    def loads(self, obj: Any, name=None, **kwargs) -> SchemaDefinition:
        if self.is_openapi:
            obj = json_schema_from_open_api(obj)
        return self.translate_schema(obj, name, **kwargs)

    def _class_name(self, cn: str) -> str:
        # in future this can be configurable
        return camelcase(cn)

    def get_id(self, obj) -> str:
        if 'id' in obj:
            id = obj['id']
        elif '$ref' in obj:
            id = obj['$ref']
        else:
            raise Exception(f'No id {obj}')
        if id.startswith("#/definitions/"):
            return self.split_name(id)[0]
        else:
            return self._class_name(Path(str(id)).stem)

    def split_name(self, name) -> Tuple[str, str]:
        name = name.replace('#/definitions/', '')
        parts = name.split('.')
        name = parts.pop()
        pkg = '.'.join(parts)
        if pkg == '':
            pkg = None
        return name, pkg


    def translate_schema(self, obj: Dict, id_val=None, name=None, root_class_name=None, input_path: str = None) -> SchemaDefinition:
        if id_val is None and '$id' in obj:
            id_val = obj['$id']
        if id_val is None and '$schema' in obj:
            id_val = obj['$schema']
        if name is None and 'title' in obj:
            name = obj['title'].replace(' ','-')
            if name[0].isnumeric():
                name = f"_{name}"
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
            root_class_name = obj.get('name', None)
        if root_class_name is None:
            root_class_name = obj.get('title', None)
        if root_class_name is None and input_path:
            root_class_name = Path(input_path).stem
        if root_class_name is None:
            raise ValueError(f'No root class name: {obj}')
        root_class_name = self._class_name(root_class_name)
        if 'properties' in obj:
            logging.info(f'Root class: {root_class_name}')
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
            c = ClassDefinition(f'{self._class_name(name)}Class')
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
        return ClassDefinitionName(self._class_name(self.get_id(obj)))

    def translate_oneOf(self, oneOfList: List) -> Optional[ClassDefinition]:
        if all('$ref' in x for x in oneOfList):
            cns = [self.translate_ref(x) for x in oneOfList]
            n = self._class_name('_'.join(cns))
            c = ClassDefinition(n, union_of=cns)
            return c
        else:
            logging.warning(f'Cannot yet handle oneOfs without refs: {oneOfList}')
            return None

    def translate_property(self, obj: Dict, name: str, class_name: str = None) -> SlotDefinition:
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
        # HCA-specific
        s.title = obj.get("user_friendly", None)
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
                if self.use_attributes and class_name:
                    ename = f'{class_name}_{name}_options'
                else:
                    ename = f'{name}_options'
                schema.enums[ename] = EnumDefinition(name=ename, permissible_values=pvs)
                s.range = ename
            self._enum_from_ontology_extension(s, obj, name, class_name=class_name)
        else:
            logging.error(f'Cannot translate type {t} in {obj}')
        if s.name is schema.slots:
            logging.warning(f'TODO: unify alternate slots')
        if not self.use_attributes:
            schema.slots[s.name] = s
        return s

    def _enum_from_ontology_extension(self, slot: SlotDefinition, js_obj: dict, name: str, class_name: str = None):
        gr = js_obj.get("graph_restriction", None)
        if not gr:
            return
        if self.use_attributes and class_name:
            ename = f'{class_name}_{name}_options'
        else:
            ename = f'{name}_options'
        rqs = []
        for ont in gr["ontologies"]:
            rq = ReachabilityQuery(source_ontology=ont,
                                   source_nodes=gr.get("classes", []),
                                   include_self=gr.get("include_self", False),
                                   is_direct=gr.get("direct", False),
                                   relationship_types=gr.get("relations", []),
                                   )
            rqs.append(rq)

        if len(rqs) == 0:
            logging.warning(f"No ontologies in {gr}")
            return
        elif len(rqs) == 1:
            edef = EnumDefinition(ename, reachable_from = rqs[0])
        else:
            includes = [AnonymousEnumExpression(reachable_from=rq) for rq in rqs]
            edef = EnumDefinition(ename, include=includes)
        self.schema.enums[ename] = edef
        slot.range = ename

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
        name = self._class_name(name)
        c = ClassDefinition(name, description=desc, from_schema=pkg)
        if unionCls:
            c.union_of = unionCls.union_of
        for k, v in properties.items():
            # TODO: reuse below
            slot = self.translate_property(v, k, class_name=name)
            if slot.name in required:
                slot.required = True
            if self.use_attributes:
                c.attributes[slot.name] = slot
            else:
                c.slots.append(slot.name)
                c.slot_usage[slot.name] = slot
        schema.classes[c.name] = c
        return c.name


    def translate_properties(self, obj: dict, parent_class: ClassDefinition):
        required = obj.get('required', [])
        for k, v in obj.get('properties',{}).items():
            slot = self.translate_property(v, k, class_name=parent_class.name)
            if slot.name in required:
                slot.required = True
            if self.use_attributes:
                parent_class.attributes[slot.name] = slot
            else:
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




