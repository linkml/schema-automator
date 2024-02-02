import click
import logging
import yaml
from dataclasses import dataclass
from typing import List, Union, Iterator

from linkml_runtime.linkml_model import SchemaDefinition, Element, PermissibleValue, ClassDefinition, SlotDefinition
from linkml_runtime.utils.metamodelcore import Curie
from linkml_runtime.utils.schemaview import SchemaView, re, EnumDefinition
from oaklib import BasicOntologyInterface
from oaklib.datamodels.search import SearchConfiguration
from oaklib.datamodels.text_annotator import TextAnnotation
from oaklib.interfaces import SearchInterface
from oaklib.interfaces.text_annotator_interface import TextAnnotatorInterface

from schema_automator.utils.schemautils import minify_schema

camel_case_pattern = re.compile(r'(?<!^)(?=[A-Z])')

def uncamel(n: str):
    # TODO: replace with equiv from linkml-runtime
    return camel_case_pattern.sub(' ', n).lower().replace('_', ' ')


@dataclass
class SchemaAnnotator:
    """
    An engine for enhancing schemas by performing lookup and annotation operations
    using an ontology service.

    A SchemaAnnotator wraps an OAK ontology interface.
    See `OAK documentation <https://incatools.github.io/ontology-access-kit/>`_ for more details
    """
    ontology_implementation: BasicOntologyInterface = None
    mine_descriptions: bool = False
    allow_partial: bool = False
    curie_only: bool = True
    assign_element_uris: bool = False
    assign_enum_meanings: bool = False

    def annotate_element(self, elt: Union[PermissibleValue, Element]) -> None:
        """
        Annotates an element or a permissible value

        :param elt:
        :return:
        """
        if isinstance(elt, Element):
            texts = [elt.name]
        elif isinstance(elt, PermissibleValue):
            texts = [elt.text]
        else:
            raise ValueError(f"Unexpected type {type(elt)}")
        texts += elt.aliases
        if self.mine_descriptions and elt.description:
            texts.append(elt.description)
        for text in texts:
            logging.info(f"Annotating: {text}")
            for r in self.annotate_text(text):
                logging.debug(f'MATCH: {r}')
                if self.allow_partial or r.matches_whole_text:
                    xref = r.object_id
                    if self.curie_only and not Curie.is_curie(xref):
                        continue
                    logging.info(f'Mapping from "{text}" to {xref}')
                    if isinstance(elt, PermissibleValue):
                        if self.assign_enum_meanings:
                            if not elt.meaning:
                                elt.meaning = xref
                                continue
                    else:
                        if self.assign_element_uris:
                            if isinstance(elt, ClassDefinition):
                                if not elt.class_uri:
                                    elt.class_uri = xref
                                    continue
                            if isinstance(elt, SlotDefinition):
                                if not elt.slot_uri:
                                    elt.slot_uri = xref
                                    continue
                            if isinstance(elt, EnumDefinition):
                                if not elt.enum_uri:
                                    elt.enum_uri = xref
                                    continue
                    if xref not in elt.exact_mappings:
                        elt.exact_mappings.append(xref)

    def annotate_text(self, text: str) -> Iterator[TextAnnotation]:
        # this is a wrapper over OAK annotation and search;
        # it (1) expands CamelCase (2) abstracts over annotation vs search
        # TODO: fold this functionality back into OAK
        oi = self.ontology_implementation
        text_exp = uncamel(text)  # TODO: use main linkml_runtime method
        if isinstance(oi, TextAnnotatorInterface):
            logging.debug(f"Using TextAnnotatorInterface on {text_exp}")
            # TextAnnotation is available; use this by default
            for r in oi.annotate_text(text_exp):
                yield r
            if text_exp != text.lower():
                for r in oi.annotate_text(text_exp):
                    yield r
        elif isinstance(oi, SearchInterface):
            logging.debug(f"Using SearchInterface on {text_exp}")
            # use search as an alternative
            cfg = SearchConfiguration(is_complete=True)
            for r in oi.basic_search(text, config=cfg):
                yield TextAnnotation(object_id=r, matches_whole_text=True)
            if text_exp != text.lower():
                for r in oi.basic_search(text_exp, config=cfg):
                    yield TextAnnotation(object_id=r, matches_whole_text=True)
        else:
            raise NotImplementedError

    def annotate_schema(self, schema: Union[SchemaDefinition, str]) -> SchemaDefinition:
        """
        Annotate all elements of a schema, adding mappings.

        This requires that the OntologyInterface implements either BasicOntologyInterface or SearchInterface
        """
        sv = SchemaView(schema)
        oi = self.ontology_implementation
        for elt_name, elt in sv.all_elements().items():
            self.annotate_element(elt)
        for e in sv.all_enums().values():
            for pv in e.permissible_values.values():
                self.annotate_element(pv)
        return sv.schema

    def enrich(self, schema: Union[SchemaDefinition, str]) -> SchemaDefinition:
        """
        Enrich a schema by performing lookups on the external ontology/vocabulary endpoint,
        and copying over metadata

        Currently, the only metadata obtained is text definitions

        .. code-block:: python

        >>> from schema_automator.annotators.schema_annotator import SchemaAnnotator
        >>> from oaklib.selector import get_implementation_from_shorthand
        >>> oi = get_implementation_from_shorthand("sqlite:obo:so")
        >>> sa = SchemaAnnotator(ontology_implementation=oi)
        >>> schema = sa.enrich("tests/data/schema.yaml")

        :param schema:
        :return:
        """
        sv = SchemaView(schema)
        oi = self.ontology_implementation
        for elt_name, elt in sv.all_elements().items():
            logging.debug(f"Enriching {elt_name}")
            if isinstance(elt, EnumDefinition):
                curies = []
                for pv in elt.permissible_values.values():
                    if pv.meaning:
                        pv_curies = [pv.meaning]
                    else:
                        pv_curies = []
                    self._add_description_from_curies(pv, pv_curies)
            else:
                curies = [sv.get_uri(elt)]
            for rel, ms in sv.get_mappings(elt_name).items():
                curies += ms
            self._add_description_from_curies(elt, curies)
        return sv.schema

    def _add_description_from_curies(self, elt: Union[Element, PermissibleValue], curies: List[str]):
        oi = self.ontology_implementation
        logging.info(f"Looking up descriptions using {curies}")
        for x in curies:
            logging.info(f"Fetching description using: {curies}")
            if elt.description:
                break
            try:
                defn = oi.definition(x)
                if defn:
                    elt.description = defn
                else:
                    mm = oi.entity_metadata_map(x)
                    logging.debug(f"MM={mm}")
                    for p in ['rdfs:comment', 'skos:definition', 'dcterms:description']:
                        if p in mm:
                            elt.description = mm[p]
                            last
            except Exception:
                pass


@click.command()
@click.argument('schema')
@click.option('--input', '-i', help="OAK input ontology selector")
@click.option('--output', '-o', help="Path to saved yaml schema")
def annotate_schema(schema: str, input: str, output: str, **args):
    """
    Annotate all elements of a schema.

    DEPRECATED: use main schemauto CLI instead
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