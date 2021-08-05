import copy
import logging

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