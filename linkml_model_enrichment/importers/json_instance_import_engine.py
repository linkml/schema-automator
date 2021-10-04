import click
import logging
from typing import Union, Dict, Tuple, List
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

    def convert(self, input: str, format: str = 'json',
                container_class_name='Container',
                **kwargs):
        csv_engine = CsvDataImportEngine()

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

@click.command()
@click.argument('input')
@click.option('--format', '-f', default='json', help="json or yaml")
@click.option('--dir', '-d', required=True)
def json2model(input, format, dir, **args):
    """ Infer a model from RDF instance data """
    ie = JsonInstanceImportEngine()
    if not os.path.exists(dir):
        os.makedirs(dir)
    schema_dict = ie.convert(input, dir=dir, format=format)
    ys = yaml.dump(schema_dict, default_flow_style=False, sort_keys=False)
    print(ys)

if __name__ == '__main__':
    json2model()


