# Auto generated from jsonschema.yaml by pythongen.py version: 0.9.0
# Generation date: 2021-08-27 16:13
# Schema: jsonschema
#
# id: https://w3id.org/linkml/jsonschema
# description: A jsonschemamodel for defining linked open data schemas
# license: https://creativecommons.org/publicdomain/zero/1.0/

import dataclasses
import sys
import re
from jsonasobj2 import JsonObj, as_dict
from typing import Optional, List, Union, Dict, ClassVar, Any
from dataclasses import dataclass
from linkml_runtime.linkml_model.meta import EnumDefinition, PermissibleValue, PvFormulaOptions

from linkml_runtime.utils.slot import Slot
from linkml_runtime.utils.metamodelcore import empty_list, empty_dict, bnode
from linkml_runtime.utils.yamlutils import YAMLRoot, extended_str, extended_float, extended_int
from linkml_runtime.utils.dataclass_extensions_376 import dataclasses_init_fn_with_kwargs
from linkml_runtime.utils.formatutils import camelcase, underscore, sfx
from linkml_runtime.utils.enumerations import EnumDefinitionImpl
from rdflib import Namespace, URIRef
from linkml_runtime.utils.curienamespace import CurieNamespace
from linkml_runtime.linkml_model.types import String

metamodel_version = "1.7.0"

# Overwrite dataclasses _init_fn to add **kwargs in __init__
dataclasses._init_fn = dataclasses_init_fn_with_kwargs

# Namespaces
OIO = CurieNamespace('OIO', 'http://www.geneontology.org/formats/oboInOwl#')
BIBO = CurieNamespace('bibo', 'http://purl.org/ontology/bibo/')
DCTERMS = CurieNamespace('dcterms', 'http://purl.org/dc/terms/')
LINKML = CurieNamespace('linkml', 'https://w3id.org/linkml/')
OSLC = CurieNamespace('oslc', 'http://open-services.net/ns/core#')
OWL = CurieNamespace('owl', 'http://www.w3.org/2002/07/owl#')
PAV = CurieNamespace('pav', 'http://purl.org/pav/')
RDF = CurieNamespace('rdf', 'http://www.w3.org/1999/02/22-rdf-syntax-ns#')
RDFS = CurieNamespace('rdfs', 'http://www.w3.org/2000/01/rdf-schema#')
SCHEMA = CurieNamespace('schema', 'http://schema.org/')
SKOS = CurieNamespace('skos', 'http://www.w3.org/2004/02/skos/core#')
XSD = CurieNamespace('xsd', 'http://www.w3.org/2001/XMLSchema#')
DEFAULT_ = LINKML


# Types
class Ref(str):
    type_class_uri = XSD.string
    type_class_curie = "xsd:string"
    type_name = "Ref"
    type_model_uri = LINKML.Ref


# Class references
class DefinitionName(extended_str):
    pass


@dataclass
class Schema(YAMLRoot):
    _inherited_slots: ClassVar[List[str]] = []

    class_class_uri: ClassVar[URIRef] = LINKML.Schema
    class_class_curie: ClassVar[str] = "linkml:Schema"
    class_name: ClassVar[str] = "Schema"
    class_model_uri: ClassVar[URIRef] = LINKML.Schema

    definitions: Optional[Union[Dict[Union[str, DefinitionName], Union[dict, "Definition"]], List[Union[dict, "Definition"]]]] = empty_dict()

    def __post_init__(self, *_: List[str], **kwargs: Dict[str, Any]):
        self._normalize_inlined_as_dict(slot_name="definitions", slot_type=Definition, key_name="name", keyed=True)

        super().__post_init__(**kwargs)


@dataclass
class Definition(YAMLRoot):
    _inherited_slots: ClassVar[List[str]] = []

    class_class_uri: ClassVar[URIRef] = LINKML.Definition
    class_class_curie: ClassVar[str] = "linkml:Definition"
    class_name: ClassVar[str] = "Definition"
    class_model_uri: ClassVar[URIRef] = LINKML.Definition

    name: Union[str, DefinitionName] = None
    title: Optional[str] = None
    type: Optional[str] = None
    properties: Optional[Union[Dict[Union[str, DefinitionName], Union[dict, "Definition"]], List[Union[dict, "Definition"]]]] = empty_dict()
    items: Optional[Union[Dict[Union[str, DefinitionName], Union[dict, "Definition"]], List[Union[dict, "Definition"]]]] = empty_dict()
    references: Optional[str] = None

    def __post_init__(self, *_: List[str], **kwargs: Dict[str, Any]):
        if self._is_empty(self.name):
            self.MissingRequiredField("name")
        if not isinstance(self.name, DefinitionName):
            self.name = DefinitionName(self.name)

        if self.title is not None and not isinstance(self.title, str):
            self.title = str(self.title)

        if self.type is not None and not isinstance(self.type, str):
            self.type = str(self.type)

        self._normalize_inlined_as_dict(slot_name="properties", slot_type=Definition, key_name="name", keyed=True)

        self._normalize_inlined_as_dict(slot_name="items", slot_type=Definition, key_name="name", keyed=True)

        if self.references is not None and not isinstance(self.references, str):
            self.references = str(self.references)

        super().__post_init__(**kwargs)


# Enumerations


# Slots
class slots:
    pass

slots.name = Slot(uri=LINKML.name, name="name", curie=LINKML.curie('name'),
                   model_uri=LINKML.name, domain=None, range=URIRef)

slots.definitions = Slot(uri=LINKML.definitions, name="definitions", curie=LINKML.curie('definitions'),
                   model_uri=LINKML.definitions, domain=None, range=Optional[Union[Dict[Union[str, DefinitionName], Union[dict, Definition]], List[Union[dict, Definition]]]])

slots.references = Slot(uri=LINKML.references, name="references", curie=LINKML.curie('references'),
                   model_uri=LINKML.references, domain=None, range=Optional[str])

slots.title = Slot(uri=LINKML.title, name="title", curie=LINKML.curie('title'),
                   model_uri=LINKML.title, domain=None, range=Optional[str])

slots.type = Slot(uri=LINKML.type, name="type", curie=LINKML.curie('type'),
                   model_uri=LINKML.type, domain=None, range=Optional[str])

slots.properties = Slot(uri=LINKML.properties, name="properties", curie=LINKML.curie('properties'),
                   model_uri=LINKML.properties, domain=None, range=Optional[Union[Dict[Union[str, DefinitionName], Union[dict, Definition]], List[Union[dict, Definition]]]])

slots.items = Slot(uri=LINKML.items, name="items", curie=LINKML.curie('items'),
                   model_uri=LINKML.items, domain=None, range=Optional[Union[Dict[Union[str, DefinitionName], Union[dict, Definition]], List[Union[dict, Definition]]]])
