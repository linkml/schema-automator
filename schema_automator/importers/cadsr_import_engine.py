"""
CADSR CDE Import Engine

.. code-block::

   * DataElement
    * DataElementConcept
     * ObjectClass

E.g.

DE Concept "Adverse Event Attribution" (AE_ATTR) from CEPT

May have multiple CDEs associated with it; these may be different CDEs from different contexts

"""
import logging
import urllib
from typing import Union, Dict, Tuple, List, Any, Optional, Iterable

from dataclasses import dataclass

from linkml.utils.schema_builder import SchemaBuilder
from linkml_runtime.linkml_model import Annotation
from linkml_runtime.linkml_model.meta import SchemaDefinition, SlotDefinition, EnumDefinition, \
    PermissibleValue, UniqueKey, ClassDefinition
from linkml_runtime.loaders import json_loader
from linkml_runtime.utils.formatutils import camelcase, underscore

from schema_automator.importers.import_engine import ImportEngine
import schema_automator.metamodels.cadsr as cadsr


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

@dataclass
class CADSRImportEngine(ImportEngine):
    """
    An ImportEngine that imports NCI CADSR CDEs

    See:

    https://github.com/monarch-initiative/cde-harmonization
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
                source = urllib.parse.quote(ctxt)
                source = f"cadsr:{source}"
                slot = SlotDefinition(
                    name=urllib.parse.quote(underscore(f"{ctxt} {cde.preferredName}")),
                    slot_uri=f"cadsr:{cde.publicId}",
                    title=cde.preferredName,
                    description=cde.preferredDefinition,
                    aliases=[cde.longName],
                    source=source,
                )
                slots[slot.name] = slot
                concept = cde.DataElementConcept
                concept_name = urllib.parse.quote(camelcase(f"{ctxt} {concept.preferredName}"))
                parent_concept_name = urllib.parse.quote(camelcase(concept.longName))
                if parent_concept_name not in classes:
                    parent_cls = ClassDefinition(
                        name=parent_concept_name,
                        title=concept.preferredName,
                        description=concept.preferredDefinition,
                        #aliases=[concept.longName],
                        class_uri=f"cadsr:{concept.publicId}",
                    )
                    classes[parent_concept_name] = parent_cls
                if concept_name not in classes:
                    cls = ClassDefinition(
                        name=concept_name,
                        title=f"{concept.preferredName} ({ctxt})",
                        description=concept.preferredDefinition,
                        aliases=[concept.longName],
                        class_uri=f"cadsr:{concept.publicId}",
                        is_a=parent_concept_name,
                    )
                    classes[concept_name] = cls
                else:
                    cls = classes[concept_name]
                cls.slots.append(slot.name)
                objectClass = concept.ObjectClass
                # TODO
                valueDomain = cde.ValueDomain
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
                        pv_value = urllib.parse.quote(pv.value)
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
                        for c in vm.Concepts:
                            code = c.conceptCode.strip()
                            tgt_pv.meaning = f"NCIT:{code}"
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




