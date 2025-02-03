import logging
from pathlib import Path
from typing import Dict, Iterable, List, Any, Mapping, TextIO
import typing
from collections import defaultdict, Counter

from jsonasobj2 import JsonObj
from linkml.utils.schema_builder import SchemaBuilder
from linkml_runtime import SchemaView
from linkml_runtime.linkml_model import (
    SchemaDefinition,
    SlotDefinition,
    ClassDefinition,
    Prefix,
)

from dataclasses import dataclass, field

from linkml_runtime.utils.formatutils import underscore
from linkml_runtime.utils.introspection import package_schemaview
from rdflib import Graph, RDF, OWL, URIRef, RDFS, SKOS, SDO, Namespace, Literal
from schema_automator.importers.import_engine import ImportEngine


HTTP_SDO = Namespace("http://schema.org/")

DEFAULT_METAMODEL_MAPPINGS: Dict[str, List[URIRef]] = {
    # See https://github.com/linkml/linkml/issues/2507
    "description": [RDFS.comment],
    "is_a": [RDFS.subClassOf, SKOS.broader],
    "domain_of": [HTTP_SDO.domainIncludes, SDO.domainIncludes, RDFS.domain],
    "range": [HTTP_SDO.rangeIncludes, SDO.rangeIncludes, RDFS.range],
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
    #: View over the LinkML metamodel
    metamodel: SchemaView = field(init=False)
    #: Mapping from field names in this RDF schema (e.g. `price`) to IRIs (e.g. `http://schema.org/price`)
    mappings: Dict[str, URIRef] = field(default_factory=dict)
    #: User-defined mapping from LinkML metamodel slots (such as `domain_of`) to RDFS IRIs (such as http://schema.org/domainIncludes)
    initial_metamodel_mappings: Dict[str, URIRef | List[URIRef]] = field(default_factory=dict)
    #: Combined mapping from LinkML metamodel slots to RDFS IRIs
    metamodel_mappings: Dict[str, List[URIRef]] = field(default_factory=lambda: defaultdict(list))
    #: Reverse of `metamodel_mappings`, but supports multiple terms mapping to the same IRI
    reverse_metamodel_mappings: Dict[URIRef, List[str]] = field(default_factory=lambda: defaultdict(list))
    #: The names of LinkML ClassDefinition slots
    classdef_slots: set[str] = field(init=False)
    #: The names of LinkML SlotDefinition slots
    slotdef_slots: set[str] = field(init=False)
    #: Every prefix seen in the graph
    seen_prefixes: set[str] = field(default_factory=set)
    #: The counts of each prefix, used to infer the default prefix
    prefix_counts: Counter[str] = field(default_factory=Counter)

    def __post_init__(self):
        sv = package_schemaview("linkml_runtime.linkml_model.meta")
        self.metamodel = sv

        # Populate the combined metamodel mappings
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

        # LinkML fields have some built-in mappings to other ontologies, such as https://w3id.org/linkml/Any -> AnyValue
        for e in sv.all_elements().values():
            mappings = []
            for ms in sv.get_mappings(e.name, expand=True).values():
                for m in ms:
                    uri = URIRef(m)
                    mappings.append(uri)
                    self.reverse_metamodel_mappings[uri].append(e.name)
            self.metamodel_mappings[e.name] = mappings
        self.classdef_slots = {s.name for s in sv.class_induced_slots(ClassDefinition.class_name)}
        self.slotdef_slots = {s.name for s in sv.class_induced_slots(SlotDefinition.class_name)}

    def convert(
        self,
        file: str | Path | TextIO,
        name: str | None = None,
        format: str | None="turtle",
        default_prefix: str | None = None,
        model_uri: str | None = None,
        identifier: str | None = None,
        **kwargs: Any,
    ) -> SchemaDefinition:
        """
        Converts an OWL schema-style ontology
        """
        g = Graph(bind_namespaces="none")
        g.parse(file, format=format)
        sb = SchemaBuilder()
        sb.add_defaults()
        schema = sb.schema
        for k, v in g.namespaces():
            if str(v) == "https://schema.org/":
                # Normalise schema.org to HTTP
                v = "http://schema.org/"
            if k == "schema" and str(v) != "http://schema.org/":
                continue
            sb.add_prefix(k, v, replace_if_present=True)
        if default_prefix is not None and isinstance(schema.prefixes, dict):
            schema.default_prefix = default_prefix
            if model_uri is not None and default_prefix not in schema.prefixes:
                sb.add_prefix(default_prefix, model_uri, replace_if_present=True)
            prefix = schema.prefixes[default_prefix]
            if isinstance(prefix, Prefix):
                schema.id = prefix.prefix_reference
        cls_slots = defaultdict(list)

        for slot in self.generate_rdfs_properties(g, cls_slots):
            sb.add_slot(slot)
        for cls in self.process_rdfs_classes(g, cls_slots):
            sb.add_class(cls)

        if identifier is not None and isinstance(schema.slots, dict) and isinstance(schema.classes, dict):
            id_slot = SlotDefinition(identifier, identifier=True, range="uriorcurie")
            schema.slots[identifier] = id_slot
            for c in schema.classes.values():
                if isinstance(c, ClassDefinition) and isinstance(c.slots, list):
                    if not c.is_a and not c.mixins:
                        if identifier not in c.slots:
                            c.slots.append(identifier)

        # Remove prefixes that aren't used
        if isinstance(schema.imports, list):
            for imp in schema.imports:
                prefix, _suffix = imp.split(":", 1)
                self.seen_prefixes.add(prefix)
        schema.prefixes = {key: value for key, value in schema.prefixes.items() if key in self.seen_prefixes}
        self.infer_metadata(schema, name, default_prefix, model_uri)
        self.fix_missing(schema)
        return schema

    def infer_metadata(self, schema: SchemaDefinition, name: str | None, default_prefix: str | None = None, model_uri: str | None = None):
        top_count = self.prefix_counts.most_common(1)
        if len(top_count) == 0:
            raise ValueError("No prefixes found in the graph")
        inferred_prefix = top_count[0][0]

        schema.name = name or inferred_prefix
        schema.default_prefix = default_prefix or inferred_prefix
        prefix_uri = None
        if isinstance(schema.prefixes, Mapping):
            prefix_uri = schema.prefixes.get(inferred_prefix)
        elif isinstance(schema.prefixes, JsonObj):
            prefix_uri = schema.prefixes._get(inferred_prefix)
        if isinstance(prefix_uri, Prefix):
            schema.id = model_uri or prefix_uri.prefix_reference

    def fix_missing(self, schema: SchemaDefinition) -> None:
        """
        For some properties we have a `subproperty_of` that references a slot that doesn't exist.
        This removes such links.
        For example with `schema:name`, we have a `subPropertyOf` that references `rdfs:label`, which is from
        the RDFS metamodel that we don't currently import.
        """
        if not isinstance(schema.slots, dict):
            raise ValueError("SchemaBuilder schema must have slots as a dict")
        slot_names: set[str] = set(schema.slots.keys())
        for slot in schema.slots.values():
            if not isinstance(slot, SlotDefinition):
                raise ValueError(f"Slot {slot} is not a SlotDefinition")
            if slot.subproperty_of is not None and slot.subproperty_of not in slot_names:
                logging.warning(f"Slot {slot.name} has subproperty_of {slot.subproperty_of}, but that slot is missing")
                slot.subproperty_of = None

    def track_uri(self, uri: str, g: Graph) -> None:
        """
        Updates the set of prefixes seen in the graph
        """
        prefix, _namespace, _name = g.namespace_manager.compute_qname(uri)
        self.seen_prefixes.add(prefix)
        self.prefix_counts.update([prefix])

    def process_rdfs_classes(
        self,
        g: Graph, 
        cls_slots: Dict[str, List[str]], 
    ) -> Iterable[ClassDefinition]:
        """
        Converts the RDFS classes in the graph to LinkML SlotDefinitions
        """
        rdfs_classes: List[URIRef] = []
        
        for rdfs_class_metaclass in self._rdfs_metamodel_iri(ClassDefinition.__name__):
            for s in g.subjects(RDF.type, rdfs_class_metaclass):
                if isinstance(s, URIRef):
                    rdfs_classes.append(s)
        
        # implicit classes
        for metap in [RDFS.subClassOf]:
            for s, _, o in g.triples((None, metap, None)):
                if isinstance(s, URIRef):
                    rdfs_classes.append(s)
                if isinstance(o, URIRef):
                    rdfs_classes.append(o)

        for s in set(rdfs_classes):
            self.track_uri(s, g)
            cn = self.iri_to_name(s)
            init_dict = self._dict_for_subject(g, s, "class")
            c = ClassDefinition(cn, **init_dict)
            c.slots = cls_slots.get(cn, [])
            c.class_uri = str(s.n3(g.namespace_manager))
            yield c

    def generate_rdfs_properties(
        self,
        g: Graph, 
        cls_slots: Dict[str, List[str]]
    ) -> Iterable[SlotDefinition]:
        """
        Converts the RDFS properties in the graph to LinkML SlotDefinitions
        """
        # All property IDs
        props: set[URIRef] = set()

        # Add explicit properties, ie those with a RDF.type mapping
        for rdfs_property_metaclass in self._rdfs_metamodel_iri(SlotDefinition.__name__):
            for p in g.subjects(RDF.type, rdfs_property_metaclass):
                if isinstance(p, URIRef):
                    props.add(p)

        # Add implicit properties, ie those that are the domain or range of a property
        for metap in (
            self.metamodel_mappings["domain_of"]
            + self.metamodel_mappings["rangeIncludes"]
        ):
            for p, _, _o in g.triples((None, metap, None)):
                if isinstance(p, URIRef):
                    props.add(p)

        for p in props:
            self.track_uri(p, g)
            sn = self.iri_to_name(p)
            #: kwargs for SlotDefinition
            init_dict = self._dict_for_subject(g, p, "slot")

            # Special case for domains and ranges: add them directly as class slots
            if "domain_of" in init_dict:
                for x in init_dict["domain_of"]:
                    cls_slots[x].append(sn)
                del init_dict["domain_of"]
            if "range" in init_dict:
                range = init_dict["range"]
                # Handle a range of multiple types
                if isinstance(range, list):
                    init_dict["any_of"] = [{"range": x} for x in init_dict["rangeIncludes"]]
                    del init_dict["range"]
            slot = SlotDefinition(sn, **init_dict)
            slot.slot_uri = str(p.n3(g.namespace_manager))
            yield slot

    def _dict_for_subject(self, g: Graph, s: URIRef, subject_type: typing.Literal["slot", "class"]) -> Dict[str, Any]:
        """
        Looks up triples for a subject and converts to dict using linkml keys.

        :param g: RDFS graph
        :param s: property URI in that graph
        :return: Dictionary mapping linkml metamodel keys to values
        """
        init_dict = {}
        # Each RDFS predicate/object pair corresponds to a LinkML key value pair for the slot
        for pp, obj in g.predicate_objects(s):
            if pp == RDF.type:
                continue
            metaslot_name = self._element_from_iri(pp)
            logging.debug(f"Mapping {pp} -> {metaslot_name}")
            # Filter out slots that don't belong in a class definition
            if subject_type == "class" and metaslot_name not in self.classdef_slots:
                continue
            # Filter out slots that don't belong in a slot definition
            if subject_type == "slot" and metaslot_name not in self.slotdef_slots:
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

    def _element_from_iri(self, iri: URIRef) -> str | None:
        r = self.reverse_metamodel_mappings.get(iri, [])
        if len(r) > 0:
            if len(r) > 1:
                logging.debug(f"Multiple mappings for {iri}: {r}")
            return r[0]

    def _object_to_value(self, obj: Any, metaslot: SlotDefinition) -> Any:
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

    def _as_name(self, v: URIRef) -> str:
        v_str = str(v)
        for sep in ["#", "/", ":"]:
            if sep in v_str:
                return v_str.split(sep)[-1]
        return v_str
