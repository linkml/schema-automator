import click
import logging
from typing import Union, Dict, Tuple, List
from collections import defaultdict
import os
from csv import DictWriter

from rdflib import Graph, URIRef
from rdflib.query import ResultRow
from rdflib.namespace import RDF, RDFS
from SPARQLWrapper import SPARQLWrapper, N3, SPARQLWrapper2, RDFXML, TURTLE

from dataclasses import dataclass
from linkml_model_enrichment.importers.import_engine import ImportEngine
from linkml_model_enrichment.importers.csv_import_engine import CsvDataImportEngine
from linkml_model_enrichment.utils.schemautils import merge_schemas

@dataclass
class RdfInstanceImportEngine(ImportEngine):
    mappings: dict = None

    def convert(self, file: str, dir: str, **kwargs):
        csv_engine = CsvDataImportEngine()

        g = Graph()
        g.parse(file, **kwargs)
        self.mappings = {}
        paths = self.graph_to_tables(g, dir)
        yamlobjs = []
        for c, tsvfile in paths.items():
            yamlobjs.append(csv_engine.convert(tsvfile, class_name=c))
        yamlobj = merge_schemas(yamlobjs)
        mappings = self.mappings
        for cn, c in yamlobj['classes'].items():
            if cn in mappings:
                c['class_uri'] = mappings[cn]
        for sn, s in yamlobj['slots'].items():
            if sn in mappings:
                s['slot_uri'] = mappings[sn]
        for en, e in yamlobj['enums'].items():
            if 'permissible_values' in e:
                for pvn, pvo in e['permissible_values'].items():
                    if pvn in mappings:
                        pvo['meaning'] = mappings[pvn]
        return yamlobj

    def graph_to_tables(self, g: Graph, dir: str):
        mappings = self.mappings
        rows_by_table = defaultdict(list)
        for s,_,t_uriref in g.triples((None, RDF.type, None)):
            t = self._as_name(t_uriref)
            mappings[t] = str(t_uriref)
            #print(f'I={s} type={t}')
            row = defaultdict(set)
            row['id'] = {s}
            for _,p_uriref,o_uriref in g.triples((s, None, None)):
                p = self._as_name(p_uriref)
                o = self._as_name(o_uriref)
                mappings[p] = str(p_uriref)
                if isinstance(o_uriref, URIRef):
                    mappings[o] = str(o_uriref)
                row[p].add(o)
            rows_by_table[t].append(row)
            #print(f'  ROW={row}')
        paths = {}
        for t, rows in rows_by_table.items():
            path = f'{os.path.join(dir, t)}.tsv'
            paths[t] = path
            fields = []
            for row in rows:
                for k in row.keys():
                    if k not in fields:
                        fields.append(k)
                    v = list(row[k])
                    v = '|'.join(v)
                    row[k] = v
            print(f'Writing {len(rows)} to {path}')
            with open(path, 'w') as stream:
                w = DictWriter(stream, delimiter='\t', fieldnames=fields)
                w.writeheader()
                for row in rows:
                    w.writerow(row)
        return paths

    def _as_name(self, v):
        v = str(v)
        for sep in ['#', '/']:
            if sep in v:
                return v.split(sep)[-1]
        return v

@click.command()
@click.argument('rdffile')
@click.option('--dir', '-d', required=True)
def rdf2model(rdffile, dir, **args):
    """ Infer a model from RDF instance data """
    sie = RdfInstanceImportEngine()
    if not os.path.exists(dir):
        os.makedirs(dir)
    schema_dict = sie.convert(rdffile, dir=dir, format='ttl')
    ys = yaml.dump(schema_dict, default_flow_style=False, sort_keys=False)
    print(ys)

if __name__ == '__main__':
    rdf2model()


