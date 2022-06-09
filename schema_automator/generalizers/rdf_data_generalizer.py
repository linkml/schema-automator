import click
from collections import defaultdict
import os
from csv import DictWriter
from linkml_runtime import SchemaView
from linkml_runtime.linkml_model import SchemaDefinition

from rdflib import Graph, URIRef
from rdflib.namespace import RDF

from dataclasses import dataclass

from schema_automator.generalizers.generalizer import Generalizer
from schema_automator.generalizers.csv_data_generalizer import CsvDataGeneralizer
from schema_automator.utils.schemautils import write_schema


@dataclass
class RdfDataGeneralizer(Generalizer):
    mappings: dict = None

    def convert(self, file: str, dir: str, **kwargs) -> SchemaDefinition:
        csv_engine = CsvDataGeneralizer()

        g = Graph()
        g.parse(file, **kwargs)
        self.mappings = {}
        paths = self.graph_to_tables(g, dir)
        schemas = []
        for c, tsvfile in paths.items():
            schemas.append(csv_engine.convert(tsvfile, class_name=c))
        sv = SchemaView(schemas[0])
        for s in schemas[1:]:
            sv.merge_schema(s)
        schema = sv.schema
        mappings = self.mappings
        for cn, c in schema.classes.items():
            if cn in mappings:
                c.class_uri = mappings[cn]
        for sn, s in schema.slots.items():
            if sn in mappings:
                s.slot_uri = mappings[sn]
        for en, e in schema.enums.items():
            for pvn, pvo in e.permissible_values.items():
                if pvn in mappings:
                    pvo.meaning = mappings[pvn]
        return schema

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
    sie = RdfDataGeneralizer()
    if not os.path.exists(dir):
        os.makedirs(dir)
    schema = sie.convert(rdffile, dir=dir, format='ttl')
    write_schema(schema)

if __name__ == '__main__':
    rdf2model()


