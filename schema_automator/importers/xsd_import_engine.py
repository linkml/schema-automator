from dataclasses import dataclass
from urllib.parse import urljoin
from xml.etree import ElementTree
from linkml.utils.schema_builder import SchemaBuilder
from linkml_runtime import SchemaView
from linkml_runtime.linkml_model import (
    SchemaDefinition,
    SlotDefinition,
    ClassDefinition,
)
from linkml_runtime.utils import formatutils
from lxml import etree


from linkml_runtime.linkml_model import SchemaDefinition
from schema_automator.importers.import_engine import ImportEngine

# Mapping between https://www.w3.org/TR/2012/REC-xmlschema11-2-20120405/datatypes.html#built-in-primitive-datatypes and https://linkml.io/linkml-model/latest/docs/#types
TYPE_MAP = {
    "anyURI": "Uri",
    "boolean": "Boolean",
    "date": "Date",
    "dateTime": "DateTime",
    "decimal": "Decimal",
    "double": "Double",
    "float": "Float",
    "string": "String",
    "time": "Time",
    "int": "Integer",
    "integer": "Integer"
}
MISSING_TYPES = {
    "base64Binary",
    "duration",
    "hexBinary",
    "gDay",
    "gMonth",
    "gMonthDay",
    "gYear",
    "gYearMonth",
    "NOTATION",
    "QName",
    "normalizedString",
    "token",
    "language",
    "NMTOKEN",
    "NMTOKENS",
    "Name",
    "NCName",
    "ID",
    "IDREF",
    "IDREFS",
    "ENTITY",
    "ENTITIES",
    "nonPositiveInteger",
    "negativeInteger",
    "long",
    "short",
    "byte",
    "nonNegativeInteger",
    "unsignedLong",
    "unsignedInt",
    "unsignedShort",
    "unsignedByte",
    "positiveInteger"
}
XSD = "http://www.w3.org/2001/XMLSchema"
NAMESPACES={"xsd": "http://www.w3.org/2001/XMLSchema"}

def xsd_to_linkml_type(xsd_type: etree.QName) -> str:
    if xsd_type.namespace == XSD:
        if xsd_type.localname in TYPE_MAP:
            # Atomic XSD types can be looked up
            return TYPE_MAP[xsd_type.localname]
        elif xsd_type.localname in MISSING_TYPES:
            raise ValueError(f"Atomic type {xsd_type} does not have a corresponding LinkML type")
        else:
            raise ValueError(f"Atomic type {xsd_type} is not defined in the standard")
    else:
        # Assume any remaining type is a complex type that we have or will define separately
        return xsd_type.localname

def resolve_type(el: etree.ElementBase) -> etree.QName:
    """
    Returns the fully resolved type of an XSD element
    """
    typ: str = el.attrib['type']
    if typ.count(":") == 1:
        # Hacky fallback for when a custom namespace is used
        prefix, name = typ.split(":")
        return etree.QName(el.nsmap[prefix], name)
    else:
        return etree.QName(typ)

def element_to_linkml_type(el: etree.ElementBase) -> str:
    """
    Returns the LinkML type of an XSD element
    """
    return xsd_to_linkml_type(resolve_type(el))

@dataclass
class XsdImportEngine(ImportEngine):

    def el_to_class(self, el: etree.ElementBase, name: str, target_ns: str | None) -> ClassDefinition:
        attributes: dict[str, SlotDefinition] = {}
        # Find all child elements and add them as slots
        for el in el.findall(f".//xsd:element" , namespaces=NAMESPACES):#, namespaces=NAMESPACES):
            attrib_name = formatutils.lcamelcase(el.attrib['name']) 
            attributes[attrib_name] = SlotDefinition(
                name=attrib_name,
                slot_uri=urljoin(target_ns, el.attrib['name']) if target_ns else None,
                range=element_to_linkml_type(el),
            )
        # Find all attributes and add them as slots
        for el in el.findall(f".//xsd:attribute", namespaces=NAMESPACES):
            attrib_name = formatutils.lcamelcase(el.attrib['name']) 
            attributes[attrib_name] = SlotDefinition(
                name=attrib_name,
                range=element_to_linkml_type(el),
            )
        
        return ClassDefinition(
            name=formatutils.camelcase(name),
            class_uri=urljoin(target_ns, name) if target_ns else None,
            attributes=attributes
        )

    def convert(self, file: str, **kwargs) -> SchemaDefinition:
        sb = SchemaBuilder()
        # tree = ElementTree.parse(file)
        tree: etree._ElementTree = etree.parse(file)
        target_ns: str | None = tree.getroot().attrib.get('targetNamespace')
        sb.add_class(self.el_to_class(tree.getroot(), "Root", target_ns))
        for typ in tree.findall("//xsd:complexType[@name]", namespaces=NAMESPACES):
            sb.add_class(self.el_to_class(typ, typ.attrib['name'], target_ns))

        return sb.schema
