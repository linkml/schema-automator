import click
import logging
import yaml
from typing import Union, Dict, Tuple, List, Any
from collections import defaultdict
import os
from csv import DictWriter

from rdflib import Graph, URIRef
from rdflib.query import ResultRow
from rdflib.namespace import RDF, RDFS
from SPARQLWrapper import SPARQLWrapper, N3, SPARQLWrapper2, RDFXML, TURTLE
from funowl.converters.functional_converter import to_python
from funowl import *
import funowl


from dataclasses import dataclass
from linkml_model_enrichment.importers.import_engine import ImportEngine


@dataclass
class OwlImportEngine(ImportEngine):
    mappings: dict = None
    include_unmapped_annotations = False

    def convert(self, file: str, name: str = None, **kwargs):
        self.mappings = {}
        doc = to_python(file)
        ontology = doc.ontology
        prefixes = doc.prefixDeclarations
        self.prefixes = prefixes
        if name is None:
            name = self.iri_to_name(ontology.iri)
        classes = {}
        slots = {}
        enums = {}
        types = {}
        schema = {
            'id': f'{ontology.iri}',
            'name': name,
            'description': name,
            'imports': ['linkml:types'],
            'prefixes': {
                'linkml': 'https://w3id.org/linkml/',
                name: f'https://w3id.org/{name}/'
            },
            'default_prefix': name,
            'types': types,
            'classes': classes,
            'slots': slots,
            'enums': enums
        }
        self.schema = schema
        isamap = defaultdict(set)
        slot_isamap = defaultdict(set)
        for a in ontology.axioms:
            if isinstance(a, SubClassOf):
                if isinstance(a.subClassExpression, Class):
                    child = self.iri_to_name(a.subClassExpression)
                    if isinstance(a.superClassExpression, Class):
                        parent = self.iri_to_name(a.superClassExpression)
                        isamap[child].add(parent)
                    else:
                        logging.error(f"cannot handle anon parent classes for {a}")
                else:
                    logging.error(f"cannot handle anon child classes for {a}")
            # https://github.com/hsolbrig/funowl/issues/19
            if isinstance(a, SubObjectPropertyOf):
                sub = a.subObjectPropertyExpression.v
                if isinstance(sub, ObjectPropertyExpression) and isinstance(sub.v, ObjectProperty):
                    child = self.iri_to_name(sub.v)
                    sup = a.superObjectPropertyExpression.v
                    if isinstance(sup, ObjectPropertyExpression) and isinstance(sup.v, ObjectProperty):
                        parent = self.iri_to_name(sup.v)
                        slot_isamap[child].add(parent)
                    else:
                        logging.error(f"cannot handle anon parent properties for {a}")
                else:
                    logging.error(f"cannot handle anon child properties for {a}")
            if isinstance(a, SubDataPropertyOf):
                sub = a.subDataPropertyExpression.v
                if isinstance(sub, DataPropertyExpression) and isinstance(sub.v, DataProperty):
                    child = self.iri_to_name(sub.v)
                    sup = a.superODataPropertyExpression.v
                    if isinstance(sup, DataPropertyExpression) and isinstance(sup.v, DataProperty):
                        parent = self.iri_to_name(sup.v)
                        slot_isamap[child].add(parent)
                    else:
                        logging.error(f"cannot handle anon parent properties for {a}")
                else:
                    logging(f"cannot handle anon child properties for {a}")
            if isinstance(a, SubAnnotationPropertyOf):
                child = self.iri_to_name(a.sub)
                parent = self.iri_to_name(a.super)
                slot_isamap[child].add(parent)

            # domains become slot declarations
            if isinstance(a, ObjectPropertyDomain) or isinstance(a, DataPropertyDomain):
                if isinstance(a, ObjectPropertyDomain):
                    p = a.objectPropertyExpression.v
                else:
                    p = a.dataPropertyExpression.v
                sn = self.iri_to_name(p)
                dc = a.classExpression
                if isinstance(dc, Class):
                    c = self.iri_to_name(dc)
                    self.class_info(c, 'slots', sn, True)
                    #logging.error(f'Inferred {c} from domain of {p}')
                if isinstance(dc, ObjectUnionOf):
                    for x in dc.classExpressions:
                        if isinstance(x, Class):
                            c = self.iri_to_name(x)
                            self.class_info(c, 'slots', sn, True)

            if isinstance(a, ObjectPropertyRange):
                p = a.objectPropertyExpression.v
                sn = self.iri_to_name(p)
                rc = a.classExpression
                if isinstance(rc, Class):
                    self.slot_info(sn, 'range', self.iri_to_name(rc))

            if isinstance(a, DataPropertyRange):
                p = a.dataPropertyExpression.v
                sn = self.iri_to_name(p)
                rc = a.dataRange
                if isinstance(rc, Datatype):
                    logging.error('TODO')
                    #self.slot_info(sn, 'range', self.iri_to_name(rc))

            if isinstance(a, AnnotationPropertyRange):
                self.slot_info(self.iri_to_name(a.property),
                               'range', self.iri_to_name(a.range))


            if isinstance(a, Declaration):
                e = a.v
                if type(e) == Class:
                    cn = self.iri_to_name(e.v)
                    self.class_info(cn, 'class_uri', str(e.v))
                if type(e) in [ObjectProperty, DataProperty, AnnotationProperty]:
                    cn = self.iri_to_name(e.v)
                    self.slot_info(cn, 'slot_uri', str(e.v))


        for c, parents in isamap.items():
            parents = list(parents)
            p = parents.pop()
            self.class_info(c, 'is_a', p)
            for p in parents:
                self.class_info(c, 'mixins', p, True)
        for c, parents in slot_isamap.items():
            parents = list(parents)
            p = parents.pop()
            self.slot_info(c, 'is_a', p)
            for p in parents:
                self.slot_info(c, 'mixins', p, True)

        for a in ontology.axioms:
            if isinstance(a, AnnotationAssertion):
                p = a.property
                strp = str(p)
                sub = a.subject.v
                val = a.value.v
                if isinstance(sub, IRI) and isinstance(val, Literal):
                    sub = self.iri_to_name(sub)
                    val = str(val.v)
                    if sub in classes:
                        t = 'classes'
                    elif sub in slots:
                        t = 'slots'
                    else:
                        logging.error(f'{sub} is not known')
                    if t is not None:
                        if strp == 'rdfs:comment':
                            self.element_info(t, sub, 'comments', val, multivalued=True)
                        elif strp == ':definition':
                            self.element_info(t, sub, 'description', val, multivalued=False)
                        else:
                            if self.include_unmapped_annotations:
                                self.element_info(t, sub, 'comments', f'{p} = {val}', multivalued=True)
        return schema

    def class_info(self, *args, **kwargs):
        self.element_info('classes', *args, **kwargs)

    def slot_info(self, *args, **kwargs):
        self.element_info('slots', *args, **kwargs)

    def element_info(self, type: str, cn: str, sn: str, v: Any, multivalued = False):
        if cn not in self.schema[type]:
            self.schema[type][cn] = {}
        c = self.schema[type][cn]
        if multivalued:
            if sn not in c:
                c[sn] = []
            c[sn].append(v)
        else:
            if sn in c and v != c[sn]:
                logging.error(f'Overwriting {sn} for {c} to {v}')
            c[sn] = v

    def iri_to_name(self, v):
        n = self._as_name(v)
        if n != v:
            self.mappings[n] = v
        return n

    def _as_name(self, v):
        v = str(v)
        for sep in ['#', '/', ':']:
            if sep in v:
                return v.split(sep)[-1]
        return v



@click.command()
@click.argument('owlfile')
@click.option('--name', '-n', help="Schema name")
@click.option('--output', '-o', help="Path to saved yaml schema")
def owl2model(owlfile, output, **args):
    """
    Infer a model from OWL Ontology

    Note: input must be in functional syntax
    """
    sie = OwlImportEngine()
    schema_dict = sie.convert(owlfile, **args)
    ys = yaml.dump(schema_dict, default_flow_style=False, sort_keys=False)
    if output:
        with open(output, 'w') as stream:
            stream.write(ys)
    else:
        print(ys)

if __name__ == '__main__':
    rdf2model()


