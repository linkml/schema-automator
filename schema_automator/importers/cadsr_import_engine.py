"""
CADSR CDE Import Engine

This ingests the output of the caDSR API https://cadsrapi.cancer.gov/rad/NCIAPI/1.0/api
"""
import logging
import urllib
from typing import Union, Dict, Tuple, List, Any, Optional, Iterable, Iterator

from dataclasses import dataclass

from linkml.utils.schema_builder import SchemaBuilder
from linkml_runtime.linkml_model import Annotation
from linkml_runtime.linkml_model.meta import SchemaDefinition, SlotDefinition, EnumDefinition, \
    PermissibleValue, UniqueKey, ClassDefinition
from linkml_runtime.loaders import json_loader
from linkml_runtime.utils.formatutils import camelcase, underscore

from schema_automator.importers.import_engine import ImportEngine
import schema_automator.metamodels.cadsr as cadsr

ID_LABEL_PAIR = Tuple[str, str]

TMAP = {
    "DATE": "date",
    "NUMBER": "float",
    "ALPHANUMERIC": "string",
    "CHARACTER": "string",
    "HL7EDv3": "string",
    "HL7CDv3": "string",
    "java.lang.Double": "float",
    "Numeric Alpha DVG": "float",
    "SAS Date": "string",
    "java.util.Date": "date",
    "DATE/TIME": "datetime",
    "TIME": "time",
    "Integer": "integer",
    "java.lang.Integer": "integer",
    "Floating-point": "float",
}

def extract_concepts(concepts: List[cadsr.Concept]) -> Tuple[ID_LABEL_PAIR, List[str]]:
    main = None
    rest = []
    if not concepts:
        raise ValueError("No concepts")
    for concept in concepts:
        if concept.evsSource != "NCI_CONCEPT_CODE":
            continue
        id = f"NCIT:{concept.conceptCode.strip()}"
        pair = id, concept.longName
        if concept.primaryIndicator == "Yes":
            if main:
                raise ValueError(f"Multiple primary for: {concepts}")
            main = pair
        else:
            rest.append(id)
    if not main:
        logging.warning(f"No primary, using arbitrary from {rest}")
        main = rest[0]
        rest = rest[1:]
    return main, rest

@dataclass
class CADSRImportEngine(ImportEngine):
    """
    An ImportEngine that imports NCI CADSR CDEs

    Ingests the output of `caDSR API <https://cadsrapi.cancer.gov/rad/NCIAPI/1.0/api>`_.

    Note that we include a LinkML schema for this in schema_automator.metamodels.cadsr

    - Each CDE (DataElement) becomes a unique slot
    - the CDE is added as a lot of a context-specific class
    - the context-specific class is a subclass of the CDE's DataElementConcept

    Note that this creates a lot of 1-1 classes, as in many cases there is no
    attempt to group concepts. However, this is not always the case.

    E.g. the concept with publicId 2012668 (Access Route) is used in 5 contexts
    (AHRQ, CCR, ...)

    Each context-specific concept has its own set of CDEs

    See also https://github.com/monarch-initiative/cde-harmonization
    """

    def convert(self, paths: Iterable[str], id: str=None, name: str=None, **kwargs) -> SchemaDefinition:
        """
        Converts one or more CDE JSON files into LinkML

        :param files:
        :param kwargs:
        :return:
        """
        sb = SchemaBuilder()
        schema = sb.schema
        if id:
            schema.id = id
        if not name:
            name = package.name
        if name:
            schema.name = name
        classes = {}
        slots = {}
        enums = {}
        for path in paths:
            logging.info(f"Loading {path}")
            with (open(path) as file):
                container: cadsr.DataElementContainer
                container = json_loader.load(file, target_class=cadsr.DataElementContainer)
                cde = container.DataElement
                ctxt = cde.context
                ln = cde.longName
                source = urllib.parse.quote(ctxt)
                source = f"cadsr:{source}"
                # Each DataElement becomes one slot;
                # we make the name both unique and human readable
                # TODO: check this; frequently reused, e.g.
                # NCI Standards + Group ID
                slot = SlotDefinition(
                    name=urllib.parse.quote(underscore(f"{ctxt} {cde.preferredName} {ln}")),
                    slot_uri=f"cadsr:{cde.publicId}",
                    title=cde.preferredName,
                    description=cde.preferredDefinition,
                    aliases=[ln],
                    conforms_to=f"cadsr:DataElement",
                    source=source,
                )
                # each data element belongs to a concept
                # (may be reused across classes?)
                slots[slot.name] = slot
                dec = cde.DataElementConcept
                property = dec.Property
                main_prop_concept, prop_mappings = extract_concepts(property.Concepts)
                # a concept is linked to a class
                objectClass = dec.ObjectClass
                # NCIT concepts describing the class;
                # there will be one primary and possibly secondary concepts
                mainConcept, mappings = extract_concepts(objectClass.Concepts)
                class_name = objectClass.longName
                concept_name = urllib.parse.quote(camelcase(f"{ctxt} {class_name}"))
                parent_concept_name = urllib.parse.quote(class_name)
                if parent_concept_name not in classes:
                    parent_cls = ClassDefinition(
                        name=parent_concept_name,
                        title=objectClass.preferredName,
                        description=objectClass.preferredDefinition,
                        #aliases=[concept.longName],
                        class_uri=f"cadsr:{objectClass.publicId}",
                        exact_mappings=[mainConcept[0]],
                        broad_mappings=mappings,
                        conforms_to=f"cadsr:ObjectClass",
                    )
                    classes[parent_concept_name] = parent_cls
                if concept_name not in classes:
                    cls = ClassDefinition(
                        name=concept_name,
                        title=f"{dec.preferredName} ({ctxt})",
                        description=dec.preferredDefinition,
                        aliases=[dec.longName],
                        class_uri=f"cadsr:{dec.publicId}",
                        is_a=parent_concept_name,
                        conforms_to=f"cadsr:DataElementConcept",
                    )
                    classes[concept_name] = cls
                else:
                    cls = classes[concept_name]
                cls.slots.append(slot.name)
                # In theory the ObjectClass should link to a general class of utility in NCIT.
                # In practice the actual concept may not be so useful. E.g. in 2724331
                # "Agent Adverse Event Attribution Name" the DataConcept is
                # Agent (C1708) defined as "An active power or cause (as principle,
                # substance, physical or biological factor, etc.) that produces a specific effect."
                # which is very upper-ontological
                #for ocConcept in objectClass.Concepts:
                #    if ocConcept.evsSource == "NCI_CONCEPT_CODE":
                #        cls.is_a = f"NCIT:{ocConcept.conceptCode}"
                valueDomain = cde.ValueDomain
                # TODO
                conceptualDomain = valueDomain.ConceptualDomain
                pvs = valueDomain.PermissibleValues
                if pvs:
                    enum_name = urllib.parse.quote(camelcase(valueDomain.preferredName))
                    enum = EnumDefinition(
                        name=enum_name,
                        title=valueDomain.preferredName,
                        description=valueDomain.preferredDefinition,
                        aliases=[valueDomain.longName],
                        # enum_uri=f"cadsr:{valueDomain.publicId}",
                    )
                    enums[enum_name] = enum
                    rng = enum_name
                    for pv in pvs:
                        # url encode the value to escape symbols like <, >, etc.
                        pv_value = urllib.parse.quote(pv.value).replace("%20", " ")
                        tgt_pv = PermissibleValue(
                            text=pv_value,
                            title=pv.value,
                            description=pv.valueDescription,
                        )
                        enum.permissible_values[tgt_pv.text] = tgt_pv
                        vm = pv.ValueMeaning
                        tgt_pv.title = vm.preferredName
                        if not tgt_pv.description:
                            tgt_pv.description = vm.preferredDefinition
                        if vm.Concepts:
                            mainConcept, mappings = extract_concepts(vm.Concepts)
                            tgt_pv.meaning = mainConcept[0]
                            tgt_pv.broad_mappings = mappings
                else:
                    datatype = valueDomain.dataType
                    rng = TMAP.get(datatype, "string")
                slot.range = rng
                anns = []
                for rd in cde.ReferenceDocuments:
                    rf_type = urllib.parse.quote(underscore(rd.type))
                    anns.append(Annotation(
                        tag=rf_type,
                        value=rd.description,
                    ))
                for ann in anns:
                    slot.annotations[ann.tag] = ann

        sb.add_prefix("NCIT", "http://purl.obolibrary.org/obo/NCIT_")
        sb.add_prefix("cadsr", "http://example.org/cadsr/")
        sb.add_defaults()
        for c in schema.classes.values():
            c.from_schema = 'http://example.org/'
        schema = sb.schema
        schema.classes = classes
        schema.slots = slots
        schema.enums = enums
        return schema

    def as_rows(self, paths: Iterable[str], **kwargs) -> Iterator[Dict]:
        for path in paths:
            logging.info(f"Loading {path}")
            with (open(path) as file):
                container: cadsr.DataElementContainer
                container = json_loader.load(file, target_class=cadsr.DataElementContainer)
                cde = container.DataElement
                yield from self._obj_as_rows(cde, path)

    def _obj_as_rows(self, e: Union[cadsr.DataElement, cadsr.DataElementConcept, cadsr.Concept, cadsr.Property, cadsr.ObjectClass, cadsr.ConceptualDomain,
        cadsr.ValueDomain, cadsr.PermissibleValue, cadsr.ValueMeaning], parent_id: str) -> Iterator[Dict]:
        if isinstance(e, cadsr.Concept):
            obj = {
                "id": e.conceptCode,
                "context": e.evsSource,
                "longName": e.longName,
            }
        elif isinstance(e, cadsr.CDEPermissibleValue):
            obj = {
                "id": e.publicId,
                "value": e.value,
                "valueDescription": e.valueDescription,
            }
        else:
            obj = {
                "id": e.publicId,
                "preferredName": e.preferredName,
                "context": e.context,
                "longName": e.longName,
            }
        obj["parentId"] = parent_id
        obj["type"] = type(e).class_name
        id = obj["id"]
        yield obj
        if isinstance(e, cadsr.DataElement):
            yield from self._obj_as_rows(e.DataElementConcept, id)
            yield from self._obj_as_rows(e.ValueDomain, id)
        elif isinstance(e, cadsr.DataElementConcept):
            yield from self._obj_as_rows(e.ObjectClass, id)
            yield from self._obj_as_rows(e.Property, id)
            yield from self._obj_as_rows(e.ConceptualDomain, id)
        elif isinstance(e, cadsr.ValueDomain):
            for pv in e.PermissibleValues:
                yield from self._obj_as_rows(pv.ValueMeaning, id)
        if isinstance(e, (cadsr.ObjectClass, cadsr.Property, cadsr.PermissibleValue)):
            for c in e.Concepts:
                yield from self._obj_as_rows(c, id)






