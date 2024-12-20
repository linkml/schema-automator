from dataclasses import dataclass, field
from typing import Iterable
from urllib.parse import urljoin
from xml.etree import ElementTree
from linkml.utils.schema_builder import SchemaBuilder
from linkml_runtime import SchemaView
from linkml_runtime.linkml_model import (
    SchemaDefinition,
    SlotDefinition,
    ClassDefinition,
)
from linkml_runtime.linkml_model.meta import AnonymousClassExpression
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
    "integer": "Integer",
    # NMTOKEN is basically just a string inside an attribute
    "NMTOKEN": "String"
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
    typ: str = el.attrib.get('type', "string")
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

def find_class_name(el: etree.ElementBase, root_name: str = "Root") -> str:
    """
    Returns the name of the class that this element is a slot for

    Params:
        el: the element that will be a slot for the class whose name we want to find
        root_name: class name to assign to the schema's root
    """
    for parent in el.iterancestors():
        if "name" in parent.attrib:
            return parent.attrib["name"]
        elif parent.tag == f"{{{XSD}}}schema":
            return root_name
    raise ValueError("Could not find class name for element")

# def visit_element(el: etree.ElementBase, sb: SchemaBuilder, target_ns: str | None) -> None:
#     """
#     Adds an XSD element as an attribute to a class in the schema

#     Params:
#         el: the <xsd:element> to add
#         sb: the schema builder to add the element to
#     """
#     cls_name = find_class_name(el)
#     attrib_name = formatutils.lcamelcase(el.attrib['name'])
#     if cls_name in sb.schema.classes:
#         cls = sb.schema.classes[cls_name]
#     else:
#         cls = ClassDefinition(
#             cls_name,
#             class_uri=urljoin(target_ns, cls_name) if target_ns else None,
#         )
#         sb.add_class(cls)

#     cls.attributes[attrib_name] = SlotDefinition(
#         name=attrib_name,
#         slot_uri=urljoin(cls.class_uri, el.attrib['name']) if cls.class_uri else None,
#         range=element_to_linkml_type(el)
#     )

@dataclass
class XsdImportEngine(ImportEngine):
    sb: SchemaBuilder = field(default_factory=SchemaBuilder)
    target_ns: str | None = None

    def visit_element(self, el: etree.ElementBase) -> SlotDefinition:
        name: str | None = el.attrib.get('name')
        if name is None and "ref" in el.attrib:
            name = formatutils.lcamelcase(el.attrib['ref'])
        if name is None:
            raise ValueError("Could not find name for element")

        slot = SlotDefinition(
            name=name,
            slot_uri=urljoin(self.target_ns, name) if self.target_ns else None,
        )

        for child in el:
            if child.tag == f"{{{XSD}}}complexType":
                # If we find a complex type, the slot defines a new class type
                slot.range = self.visit_complex_type(child)

        if "type" in el.attrib:
            slot.range = element_to_linkml_type(el)

        return slot

    def visit_attribute(self, el: etree.ElementBase) -> SlotDefinition:
        return SlotDefinition(
            name=el.attrib['name'],
            slot_uri=urljoin(self.target_ns, el.attrib['name']) if self.target_ns else None,
            range=element_to_linkml_type(el)
        )

    def visit_complex_type(self, el: etree.ElementBase) -> ClassDefinition:
        name: str | None = el.attrib.get('name')
        if name is None:
            for parent in el.iterancestors():
                if "name" in parent.attrib:
                    name = parent.attrib["name"]
        if name is None:
            raise ValueError("Could not find name for complex type")
        cls = ClassDefinition(
            name=name,
            class_uri=urljoin(self.target_ns, name) if self.target_ns else None,
            attributes={}
        )

        for child in el:
            if child.tag == f"{{{XSD}}}sequence":
                cls.attributes |= {slot.name: slot for slot in self.visit_sequence(child)}
            if child.tag == f"{{{XSD}}}attribute":
                slot = self.visit_attribute(child)
                cls.attributes[slot.name] = slot

        return cls

    def visit_choice(self, el: etree.ElementBase) -> Iterable[SlotDefinition]:
        # TODO: indicate that not all slots can be used at the same time
        return self.visit_sequence(el)

    def visit_sequence(self, el: etree.ElementBase) -> Iterable[SlotDefinition]:
        for child in el:
            if child.tag == f"{{{XSD}}}element":
                yield self.visit_element(child)
            elif child.tag == f"{{{XSD}}}choice":
                yield from self.visit_choice(child)
            elif child.tag == f"{{{XSD}}}sequence":
                yield from self.visit_sequence(child)
            elif isinstance(child, etree._Comment):
                pass
            else:
                print(f"Skipping unknown tag {child.tag}")

    def visit_schema(self, schema: etree.ElementBase) -> None:
        self.target_ns = schema.attrib.get('targetNamespace')
        for child in schema:
            # A top level element can be treated as a class
            if child.tag == f"{{{XSD}}}element":
                slot = self.visit_element(child)
                if isinstance(slot.range, ClassDefinition):
                    self.sb.add_class(slot.range)
            elif child.tag == f"{{{XSD}}}complexType":
                self.sb.add_class(self.visit_complex_type(child))

    def convert(self, file: str, **kwargs) -> SchemaDefinition:
        tree = etree.parse(file)
        self.visit_schema(tree.getroot())
        # target_ns: str | None = tree.getroot().attrib.get('targetNamespace')
        # for element in tree.findall("//xsd:element", namespaces=NAMESPACES):
        #     visit_element(element, sb, target_ns=target_ns)
        # for element in tree.findall("//xsd:attribute", namespaces=NAMESPACES):
        #     visit_element(element, sb, target_ns=target_ns)
        # tree: etree._ElementTree = etree.parse(file)
        # target_ns: str | None = tree.getroot().attrib.get('targetNamespace')
        # sb.add_class(self.el_to_class(tree.getroot(), "Root", target_ns))
        # for typ in tree.findall("//xsd:complexType[@name]", namespaces=NAMESPACES):
        #     sb.add_class(self.el_to_class(typ, typ.attrib['name'], target_ns))

        return self.sb.schema
