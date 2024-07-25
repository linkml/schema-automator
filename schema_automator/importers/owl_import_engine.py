import click
import logging
import yaml
from typing import Union, Dict, Tuple, List, Any
from collections import defaultdict

from linkml_runtime.linkml_model import SchemaDefinition
from funowl.converters.functional_converter import to_python
from funowl import *

from dataclasses import dataclass
from schema_automator.importers.import_engine import ImportEngine
from schema_automator.utils.schemautils import write_schema


@dataclass
class OwlImportEngine(ImportEngine):
    """
    An ImportEngine that takes schema-style OWL and converts it to a LinkML schema
    """
    mappings: dict = None
    include_unmapped_annotations = False

    def convert(self, file: str, name: str = None, model_uri: str = None, identifier: str = None, **kwargs) -> \
            SchemaDefinition:
        """
        Converts an OWL schema-style ontology

        :param file:
        :param name:
        :param model_uri:
        :param identifier:
        :param kwargs:
        :return:
        """
        self.mappings = {}
        doc = to_python(file)
        ontology = doc.ontology
        if len(ontology.axioms) == 0:
            raise Exception(f'Empty ontology in {file} (note: ontologies must be in functional syntax)')
        prefixes = doc.prefixDeclarations
        self.prefixes = prefixes
        if model_uri is None:
            model_uri = f'https://w3id.org/{name}/'
        if name is None:
            name = self.iri_to_name(ontology.iri)
        classes = {}
        slots = {}
        enums = {}
        types = {}
        schema_dict = {
            'id': f'{ontology.iri}',
            'name': name,
            'description': name,
            'imports': ['linkml:types'],
            'prefixes': {
                'linkml': 'https://w3id.org/linkml/',
                name: model_uri,
            },
            'default_prefix': name,
            'types': types,
            'classes': classes,
            'slots': slots,
            'enums': enums
        }
        self.schema = schema_dict
        isamap = defaultdict(set)
        slot_isamap = defaultdict(set)
        slot_usage_map = defaultdict(dict)
        single_valued_slots = set()
        for a in ontology.axioms:
            logging.debug(f'Axiom: {a}')
            if isinstance(a, SubClassOf):
                if isinstance(a.subClassExpression, Class):
                    def set_slot_usage(p, k, v):
                        if p not in slot_usage_map[child]:
                            slot_usage_map[child][p] = {}
                        slot_usage_map[child][p][k] = v
                    def set_cardinality(p, min_card, max_card):
                        if max_card is not None:
                            if max_card == 1:
                                set_slot_usage(p, 'multivalued', False)
                            elif max_card > 1:
                                set_slot_usage(p, 'multivalued', True)
                        if min_card is not None:
                            if min_card == 1:
                                set_slot_usage(p, 'required', True)
                            elif min_card == 0:
                                set_slot_usage(p, 'required', False)
                            else:
                                set_slot_usage(p, 'multivalued', True)
                    child = self.iri_to_name(a.subClassExpression)
                    if isinstance(a.superClassExpression, Class):
                        parent = self.iri_to_name(a.superClassExpression)
                        isamap[child].add(parent)
                    elif isinstance(a.superClassExpression, DataExactCardinality):
                        x = a.superClassExpression
                        card = x.card
                        p = self.iri_to_name(x.dataPropertyExpression)
                        set_cardinality(p, card, card)
                    elif isinstance(a.superClassExpression, ObjectExactCardinality):
                        x = a.superClassExpression
                        card = x.card
                        p = self.iri_to_name(x.objectPropertyExpression)
                        set_cardinality(p, card, card)
                    elif isinstance(a.superClassExpression, ObjectMinCardinality):
                        x = a.superClassExpression
                        p = self.iri_to_name(x.objectPropertyExpression)
                        set_cardinality(p, x.min_, None)
                    elif isinstance(a.superClassExpression, DataMinCardinality):
                        x = a.superClassExpression
                        p = self.iri_to_name(x.dataPropertyExpression)
                        set_cardinality(p, x.min_, None)
                    elif isinstance(a.superClassExpression, ObjectMaxCardinality):
                        x = a.superClassExpression
                        p = self.iri_to_name(x.objectPropertyExpression)
                        set_cardinality(p, None, x.max_)
                    elif isinstance(a.superClassExpression, DataMaxCardinality):
                        x = a.superClassExpression
                        p = self.iri_to_name(x.dataPropertyExpression)
                        set_cardinality(p, None, x.max_)
                    elif isinstance(a.superClassExpression, ObjectAllValuesFrom):
                        x = a.superClassExpression
                        p = self.iri_to_name(x.objectPropertyExpression)
                        if isinstance(x.classExpression, Class):
                            set_slot_usage(p, 'range', self.iri_to_name(x.classExpression))
                        else:
                            logging.error(f'Cannot yet handle anonymous ranges: {x.classExpression}')
                    elif isinstance(a.superClassExpression, ObjectSomeValuesFrom):
                        x = a.superClassExpression
                        p = self.iri_to_name(x.objectPropertyExpression)
                        set_cardinality(p, 1, None)
                    elif isinstance(a.superClassExpression, DataSomeValuesFrom):
                        x = a.superClassExpression
                        if len(x.dataPropertyExpressions) == 1:
                            p = self.iri_to_name(x.dataPropertyExpressions[0])
                            set_cardinality(p, 1, None)
                        else:
                            logging.error(f'Cannot handle multiple data property expressions: {x}')
                    elif isinstance(a.superClassExpression, DataAllValuesFrom):
                        x = a.superClassExpression
                        if len(x.dataPropertyExpressions) == 1:
                            p = self.iri_to_name(x.dataPropertyExpressions[0])
                            r = x.dataRange
                            if isinstance(r, DataOneOf):
                                logging.error(f'TODO: enum for {r}')
                            elif isinstance(r, Datatype):
                                set_slot_usage(p, 'range', r)
                            else:
                                logging.error(f'Cannot handle range of {r}')
                        else:
                            logging.error(f'Cannot handle multiple data property expressions: {x}')
                    elif isinstance(a.superClassExpression, DataHasValue):
                        x = a.superClassExpression
                        p = self.iri_to_name(x.dataPropertyExpression)
                        #if p not in slot_usage_map[child]:
                        #    slot_usage_map[child][p] = {}
                        lit = x.literal.v
                        if isinstance(lit, TypedLiteral):
                            lit = lit.literal
                        set_slot_usage(p, 'equals_string', str(lit))
                        #slot_usage_map[child][p]['equals_string'] = str(lit)
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
                        logging.error(f"cannot handle anon object parent properties for {a}")
                else:
                    logging.error(f"cannot handle anon object child properties for {a}")
            if isinstance(a, SubDataPropertyOf):
                sub = a.subDataPropertyExpression.v
                if isinstance(sub, DataProperty):
                    child = self.iri_to_name(sub)
                    sup = a.superDataPropertyExpression.v
                    if isinstance(sup, DataProperty):
                        parent = self.iri_to_name(sup)
                        slot_isamap[child].add(parent)
                    else:
                        logging.error(f"cannot handle anon data parent properties for {a}")
                else:
                    logging(f"cannot handle anon data child properties for {a}")
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
                uri_as_curie = str(e.v)
                if uri_as_curie.startswith(':'):
                    uri_as_curie = f'{name}{uri_as_curie}'
                if type(e) == Class:
                    cn = self.iri_to_name(e.v)
                    self.class_info(cn, 'class_uri', uri_as_curie)
                if type(e) in [ObjectProperty, DataProperty, AnnotationProperty]:
                    cn = self.iri_to_name(e.v)
                    self.slot_info(cn, 'slot_uri', uri_as_curie)


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
                if isinstance(sub, IRI):
                    sub = self.iri_to_name(sub)
                    if isinstance(val, AnonymousIndividual):
                        logging.info(f'Ignoring anonymous individuals: {sub} {strp} {val}')
                        continue
                    elif isinstance(val, Literal):
                        val = str(val.v)
                    elif isinstance(val, IRI):
                        val = val.v
                    else:
                        val = str(val)
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
                        elif strp == 'schema:rangeIncludes':
                            range_cn = self.iri_to_name(val)
                            logging.error(f'UNTESTED RANGE: schema.org {sub} {val} // {domain_cn}')
                            self.add_range(sub, range_cn)
                        elif strp == 'schema:domainIncludes':
                            domain_cn = self.iri_to_name(val)
                            logging.error(f'UNTESTED: schema.org {sub} {val} // {domain_cn}')
                            if domain_cn not in self.schema['classes']:
                                self.schema['classes'][domain_cn] = {}
                            if 'slots' not in self.schema['classes'][domain_cn]:
                                self.schema['classes'][domain_cn]['slots'] = []
                            self.schema['classes'][domain_cn]['slots'].append(sub)
                        else:
                            if self.include_unmapped_annotations:
                                self.element_info(t, sub, 'comments', f'{p} = {val}', multivalued=True)
        for cn, usage in slot_usage_map.items():
            schema_dict['classes'][cn]['slot_usage'] = usage
        for sn, s in schema_dict['slots'].items():
            if 'multivalued' not in s:
                s['multivalued'] = sn not in single_valued_slots
            if 'range' in s:
                if isinstance(s['range'], list):
                    rg = s['range']
                    if len(rg) == 0:
                        del s['range']
                    elif len(rg) == 1:
                        s['range'] = rg[0]
                    else:
                        del s['range']
                        s['any_of'] = [
                            {'range': x} for x in rg
                        ]
        if identifier is not None:
            slots[identifier] = {'identifier': True, 'range': 'uriorcurie'}
            for c in classes.values():
                if not c.get('is_a', None) and not c.get('mixins', []):
                    if 'slots' not in c:
                        c['slots'] = []
                    c['slots'].append(identifier)
        schema = SchemaDefinition(**schema_dict)
        return schema

    def class_info(self, *args, **kwargs):
        self.element_info('classes', *args, **kwargs)

    def slot_info(self, *args, **kwargs):
        self.element_info('slots', *args, **kwargs)

    def add_range(self, sn, range_cn):
        if sn not in self.schema['slots']:
            self.schema['slots'][sn] = {}
        if 'range' not in self.schema['slots'][sn]:
            self.schema['slots'][sn]['range'] = []
        self.schema['slots'][sn]['range'].append(range_cn)


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
@click.option('--identifier', '-I', help="Slot to use as identifier")
@click.option('--model-uri', help="Model URI prefix")
@click.option('--output', '-o', help="Path to saved yaml schema")
def owl2model(owlfile, output, **args):
    """
    Infer a model from OWL Ontology

    Note: input must be in functional syntax
    """
    sie = OwlImportEngine()
    schema = sie.convert(owlfile, **args)
    write_schema(schema, output)


if __name__ == '__main__':
    owl2model()


