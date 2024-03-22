import logging
from typing import Dict, List, Any
from collections import defaultdict

from linkml.utils.schema_builder import SchemaBuilder
from linkml_runtime import SchemaView
from linkml_runtime.linkml_model import (
    SchemaDefinition,
    SlotDefinition,
    ClassDefinition,
)
from funowl.converters.functional_converter import to_python
from funowl import *

from dataclasses import dataclass, field

from linkml_runtime.utils.formatutils import underscore
from linkml_runtime.utils.introspection import package_schemaview
from rdflib import Graph, RDF, OWL, URIRef, RDFS, SKOS, SDO, Namespace
from schema_automator.importers.import_engine import ImportEngine
from schema_automator.utils.schemautils import write_schema


HTTP_SDO = Namespace("http://schema.org/")

DEFAULT_METAMODEL_MAPPINGS = {
    "is_a": [RDFS.subClassOf, SKOS.broader],
    "domain_of": [HTTP_SDO.domainIncludes, SDO.domainIncludes],
    "rangeIncludes": [HTTP_SDO.rangeIncludes, SDO.rangeIncludes],
    "exact_mappings": [OWL.sameAs, HTTP_SDO.sameAs],
    ClassDefinition.__name__: [RDFS.Class, OWL.Class, SKOS.Concept],
    SlotDefinition.__name__: [
        RDF.Property,
        OWL.ObjectProperty,
        OWL.DatatypeProperty,
        OWL.AnnotationProperty,
    ],
}


@dataclass
class RdfsImportEngine(ImportEngine):
    """
    An ImportEngine that takes RDFS and converts it to a LinkML schema
    """

    mappings: dict = None
    initial_metamodel_mappings: Dict[str, List[URIRef]] = None
    metamodel_mappings: Dict[str, List[URIRef]] = None
    reverse_metamodel_mappings: Dict[URIRef, List[str]] = None
    include_unmapped_annotations = False
    metamodel = None
    metamodel_schemaview: SchemaView = None
    classdef_slots: List[str] = None

    def __post_init__(self):
        sv = package_schemaview("linkml_runtime.linkml_model.meta")
        self.metamodel_schemaview = sv
        self.metamodel = sv
        self.metamodel_mappings = defaultdict(list)
        self.reverse_metamodel_mappings = defaultdict(list)
        for k, vs in DEFAULT_METAMODEL_MAPPINGS.items():
            self.metamodel_mappings[k].extend(vs)
            for v in vs:
                self.reverse_metamodel_mappings[v].append(k)
        if self.initial_metamodel_mappings:
            for k, vs in self.initial_metamodel_mappings.items():
                if not isinstance(vs, list):
                    vs = [vs]
                self.metamodel_mappings[k].extend(vs)
                for v in vs:
                    self.reverse_metamodel_mappings[URIRef(v)].append(k)
                    logging.info(f"Adding mapping {k} -> {v}")
        for e in sv.all_elements().values():
            mappings = []
            for ms in sv.get_mappings(e.name, expand=True).values():
                for m in ms:
                    uri = URIRef(m)
                    mappings.append(uri)
                    self.reverse_metamodel_mappings[uri].append(e.name)
            self.metamodel_mappings[e.name] = mappings
        self.defclass_slots = [s.name for s in sv.class_induced_slots(ClassDefinition.class_name)]

    def convert(
        self,
        file: str,
        name: str = None,
        format="turtle",
        default_prefix: str = None,
        model_uri: str = None,
        identifier: str = None,
        **kwargs,
    ) -> SchemaDefinition:
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
        g = Graph()
        g.parse(file, format=format)
        if name is not None and default_prefix is None:
            default_prefix = name
        if name is None:
            name = default_prefix
        if name is None:
            name = "example"
        sb = SchemaBuilder(name=name)
        sb.add_defaults()
        schema = sb.schema
        for k, v in g.namespaces():
            if k == "schema" and v != "http://schema.org/":
                continue
            sb.add_prefix(k, v, replace_if_present=True)
        if default_prefix is not None:
            schema.default_prefix = default_prefix
            if default_prefix not in schema.prefixes:
                sb.add_prefix(default_prefix, model_uri, replace_if_present=True)
            schema.id = schema.prefixes[default_prefix].prefix_reference
        cls_slots = defaultdict(list)
        props = []
        for rdfs_property_metaclass in self._rdfs_metamodel_iri(
            SlotDefinition.__name__
        ):
            for p in g.subjects(RDF.type, rdfs_property_metaclass):
                props.append(p)
        # implicit properties
        for metap in (
            self.reverse_metamodel_mappings["domain_of"]
            + self.reverse_metamodel_mappings["rangeIncludes"]
        ):
            for p, _, _o in g.triples((None, metap, None)):
                props.append(p)
        for p in set(props):
            sn = self.iri_to_name(p)
            init_dict = self._dict_for_subject(g, p)
            if "domain_of" in init_dict:
                for x in init_dict["domain_of"]:
                    cls_slots[x].append(sn)
                del init_dict["domain_of"]
            if "rangeIncludes" in init_dict:
                init_dict["any_of"] = [{"range": x} for x in init_dict["rangeIncludes"]]
                del init_dict["rangeIncludes"]
            slot = SlotDefinition(sn, **init_dict)
            slot.slot_uri = str(p.n3(g.namespace_manager))
            sb.add_slot(slot)
        rdfs_classes = []
        for rdfs_class_metaclass in self._rdfs_metamodel_iri(ClassDefinition.__name__):
            for s in g.subjects(RDF.type, rdfs_class_metaclass):
                rdfs_classes.append(s)
        # implicit classes
        for metap in [RDFS.subClassOf]:
            for s, _, o in g.triples((None, metap, None)):
                rdfs_classes.append(s)
                rdfs_classes.append(o)
        for s in set(rdfs_classes):
            cn = self.iri_to_name(s)
            init_dict = self._dict_for_subject(g, s)
            c = ClassDefinition(cn, **init_dict)
            c.slots = cls_slots.get(cn, [])
            c.class_uri = str(s.n3(g.namespace_manager))
            sb.add_class(c)
        if identifier is not None:
            id_slot = SlotDefinition(identifier, identifier=True, range="uriorcurie")
            schema.slots[identifier] = id_slot
            for c in schema.classes.values():
                if not c.is_a and not c.mixins:
                    if identifier not in c.slots:
                        c.slots.append(identifier)
        return schema

    def _dict_for_subject(self, g: Graph, s: URIRef) -> Dict[str, Any]:
        """
        Looks up triples for a subject and converts to dict using linkml keys.

        :param g:
        :param p:
        :return:
        """
        init_dict = {}
        for pp, obj in g.predicate_objects(s):
            if pp == RDF.type:
                continue
            metaslot_name = self._element_from_iri(pp)
            logging.debug(f"Mapping {pp} -> {metaslot_name}")
            if metaslot_name not in self.defclass_slots:
                continue
            if metaslot_name is None:
                logging.warning(f"Not mapping {pp}")
                continue
            if metaslot_name == "name":
                metaslot_name = "title"
            metaslot = self.metamodel.get_slot(metaslot_name)
            v = self._object_to_value(obj, metaslot=metaslot)
            metaslot_name_safe = underscore(metaslot_name)
            if not metaslot or metaslot.multivalued:
                if metaslot_name_safe not in init_dict:
                    init_dict[metaslot_name_safe] = []
                init_dict[metaslot_name_safe].append(v)
            else:
                init_dict[metaslot_name_safe] = v
        return init_dict

    def _rdfs_metamodel_iri(self, name: str) -> List[URIRef]:
        return self.metamodel_mappings.get(name, [])

    def _element_from_iri(self, iri: URIRef) -> str:
        r = self.reverse_metamodel_mappings.get(iri, [])
        if len(r) > 0:
            if len(r) > 1:
                logging.debug(f"Multiple mappings for {iri}: {r}")
            return r[0]

    def _object_to_value(self, obj: Any, metaslot: SlotDefinition = None) -> Any:
        if isinstance(obj, URIRef):
            if metaslot.range == "uriorcurie" or metaslot.range == "uri":
                return str(obj)
            return self.iri_to_name(obj)
        if isinstance(obj, Literal):
            return obj.value
        return obj

    def iri_to_name(self, v: URIRef) -> str:
        n = self._as_name(v)
        if n != v:
            self.mappings[n] = v
        return n

    def _as_name(self, v: URIRef):
        v = str(v)
        for sep in ["#", "/", ":"]:
            if sep in v:
                return v.split(sep)[-1]
        return v
