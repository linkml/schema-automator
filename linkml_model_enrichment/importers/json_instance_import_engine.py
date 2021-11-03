import click
import logging
from typing import Union, Dict, Tuple, List, Any
from collections import defaultdict
import os
from csv import DictWriter
import json
import yaml
import gzip

from dataclasses import dataclass
from linkml_model_enrichment.importers.import_engine import ImportEngine
from linkml_model_enrichment.importers.csv_import_engine import CsvDataImportEngine
from linkml_model_enrichment.utils.schemautils import merge_schemas
from linkml_runtime.utils.formatutils import camelcase

@dataclass
class JsonInstanceImportEngine(ImportEngine):
    mappings: dict = None
    omit_null: bool = None

    def convert(self, input: Union[str, Dict], format: str = 'json',
                container_class_name='Container',
                **kwargs):
        csv_engine = CsvDataImportEngine(**kwargs)

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
                else:
                    raise Exception(f'bad format {format}')
        rows_by_table = defaultdict(list)
        self.rows_by_table = rows_by_table
        self._convert_obj(obj, table=container_class_name)
        yamlobjs = []
        for cn, rows_dict in rows_by_table.items():
            schema_obj = csv_engine.convert_dicts(rows_dict, cn, cn)
            yamlobjs.append(schema_obj)
        yamlobj = merge_schemas(yamlobjs)
        yamlobj['classes'][container_class_name]['tree_root'] = True
        return yamlobj

    def _key_to_classname(self, k: str) -> str:
        return camelcase(k)

    def _convert_obj(self, obj, table='Container'):
        if isinstance(obj, dict):
            row = defaultdict(set)
            for k, v in obj.items():
                if v is None and self.omit_null:
                    continue
                row[k] = self._convert_obj(v, table=camelcase(k))
            self.rows_by_table[table].append(row)
            return f'$ref:{table}'
        elif isinstance(obj, list):
            new_list = [self._convert_obj(v, table=table) for v in obj]
            return new_list
        else:
            return obj




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
    ie = JsonInstanceImportEngine(omit_null=omit_null)
    schema_dict = ie.convert(input, dir=dir, format=format, **kwargs)
    ys = yaml.dump(schema_dict, default_flow_style=False, sort_keys=False)
    print(ys)

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
    print(f'INPUTS={inputs}')
    ie = JsonInstanceImportEngine(omit_null=omit_null)
    objs = parse_frontmatter_files(list(inputs))
    schema_dict = ie.convert({'objects': objs}, dir=dir, format=format, **kwargs)
    ys = yaml.dump(schema_dict, default_flow_style=False, sort_keys=False)
    print(ys)

if __name__ == '__main__':
    json2model()


