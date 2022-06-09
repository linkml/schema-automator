#!/usr/bin/env python
"""Infer a schema from a rdftab

"""
from linkml.utils.schemaloader import load_raw_schema
from typing import Union, List, Set, Optional
from linkml.generators.yamlgen import YAMLGenerator

import logging
import click
import yaml
import csv
import time

from linkml_runtime.linkml_model.meta import SchemaDefinition
from linkml.utils.generator import Generator, shared_arguments
from dateutil.parser import parse

CURIE = str

RANGE_COMPOSITION_TABLE = {
    ('xsd:integer', 'xsd:float'): 'number',
    ('owl:Thing', 'owl:Class'): 'owl:Thing',
    ('owl:ObjectProperty', 'owl:TransitiveProperty'): 'owl:ObjectProperty',
    ('owl:ObjectProperty', 'owl:SymmetrucProperty'): 'owl:ObjectProperty'
}

OMIT_PRED_IN = ['rdf', 'swrl']
OMIT_CLASS_IN = ['rdf', 'swrl', 'UO']

def remove_prefix(id: str) -> str:
    """
    get the local part of a CURIE or URI
    """
    if 'http' in id:
        if id.startswith('<'):
            id = id.replace('<', '').replace('>', '')
        if '#' in id:
            parts = id.split('#')
        elif '/'  in id:
            parts = id.split('.')
        else:
            logging.error(f'ID: {id}')
            parts = [id]
    else:
        parts = id.split(':')
        if len(parts) > 2:
            logging.warning(f'ID has > 2 parts: {id}')
    local_id = parts[-1]
    if '#' in local_id:
        parts = local_id.split('#')
        local_id = parts[-1]
    if '/' in local_id:
        parts = local_id.split('/')
        local_id = parts[-1]
    return local_id


def is_literal(x: CURIE) -> bool:
    """
    True if the URI is an xsd type
    """
    return x.startswith('xsd:')

def is_thing_or_individual(x: CURIE) -> bool:
    """
    True if the URI is owl Thing or NamedIndividual
    """
    return x == 'owl:Thing' or x == 'owl:NamedIndividual'

def condense_range_pair(r1: CURIE, r2: CURIE) -> Optional[CURIE]:
    """
    Infer a parent range from a pair of ranges

    TODO: use the ontology to do this
    """
    if r1 == r2:
        return r1
    if (r1,r2) in RANGE_COMPOSITION_TABLE:
        return RANGE_COMPOSITION_TABLE[(r1,r2)]
    elif (r2,r1) in RANGE_COMPOSITION_TABLE:
        return RANGE_COMPOSITION_TABLE[(r2,r1)]
    else:
        if is_literal(r1) != is_literal(r2):
            logging.warning(f'Trying to combine literal and non-literal: {r1} {r2}')
        if is_thing_or_individual(r1):
            return r2
        elif is_thing_or_individual(r2):
            return r1
        else:
            logging.warning(f'Logic not implemented to condense: {r1} {r2}')
            return None

def condense_ranges(cset: Set[CURIE], classes: dict) -> Optional[str]:
    """
    Condense a set of ranges into one range that subsumes them all

    TODO: use the ontology to do this
    """
    todo = list(cset)
    r = todo.pop()
    while len(todo) > 0:
        r2 = todo.pop()
        r = condense_range_pair(r, r2)
        if r is None:
            return None
    return remove_prefix(r)

def new_cls(u: CURIE) -> dict:
    """
    Create stub linkml ClassDefinition dict
    """
    return {'class_uri': u, 'slots': [], 'slot_usage': {}}

def remove_angle_brackets(id: str) -> str:
    if id.startswith('<'):
        id = id.replace('<', '').replace('>', '')
    if id.startswith('obo:http'):
        id = id.replace('obo:', '')
    return id

def set_range(slot: dict, r: str, classes: dict) -> None:
    if r in classes:
        slot['range'] = r
    else:
        if 'range' in slot:
            del slot['range']
        logging.warning(f'Omitting range: {r} as there is no class definitions')

def infer_model_from_predicate_summary(tsvfile: str, sep="\t",
                                       schema_name: str = 'example',
                                       count_threshold: int=2,
                                       include_counts = True,
                                       base_uri: str = None,
                                       schema_description: str = 'TODO',
                                       enum_columns: List[str]=[],
                                       enum_threshold=0.1,
                                       max_enum_size=50) -> dict:
    """
    Given a predicate summary table, infer a linkml schema
    """
    with open(tsvfile, newline='') as tsvfile:
        rr = csv.DictReader(tsvfile, delimiter=sep)
        slots = {}
        slot_values = {}
        n = 0
        enums = {}
        slot_usage = {}
        classes = {}
        slot_ranges = {}
        for row in rr:
            pred = remove_angle_brackets(row['predicate'])
            domain = row['subject_type']
            range = row['object_type']
            num = int(row['num_statements'])
            predname = row['predicate_label']
            is_multivalued = int(row['is_multivalued']) != 0
            if num < count_threshold:
                continue
            # TODO: make configurable
            if pred == 'IAO:0000111':
                # https://github.com/EnvironmentOntology/envo/issues/1187
                predname = 'editor_preferred_term'
            # TODO: make configurable
            if pred.startswith('oio:http'):
                pred = pred.replace('oio:http', 'http')
            dc = remove_prefix(domain)
            rc = remove_prefix(range)
            if predname is None or predname == '':
                sn = remove_prefix(pred)
            else:
                sn = predname
            if sn is None or sn == '':
                raise Exception(f'Null p for {row}')
            if sn.isnumeric():
                logging.warning(f'Ignoring: {pred}, no name {predname}')
                continue
            sn = sn.replace(' ', '_')
            #p = p.lower()
            if dc not in classes:
                classes[dc] = new_cls(domain)
            c = classes[dc]
            if rc not in classes:
                classes[rc] = new_cls(range)
            if sn not in slots:
                slots[sn] = {'slot_uri': pred, 'multivalued': is_multivalued}
                slot_ranges[sn] = set()
            generic_slot = slots[sn]
            if generic_slot['slot_uri'] != pred:
                if 'exact_mappings' not in generic_slot:
                    generic_slot['exact_mappings'] = []
                if pred not in generic_slot['exact_mappings']:
                    generic_slot['exact_mappings'].append(pred)
                logging.warning(f'Collapsing {pred} and {generic_slot["slot_uri"]} into {sn}')
            slot_ranges[sn].add(range)
            if sn not in c['slots']:
                c['slots'].append(sn)
                c['slot_usage'][sn] = {'range': set(), 'count': 0}
            c['slot_usage'][sn]['range'].add(range)
            c['slot_usage'][sn]['count'] += num
        # filter useless classes
        classes = {cn:c for cn,c in classes.items() if len(c['slots']) > 0}
        for sn, ranges in slot_ranges.items():
            r = condense_ranges(ranges, classes)
            if r is not None:
                logging.error(f'Set range for slot {sn} to {r}')
                set_range(slots[sn], r, classes)
            else:
                slots[sn]['todos'] = ['define range']
        for cn, c in classes.items():
            redundant = []
            for sn, class_slot in c['slot_usage'].items():
                r = condense_ranges(class_slot['range'], classes)
                if r is None:
                    del class_slot['range']
                    class_slot['todos'] = ['define range']
                else:
                    logging.error(f'Setting range for slot {cn}.{sn} in {class_slot} to {r}')
                    set_range(class_slot, r, classes)
                    logging.error(f'Set range for slot {cn}.{sn} in {class_slot} to {r}')
                n = class_slot['count']
                del class_slot['count']
                # check for redundancy
                is_redundant = True
                if sn in slots:
                    generic_slot = slots[sn]
                    for k, v in class_slot.items():
                        if k in generic_slot:
                            if generic_slot[k] != v:
                                logging.error(f'OVERIDE {sn} in {cn} slot property: {k} :: {v} >> {generic_slot[k]}')
                                is_redundant = False
                        else:
                            logging.error(f'NONRED {sn} in {cn} slot property: {k} not in {generic_slot}')
                            is_redundant = False
                else:
                    raise Exception(f'No slot: {sn}')
                if include_counts:
                    class_slot['comments'] = [f'Usages: {n}']
                if is_redundant:
                    redundant.append(sn)
                    logging.error(f'deleting redundant usage for {cn}.{sn}')
                else:
                    logging.error(f'keeping nonredundant usage for {cn}.{sn}')
            for sn in redundant:
                del c['slot_usage'][sn]
    # TODO: infer if required; infer multivalued
    if base_uri is None:
        base_uri = f'https://w3id.org/{schema_name}'
    schema = {
        'id': base_uri,
        'name': schema_name,
        'description': schema_description,
        'imports': ['linkml:types'],
        'prefixes': {
            'linkml': 'https://w3id.org/linkml/',
            schema_name: f'{base_uri}/'
        },
        'default_prefix': schema_name,
        'types': {},
        'classes': classes,
        'slots': slots,
        'enums': enums
    }
    return schema

@click.group()
def main():
    pass

@main.command()
@click.argument('tsvfile') ## input TSV (must have column headers
@click.option('--schema_name', '-n', default='example', help='Schema name')
@click.option('--sep', '-s', default='\t', help='separator')
@click.option('--base-uri', '-b', help='base URI')
@click.option('--schema-description', '-D', help='schema description')
@click.option('--enum-columns', '-E', multiple=True, help='column that is forced to be an enum')
@click.option('--include-counts/--no-include-counts', default=True, help='set to include counts in slot_usage')
def preds2model(tsvfile, **args):
    """
    Infer a model from a predicate summary TSV

    Pre-processing:

    sqlite3 db/foo.db -cmd '.headers on' -cmd '.separator "\t"' "select * from predicate_summary_labeled"

    """
    s = infer_model_from_predicate_summary(tsvfile, **args)
    ys = yaml.dump(s, default_flow_style=False, sort_keys=False)
    schema = load_raw_schema(ys)
    G = YAMLGenerator(schema)
    print(G.serialize())

if __name__ == '__main__':
    main()
