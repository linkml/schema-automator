import click
import logging
import yaml
from typing import Union, Dict, Tuple, List, Any, Optional
from collections import defaultdict
import os
import re
import csv
import copy
import requests

from csv import DictWriter
from dateutil.parser import parse
from quantulum3 import parser as q_parser
from quantulum3.classes import Quantity



from rdflib import Graph, URIRef
from rdflib.query import ResultRow
from rdflib.namespace import RDF, RDFS
from SPARQLWrapper import SPARQLWrapper, N3, SPARQLWrapper2, RDFXML, TURTLE
from funowl.converters.functional_converter import to_python
from funowl import *


from dataclasses import dataclass, field
from linkml_model_enrichment.importers.import_engine import ImportEngine

@dataclass
class CsvDataImportEngine(ImportEngine):

    sep = "\t"
    schema_name: str = 'example'
    robot: bool = False
    enum_columns: List[str] = field(default_factory=lambda: [])
    enum_mask_columns: List[str] = field(default_factory=lambda: [])
    enum_threshold = 0.1
    enum_strlen_threshold = 30
    max_enum_size = 50

    def convert_multiple(self, files: List[str], **kwargs) -> Dict:
        yamlobjs = []
        for file in files:
            c = os.path.splitext(os.path.basename(file))[0]
            s = self.convert(file, class_name=c, **kwargs)
            if s is not None:
                yamlobjs.append(s)
        return merge_schemas(yamlobjs)

    def convert(self, file: str, **kwargs)-> Dict:
        with open(file, newline='') as tsvfile:
            rr = csv.DictReader(tsvfile, delimiter=self.sep)
            return self.convert_dicts([r for r in rr], **kwargs)

    def convert_dicts(self, rr: List[Dict], name: str = 'example', class_name: str = 'example', **kwargs) -> Optional[Dict]:
        slots = {}
        slot_values = {}
        n = 0
        enums = {}
        robot_defs = {}
        slot_usage = {}
        types = {}
        enum_columns = self.enum_columns
        enum_mask_columns = self.enum_mask_columns
        if len(rr) == 0:
            return None
        for row in rr:
            n += 1
            if n == 1 and self.robot:
                for k,v in row.items():
                    robot_defs[k] = v
                continue
            for k,v in row.items():
                if v is None:
                    v = ""
                if isinstance(v, list):
                    vs = v
                else:
                    vs = v.split('|')
                if k not in slots:
                    slots[k] = {'range': None}
                    slot_values[k] = set()
                if v is not None and v != "":
                    slots[k]['examples'] = [{'value': v}]
                    slot_values[k].update(vs)
                if len(vs) > 1:
                    slots[k]['multivalued'] = True
        types = {}
        new_slots = {}
        for sn, s in slots.items():
            vals = slot_values[sn]
            s['range'] = infer_range(s, vals, types)
            if (s['range'] == 'string' or sn in enum_columns) and sn not in enum_mask_columns:
                n_distinct = len(vals)
                longest = max([len(str(v)) for v in vals]) if n_distinct > 0 else 0
                if sn in enum_columns or \
                        ((n_distinct / n) < self.enum_threshold and n_distinct > 0 and
                         n_distinct <= self.max_enum_size and longest < self.enum_strlen_threshold):
                    enum_name = sn.replace(' ', '_').replace('(s)', '')
                    enum_name = f'{enum_name}_enum'
                    s['range'] = enum_name
                    enums[enum_name] = {
                        'permissible_values': {v:{'description': v} for v in vals}
                    }
            # ROBOT template hints. See http://robot.obolibrary.org/template
            if k in robot_defs:
                rd = robot_defs[sn]
                if 'SPLIT' in rd:
                    rd = re.sub(' SPLIT.*', '', rd)
                if rd.startswith("EC"):
                    rd = rd.replace('EC ', '')
                    rel = capture_robot_some(rd)
                    ss = rd.replace('%', '{' + k + '}')
                    slot_usage['equivalence axiom'] = {'string_serialization': ss}
                    if rel is not None:
                        s['is_a'] = rel
                        new_slots[rel] = {}
                elif rd.startswith("SC"):
                    rd = rd.replace('SC ', '')
                    rel = capture_robot_some(rd)
                    ss = rd.replace('%', '{' + k + '}')
                    slot_usage['subclass axiom'] = {'string_serialization': ss}
                    if rel is not None:
                        s['is_a'] = rel
                        new_slots[rel] = {}
                elif rd.startswith("C"):
                    rd = rd.replace('C ', '')
                    if rd == '%':
                        s['broad_mappings'] = ['rdfs:subClassOf']
                    rel = capture_robot_some(rd)
                    if rel is not None:
                        s['is_a'] = rel
                        new_slots[rel] = {}
                elif rd.startswith("I"):
                    rd = rd.replace('I ', '')
                    # TODO
                elif rd == 'TYPE':
                    s['slot_uri'] = 'rdf:type'
                elif rd == 'ID':
                    s['identifier'] = True
                elif rd == 'LABEL':
                    s['slot_uri'] = 'rdfs:label'
                elif rd.startswith("A "):
                    s['slot_uri'] = rd.replace('A ', '')
                elif rd.startswith("AT "):
                    s['slot_uri'] = re.sub('^^.*', '', rd.replace('AT ', ''))
                elif rd.startswith(">A "):
                    logging.warning('Axiom annotations not supported')
                slot_uri = s.get('slot_uri', None)
                if slot_uri is not None:
                    if ' ' in slot_uri or ':' not in slot_uri:
                        del s['slot_uri']
                        logging.warning(f'ROBOT "A" annotations not supported yet')
        class_slots = list(slots.keys())
        for sn,s in new_slots.items():
            if sn not in slots:
                slots[sn] = s
        schema = {
            'id': f'https://w3id.org/{name}',
            'name': name,
            'description': name,
            'imports': ['linkml:types'],
            'prefixes': {
                'linkml': 'https://w3id.org/linkml/',
                name: f'https://w3id.org/{name}'
            },
            'default_prefix': name,
            'types': types,
            'classes': {
                class_name: {
                    'slots': class_slots,
                    'slot_usage': slot_usage
                }
            },
            'slots': slots,
            'enums': enums,
            'types': types
        }
        add_missing_to_schema(schema)
        return schema

def capture_robot_some(s: str) -> str:
    """
    parses an OWL some values from from a robot template
    :param s:
    :return:
    """
    results = re.findall('(\S+) some %',s)
    if len(results) == 0:
        return None
    else:
        r = results[0]
        if ':' in r:
            # only use named properties
            return None
        else:
            return r

def isfloat(value):
    try:
        float(value)
        return True
    except ValueError:
        return False

def is_measurement(value):
    ms = q_parser.parse(value)
    for m in ms:
        if m.unit.name != 'dimensionless':
            return True

def is_all_measurement(values):
    """
    heuristic to guess if all values are measurements

    uses quantulum to parse

    A significant proportion must be dimensional, to avoid
    accidentally classifying a list of floats as measurements
    """
    n_dimensional = 0
    n = 0
    for value in values:
        ms = q_parser.parse(value)
        if len(ms) == 0:
            return False
        n += 1
        if all(m.unit.name != 'dimensionless' for m in ms):
            n_dimensional += 1
    # TODO: make this configurable
    if n_dimensional > n/2:
        return True
    else:
        return False


def infer_range(slot: dict, vals: set, types: dict) -> str:
    nn_vals = [v for v in vals if v is not None and v != ""]
    if len(nn_vals) == 0:
        return 'string'
    if all(v.isdigit() for v in nn_vals):
        return 'integer'
    if all(is_date(v) for v in nn_vals):
        return 'datetime'
    if all(isfloat(v) for v in nn_vals):
        return 'float'
    if is_all_measurement(nn_vals):
        return 'measurement'
    v0 = nn_vals[0]
    db = get_db(v0)
    if db is not None:
        if all(get_db(v) == db for v in nn_vals):
            t = f'{db} identifier'
            types[t] = {'typeof': 'string'}
            return t
        if all(get_db(v) is not None for v in nn_vals):
            t = 'identifier'
            types[t] = {'typeof': 'string'}
            return t
    return 'string'

def get_db(id: str) -> str:
    parts = id.split(':')
    if len(parts) > 1:
        return parts[0]
    else:
        return None

def is_date(string, fuzzy=False):
    """
    Return whether the string can be interpreted as a date.

    :param string: str, string to check for date
    :param fuzzy: bool, ignore unknown tokens in string if True
    """
    try:
        parse(string, fuzzy=fuzzy)
        return True
    except Exception:
        # https://stackoverflow.com/questions/4990718/how-can-i-write-a-try-except-block-that-catches-all-exceptions
        # we don't know all the different parse exceptions, we assume any error means this is a date
        return False

@dataclass
class Hit():
    term_id: str
    name: str
    score: float

def get_pv_element(v: str, zooma_confidence: str, cache: dict = {}) -> Hit:
    """
    uses ZOOMA to guess a meaning of an enum permissible value

    :param v:
    :param zooma_confidence:
    :param cache:
    :return:
    """
    if v in cache:
        return cache[v][0]
    if zooma_confidence is None:
        return None

    def confidence_to_int(c: str) -> int:
        if c == 'HIGH':
            return 5
        elif c == 'GOOD':
            return 4
        elif c == 'MEDIUM':
            return 2
        elif c == 'LOW':
            return 1
        else:
            raise Exception(f'Unknown: {c}')
    confidence_threshold = confidence_to_int(zooma_confidence)

    ontscores = {
        'NCBITaxon': 1.0,
        'OMIT': -1.0,

    }

    # zooma doesn't seem to do much pre-processing, so we convert
    label = v
    if 'SARS-CoV' not in label:
        label = re.sub("([a-z])([A-Z])","\g<1> \g<2>",label) # expand CamelCase
    label = label.replace('.', ' ').replace('_', ' ')
    params = {'propertyValue': label}
    time.sleep(1) # don't overload service
    logging.info(f'Q: {params}')
    r = requests.get('http://www.ebi.ac.uk/spot/zooma/v2/api/services/annotate',params=params)
    hits = [] # List[hit]
    for hit in r.json():
        confidence = float(confidence_to_int(hit['confidence']))
        id = hit['semanticTags'][0]
        if confidence >= confidence_threshold:
            hit = Hit(term_id= id,
                      name= hit['annotatedProperty']['propertyValue'],
                      score= confidence)
            hits.append(hit)
        else:
            logging.warning(f'Skipping {id} {confidence}')
    hits = sorted(hits, key=lambda h: h.score, reverse=True)
    logging.error(f'Hits for {label} = {hits}')
    if len(hits) > 0:
        cache[label] = hits
        return hits[0]
    else:
        return None





def convert_range(k: str, dt: str) -> str:
    t = 'string'
    if dt == 'float64':
        t = 'float'
    return t

def infer_enum_meanings(schema: dict,
                        zooma_confidence: str = 'MEDIUM',
                        cache={}) -> None:
    for _,e in schema['enums'].items():
        pvs = e['permissible_values']
        for k, pv in pvs.items():
            if pv == None:
                pv = {}
                pvs[k] = pv
            if 'meaning' not in pv or pv['meaning'] is not None:
                hit = get_pv_element(k, zooma_confidence=zooma_confidence, cache=cache)
                if hit is not None:
                    pv['meaning'] = hit.term_id
                    if 'description' not in pv:
                        pv['description'] = hit.name




def add_missing_to_schema(schema: dict):
    for slot in schema['slots'].values():
        if slot.get('range', None) == 'measurement':
            types = schema['types']
            if 'measurement' not in types:
                types['measurement'] = \
                    {'typeof': 'string',
                     'description': 'Holds a measurement serialized as a string'}

@click.group()
def main():
    pass

@main.command()
@click.argument('tsvfile') ## input TSV (must have column headers
@click.option('--output', '-o', help='Output file')
@click.option('--class_name', '-c', default='example', help='Core class name in schema')
@click.option('--schema_name', '-n', default='example', help='Schema name')
@click.option('--sep', '-s', default='\t', help='separator')
@click.option('--enum-columns', '-E', multiple=True, help='column that is forced to be an enum')
@click.option('--robot/--no-robot', default=False, help='set if the TSV is a ROBOT template')
def tsv2model(tsvfile, output, class_name, schema_name, **kwargs):
    """ Infer a model from a TSV """
    ie = CsvDataImportEngine(**kwargs)
    schema_dict = ie.convert(tsvfile, class_name=class_name, schema_name=schema_name)
    ys = yaml.dump(schema_dict, default_flow_style=False, sort_keys=False)
    if output:
        with open(output, 'w') as stream:
            stream.write(ys)
    else:
        print(ys)

@main.command()
@click.argument('tsvfiles', nargs=-1) ## input TSV (must have column headers
@click.option('--output', '-o', help='Output file')
@click.option('--schema_name', '-n', default='example', help='Schema name')
@click.option('--sep', '-s', default='\t', help='separator')
@click.option('--enum-columns', '-E', multiple=True, help='column(s) that is forced to be an enum')
@click.option('--enum-mask-columns', multiple=True, help='column(s) that are excluded from being enums')
@click.option('--max-enum-size', default=50, help='do not create an enum if more than max distinct members')
@click.option('--enum-threshold', default=0.1, help='if the number of distinct values / rows is less than this, do not make an enum')
@click.option('--robot/--no-robot', default=False, help='set if the TSV is a ROBOT template')
def tsvs2model(tsvfiles, output, schema_name, **kwargs):
    """ Infer a model from multiple TSVs """
    ie = CsvDataImportEngine(**kwargs)
    schema_dict = ie.convert_multiple(tsvfiles, schema_name=schema_name)
    ys = yaml.dump(schema_dict, default_flow_style=False, sort_keys=False)
    if output:
        with open(output, 'w') as stream:
            stream.write(ys)
    else:
        print(ys)


@main.command()
@click.argument('yamlfile')
@click.option('--zooma-confidence', '-Z', help='zooma confidence')
@click.option('--results', '-r', help='mapping results file')
def enrich(yamlfile, results, **args):
    """ Infer a model from a TSV """
    yamlobj = yaml.load(open(yamlfile))
    cache = {}
    infer_enum_meanings(yamlobj, cache=cache)
    if results is not None:
        with open(results, "w") as io:
            #io.write(str(cache))
            io.write(yaml.dump(cache))
    print(yaml.dump(yamlobj, default_flow_style=False, sort_keys=False))

if __name__ == '__main__':
    main()
