import copy
import logging
from typing import Union

import yaml
from linkml_runtime.dumpers import yaml_dumper
from linkml_runtime.linkml_model import SchemaDefinition


def minify_schema(obj: Union[dict, SchemaDefinition]) -> dict:
    # TODO prefixes
    if isinstance(obj, SchemaDefinition):
        yd = yaml_dumper.dumps(obj)
        obj = yaml.safe_load(yd)
    if isinstance(obj, dict):
        for k, v in obj.items():
            if isinstance(v, dict) and 'name' in v and v['name'] == k:
                del v['name']
            minify_schema(v)
    elif isinstance(obj, list):
        for v in obj:
            minify_schema(v)
    else:
        None
    return obj



# TODO: replace with schemaview
def merge_schemas(schemas, nomerge_enums_for=[]):
    schema = copy.deepcopy(schemas[0])
    for s in schemas:
        for n,x in s['classes'].items():
            if n not in schema['classes']:
                schema['classes'][n] = x
        for n,x in s['slots'].items():
            if n not in schema['slots']:
                schema['slots'][n] = x
            else:
                cur_slot = schema['slots'][n]
                if 'range' in cur_slot and 'range' in x:
                    if cur_slot['range'] != x['range']:
                        logging.error(f'Inconsistent ranges: {cur_slot} vs {x}')
                        if cur_slot['range'] == 'string':
                            cur_slot['range'] = x['range']
                elif 'range' not in cur_slot:
                    cur_slot['range'] = x['range']
        for n,x in s['types'].items():
            if n not in schema['types']:
                schema['types'][n] = x
            else:
                None # TODO
        for n,x in s['enums'].items():
            if n not in schema['enums']:
                schema['enums'][n] = x
            else:
                None # TODO
    return schema