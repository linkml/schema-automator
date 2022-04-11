import urllib.request, urllib.error, urllib.parse

import click
import requests
import logging
import json
import yaml
import os
from dataclasses import dataclass
from pprint import pprint
from typing import Any, List, Dict, Union

from linkml_runtime.linkml_model import SchemaDefinition
from linkml_runtime.utils.schemaview import SchemaView

from linkml_model_enrichment.utils.schemautils import minify_schema

REST_URL = "http://data.bioontology.org"

ANNOTATION = Dict[str, Any]

@dataclass
class Term:
    id: str
    prefLabel: str
    synonyms: List[str] = None
    definition: str = None
    semanticType: str = None
    cui: str = None

@dataclass
class Annotation:
    start_position: int
    end_position: int
    matchType: str
    text: str
    source: str

    def complete(self) -> bool:
        return len(self.source) == (self.end_position - self.start_position) + 1

@dataclass
class Result:
    annotatedClass: Term
    annotations: List[Annotation] = None
    mappings: List = None

    def complete(self) -> bool:
        return any(a for a in self.annotations if a.complete())

@dataclass
class ResultSet:
    results: List[Result] = None

@dataclass
class SchemaAnnotator:
    bioportal_api_key: str = None

    def load_bioportal_api_key(self, path: str = None) -> None:
        if path is None:
            path = os.path.join('conf', 'bioportal_apikey.txt')
        with open(path) as stream:
            lines = stream.readlines()
            key = lines[0].strip()
            self.bioportal_api_key = key

    def get_json(self, url) -> Any:
        opener = urllib.request.build_opener()
        opener.addheaders = [('Authorization', 'apikey token=' + API_KEY)]
        return json.loads(opener.open(url).read())

    def annotate_text(self, text, include: List = None, require_exact_match=True) -> ResultSet:
        logging.info(f'Annotating text: {text}')
        if include is None:
            include =['prefLabel', 'synonym', 'definition', 'semanticType', 'cui']
        include_str = ','.join(include)
        params = {'include':  include_str,
                  'require_exact_match': require_exact_match,
                  'text': text}
        if self.bioportal_api_key is  None:
            self.load_bioportal_api_key()
        r = requests.get(REST_URL + '/annotator',
                         headers={'Authorization': 'apikey token=' + self.bioportal_api_key},
                         params=params)
        #return r.json()
        return self.json_to_results(r.json(), text)

    def json_to_results(self, json_list: List[Any], text: str) -> ResultSet:
        results = []
        for obj in json_list:
            #print(f'JSON: {obj}')
            ac_obj = obj['annotatedClass']
            ac = Term(id=ac_obj['@id'], prefLabel=ac_obj.get('prefLabel', None))
            anns = [Annotation(start_position=x['from'],
                               end_position=x['to'],
                               matchType=x['matchType'],
                               text=x['text'],
                               source=text) for x in obj['annotations']]
            r = Result(annotatedClass=ac, annotations=anns)
            logging.debug(f'RESULT: {r}')
            results.append(r)
        return ResultSet(results)

    def annotate_schema(self, schema: Union[SchemaDefinition, str], match_only=True) -> SchemaDefinition:
        """
        Annotate all elements of a schema, adding mappings
        """
        sv = SchemaView(schema)
        for elt_name, elt in sv.all_elements().items():
            for n in [elt.name] + elt.aliases:
                rs = self.annotate_text(n, require_exact_match=True)
                for r in rs.results:
                     if r.complete():
                        xref = r.annotatedClass.id
                        logging.info(f'Mapping from {elt_name} "{n}" to {xref}')
                        if xref not in elt.exact_mappings:
                            elt.exact_mappings.append(xref)
        return sv.schema

@click.command()
@click.argument('schema')
@click.option('--output', '-o', help="Path to saved yaml schema")
def annotate_schema(schema: str, output: str, **args):
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