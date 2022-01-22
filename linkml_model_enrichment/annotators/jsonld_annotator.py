import json
import logging
from typing import Union, Dict, Optional

from linkml_runtime import SchemaView
from linkml_runtime.linkml_model import SchemaDefinition, Definition, Prefix, DefinitionName

JSON = Dict


def is_url(s: str) -> bool:
    if s is not None:
        return s.startswith('http')
    else:
        return False

class JsonLdAnnotator:
    """
    Annotates a schema using URIs derived from a JSON-LD file


    """

    def annotate(self, schema: Union[str, SchemaDefinition], jsonld_path: str):
        sv = SchemaView(schema)
        with open(jsonld_path) as f:
            jsonld = json.load(f)
        ctxt = jsonld['@context']
        for c in sv.all_classes().values():
            self.annotate_element(c, 'class_uri', ctxt)
        for s in sv.all_slots().values():
            self.annotate_element(s, 'slot_uri', ctxt)
        all_curies = []
        for c in sv.all_classes().values():
            if c.class_uri:
                all_curies.append(c.class_uri)
        for s in sv.all_slots().values():
            if s.slot_uri:
                all_curies.append(s.slot_uri)
        all_prefixes = set()
        for cu in all_curies:
            all_prefixes.add(cu.split(':')[0])
        print(f'ALL PREFIXES: {all_prefixes}')
        for k, v in ctxt.items():
            if k in all_prefixes:
                if k not in schema.prefixes:
                    url = None
                    if isinstance(v, str):
                        url = v
                    if is_url(url):
                        schema.prefixes[k] = Prefix(k, url)

    def annotate_element(self, el: Definition, mapping_slot: str, jsonld: JSON):
        if el.name in jsonld:
            curie = self.get_curie(el.name, jsonld)
            if curie:
                logging.info(f'ANNOTATING: {el.name} with {curie}')
                setattr(el, mapping_slot, curie)
            else:
                logging.error(f'Cannot annotate: {el.name}')


    def get_curie(self, name: DefinitionName, jsonld: JSON) -> Optional[str]:
        if name in jsonld:
            curie = jsonld[name]
            if isinstance(curie, str):
                if curie.startswith('@'):
                    return None
                else:
                    return curie
            elif isinstance(curie, dict):
                if '@id' in curie:
                    return curie['@id']


