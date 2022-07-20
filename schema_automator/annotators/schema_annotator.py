import urllib.request, urllib.error, urllib.parse

import click
import requests
import logging
import json
import yaml
import os
from dataclasses import dataclass
from pprint import pprint
from typing import Any, List, Dict, Union, Iterator

from linkml_runtime.linkml_model import SchemaDefinition
from linkml_runtime.utils.metamodelcore import Curie
from linkml_runtime.utils.schemaview import SchemaView, re
from oaklib import BasicOntologyInterface
from oaklib.datamodels.search import SearchConfiguration
from oaklib.datamodels.text_annotator import TextAnnotation
from oaklib.interfaces import SearchInterface
from oaklib.interfaces.text_annotator_interface import TextAnnotatorInterface

from schema_automator.utils.schemautils import minify_schema

camel_case_pattern = re.compile(r'(?<!^)(?=[A-Z])')

def uncamel(n: str):
    return camel_case_pattern.sub(' ', n).lower().replace('_', ' ')

@dataclass
class SchemaAnnotator:
    """
    An engine for enhancing schemas by performing lookup and annotation operations
    using an ontology service.

    A SchemaAnnotator wraps an OAK ontology interface.
    See `OAK documentation <https://incatools.github.io/ontology-access-kit/>`_ for more details
    """
    ontology_implementation: BasicOntologyInterface

    def annotate_text(self, text: str) -> Iterator[TextAnnotation]:
        # this is a wrapper over OAK annotation and search;
        # it (1) expands CamelCase (2) abstracts over annotation vs search
        # TODO: fold this functionality back into OAK
        oi = self.ontology_implementation
        text_exp = uncamel(text) # TODO: use main linkml_runtime method
        if isinstance(oi, TextAnnotatorInterface):
            # TextAnnotation is available; use this by default
            for r in oi.annotate_text(text_exp):
                yield r
            if text_exp != text.lower():
                for r in oi.annotate_text(text_exp):
                    yield r
        elif isinstance(oi, SearchInterface):
            # use search as an alternative
            cfg = SearchConfiguration(is_complete=True)
            for r in oi.basic_search(text, config=cfg):
                yield TextAnnotation(object_id=r, matches_whole_text=True)
            if text_exp != text.lower():
                for r in oi.basic_search(text_exp, config=cfg):
                    yield TextAnnotation(object_id=r, matches_whole_text=True)
        else:
            raise NotImplementedError

    def annotate_schema(self, schema: Union[SchemaDefinition, str], curie_only=True) -> SchemaDefinition:
        """
        Annotate all elements of a schema, adding mappings.

        This requires that the OntologyInterface implements either BasicOntologyInterface or SearchInterface
        """
        sv = SchemaView(schema)
        oi = self.ontology_implementation
        for elt_name, elt in sv.all_elements().items():
            for n in [elt.name] + elt.aliases:
                for r in self.annotate_text(n):
                    logging.debug(f'MATCH: {r}')
                    if r.matches_whole_text:
                        xref = r.object_id
                        if curie_only and not Curie.is_curie(xref):
                            continue
                        logging.info(f'Mapping from {elt_name} "{n}" to {xref}')
                        if xref not in elt.exact_mappings:
                            elt.exact_mappings.append(xref)
        for e in sv.all_enums().values():
            for pv in e.permissible_values.values():
                for r in self.annotate_text(pv.text):
                    logging.debug(f'MATCH: {r}')
                    if r.matches_whole_text:
                        xref = r.object_id
                        if curie_only and not Curie.is_curie(xref):
                            continue
                        logging.info(f'Mapping from {elt_name} "{n}" to {xref}')
                        if pv.meaning is None:
                            logging.info(f'Arbitrarily choosing first match: {xref}')
                            pv.meaning = xref
                        else:
                            if xref not in pv.exact_mappings:
                                pv.exact_mappings.append(xref)

        return sv.schema

    def enrich(self, schema: Union[SchemaDefinition, str]) -> SchemaDefinition:
        """
        Enrich a schema by performing lookups on the external ontology/vocabulary endpoint,
        and copying over metadata

        Currently the only metadata obtained is text definitions

        :param schema:
        :return:
        """
        sv = SchemaView(schema)
        oi = self.ontology_implementation
        for elt_name, elt in sv.all_elements().items():
            curies = [sv.get_uri(elt)]
            for rel, ms in sv.get_mappings().items():
                curies += ms
            for x in curies:
                if elt.description:
                    break
                try:
                    defn = oi.get_definition_by_curie(x)
                    if defn:
                        elt.description = defn
                except Exception:
                    pass
        return sv.schema


@click.command()
@click.argument('schema')
@click.option('--input', '-i', help="OAK input ontology selector")
@click.option('--output', '-o', help="Path to saved yaml schema")
def annotate_schema(schema: str, input: str, output: str, **args):
    """
    Annotate all elements of a schema
    """
    logging.basicConfig(level=logging.INFO)
    annr = SchemaAnnotator()
    schema = annr.annotate_schema(schema)
    sd = minify_schema(schema)
    if output:
        with open(output, 'w') as stream:
            yaml.safe_dump(sd, stream, sort_keys=False)
    else:
        print(yaml.safe_dump(sd, sort_keys=False))

if __name__ == '__main__':
    annotate_schema()