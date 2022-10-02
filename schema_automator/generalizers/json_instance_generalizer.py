import logging

import click
from typing import Union, Dict, List, Any, Mapping, Collection
from collections import defaultdict
import json

import tomlkit
import yaml
import gzip

from dataclasses import dataclass, field

from linkml_runtime import SchemaView
from linkml_runtime.linkml_model import SchemaDefinition, SlotDefinitionName

from schema_automator.generalizers.generalizer import Generalizer
from schema_automator.generalizers.csv_data_generalizer import CsvDataGeneralizer
from linkml_runtime.utils.formatutils import camelcase

from schema_automator.utils.schemautils import write_schema


@dataclass
class JsonDataGeneralizer(Generalizer):
    """
    A generalizer that abstract from JSON instance data
    """
    mappings: dict = None
    omit_null: bool = None

    inline_as_dict_slot_keys: Mapping[str, str] = None
    """Mapping between the name of a dict-inlined slot and the unique key for that entity
    """



    def convert(self, input: Union[str, Dict], format: str = 'json',
                container_class_name='Container',
                **kwargs) -> SchemaDefinition:
        """
        Generalizes from a JSON file

        :param input:
        :param format:
        :param container_class_name:
        :param kwargs:
        :return:
        """
        csv_engine = CsvDataGeneralizer(**kwargs)

        if isinstance(input, dict):
            obj = input
        else:
            if format.endswith('.gz'):
                format = format.replace('.gz', '')
                stream = gzip.open(input)
            else:
                stream = open(input)
            with stream:
                if format == 'json':
                    obj = json.load(stream)
                elif format == 'yaml':
                    obj = yaml.safe_load(stream)
                elif format == 'toml':
                    obj_str = "".join(stream.readlines())
                    toml_obj = tomlkit.parse(obj_str)
                    json_str = json.dumps(toml_obj)
                    obj = json.loads(json_str)
                else:
                    raise Exception(f'bad format {format}')
        rows_by_table = defaultdict(list)
        self.rows_by_table = rows_by_table
        self._convert_obj(obj, table=container_class_name)
        schemas = []
        for cn, rows_dict in rows_by_table.items():
            schema = csv_engine.convert_dicts(rows_dict, cn, cn)
            schemas.append(schema)
        sv = SchemaView(schemas[0])
        for s in schemas[1:]:
            sv.merge_schema(s)
        schema = sv.schema
        schema.classes[container_class_name].tree_root = True
        self.add_additional_info(schema)
        return schema

    def _key_to_classname(self, k: str) -> str:
        return camelcase(k)

    def _convert_obj(self, obj, table='Container'):
        """
        Recursively transform an object into flattened key-value lists

        :param obj:
        :param table:
        :return:
        """
        if isinstance(obj, dict):
            row = defaultdict(set)
            for k, v in obj.items():
                if v is None and self.omit_null:
                    continue
                if self.inline_as_dict_slot_keys and k in self.inline_as_dict_slot_keys:
                    key_name = self.inline_as_dict_slot_keys[SlotDefinitionName(k)]
                    self.identifier_slots.append(key_name)
                    #print(f"INLINED: {key_name} = {v}")
                    v = self._inlined_dict_to_list(v, key_name)
                tbl_name = k
                if self.depluralize_class_names:
                    singular_noun = self.inflect_engine.singular_noun(tbl_name)
                    if singular_noun:
                        logging.info(f"Depluralized: {tbl_name} => {singular_noun}")
                        tbl_name = singular_noun
                tbl_name = camelcase(tbl_name)
                row[k] = self._convert_obj(v, table=tbl_name)
            self.rows_by_table[table].append(row)
            return f'$ref:{table}'
        elif isinstance(obj, list):
            new_list = [self._convert_obj(v, table=table) for v in obj]
            return new_list
        else:
            return obj

    def _inlined_dict_to_list(self, inlined_dict: Dict[str, dict], key_name: str) -> list:
        rows = []
        for k, v in inlined_dict.items():
            if isinstance(v, dict):
                rows.append({**v, key_name: k})
            elif isinstance(v, list):
                raise ValueError(f"Cannot handle an inlined dict of form {inlined_dict} for key={k}")
            else:
                rows.append({key_name: k, f"{key_name}_value": v})
        return rows



    def _as_name(self, v):
        v = str(v)
        for sep in ['#', '/']:
            if sep in v:
                return v.split(sep)[-1]
        return v

def parse_frontmatter_files(paths: List[str], text_slot='_text') -> Any:
    blocks = []
    for path in paths:
        with open(path) as stream:
            state = 0
            yamlstr = ""
            txt = ""
            for line in stream.readlines():
                if line.startswith('---'):
                    state += 1
                else:
                    if state == 1:
                        yamlstr += line
                    elif state == 2:
                        txt += line
                    elif state > 2:
                        raise Exception(f'Limited to one frontmatter block per file')
            obj = yaml.safe_load(yamlstr)
            obj[text_slot] = txt
            blocks.append(obj)
    return blocks



@click.command()
@click.argument('input')
@click.option('--container-class-name', help="name of root class")
@click.option('--format', '-f', default='json', help="json or yaml (or json.gz or yaml.gz) or frontmatter")
@click.option('--enum-columns', '-E', multiple=True, help='column(s) that is forced to be an enum')
@click.option('--enum-mask-columns', multiple=True, help='column(s) that are excluded from being enums')
@click.option('--max-enum-size', default=50, help='do not create an enum if more than max distinct members')
@click.option('--enum-threshold', default=0.1, help='if the number of distinct values / rows is less than this, do not make an enum')
@click.option('--omit-null/--no-omit-null', default=False, help="if true, ignore null values")
def json2model(input, format, omit_null, **kwargs):
    """ Infer a model from JSON instance data


    """
    ie = JsonDataGeneralizer(omit_null=omit_null)
    schema = ie.convert(input, dir=dir, format=format, **kwargs)
    write_schema(schema)

@click.command()
@click.argument('inputs', nargs=-1)
@click.option('--container-class-name', help="name of root class")
@click.option('--enum-columns', '-E', multiple=True, help='column(s) that is forced to be an enum')
@click.option('--enum-mask-columns', multiple=True, help='column(s) that are excluded from being enums')
@click.option('--max-enum-size', default=50, help='do not create an enum if more than max distinct members')
@click.option('--enum-threshold', default=0.1, help='if the number of distinct values / rows is less than this, do not make an enum')
@click.option('--omit-null/--no-omit-null', default=False, help="if true, ignore null values")
def frontmatter2model(inputs, format, omit_null, **kwargs):
    """ Infer a model from frontmatter files


    """
    ie = JsonDataGeneralizer(omit_null=omit_null)
    objs = parse_frontmatter_files(list(inputs))
    schema = ie.convert({'objects': objs}, dir=dir, format=format, **kwargs)
    write_schema(schema)

if __name__ == '__main__':
    json2model()


