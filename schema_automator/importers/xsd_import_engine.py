from dataclasses import dataclass, field
from textwrap import dedent
from typing import Any, Iterable, cast
import re
from urllib.parse import urljoin
from linkml.utils.schema_builder import SchemaBuilder
from linkml_runtime.linkml_model import (
    SchemaDefinition,
    SlotDefinition,
    ClassDefinition,
)
from linkml_runtime.linkml_model.meta import AnonymousSlotExpression, Bool
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
    "NMTOKEN": "String",
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
    "positiveInteger",
}
XSD = "http://www.w3.org/2001/XMLSchema"
NAMESPACES = {"xsd": "http://www.w3.org/2001/XMLSchema"}


def xsd_to_linkml_type(xsd_type: etree.QName) -> str:
    """
    Returns the LinkML type from an XSD type
    """
    if xsd_type.namespace == XSD:
        if xsd_type.localname in TYPE_MAP:
            # Atomic XSD types can be looked up
            return TYPE_MAP[xsd_type.localname]
        elif xsd_type.localname in MISSING_TYPES:
            raise ValueError(
                f"Atomic type {xsd_type} does not have a corresponding LinkML type"
            )
        else:
            raise ValueError(f"Atomic type {xsd_type} is not defined in the standard")
    else:
        # Assume any remaining type is a complex type that we have or will define separately
        return xsd_type.localname


def resolve_type(el: etree.ElementBase) -> etree.QName:
    """
    Returns the fully resolved type of an XSD element

    Params:
        el: the element to resolve the type of. Must be either an <xsd:element> or <xsd:attribute>, with a 'type' attribute.
    """
    typ: str = el.attrib.get("type", "string")
    if typ.count(":") == 1:
        # Hacky fallback for when a custom namespace is used
        prefix, name = typ.split(":")
        return etree.QName(el.nsmap[prefix], name)
    else:
        return etree.QName(typ)


def element_to_linkml_type(el: etree.ElementBase) -> str:
    """
    Returns the LinkML type of an XSD element

    Params:
        el: the element to resolve the type of. Must be either an <xsd:element> or <xsd:attribute>, with a 'type' attribute.
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


@dataclass
class XsdImportEngine(ImportEngine):
    sb: SchemaBuilder = field(default_factory=SchemaBuilder)
    target_ns: str | None = None

    def visit_element(self, el: etree.ElementBase) -> SlotDefinition:
        """
        Converts an xsd:element into a SlotDefinition
        """
        name: str | None = el.attrib.get("name")
        """
        XML supports empty elements, which we can represent as booleans.
        For example this XML data:
        ```xml
        <parent>
            <some_flag></some_flag>
        </parent>
        ```
        Can be represented as:
        ```yaml
        parent:
            some_flag: true
        ```
        """
        range: str | ClassDefinition = "boolean"
        any_of: list[AnonymousSlotExpression] = []
        multivalued: bool | None = None
        description: str | None = None

        if name is None and "ref" in el.attrib:
            # If we find a ref, the slot's range is a reference to another class
            # We can make up a name for the slot using the referenced class, although the slot doesn't actually have a name in XSD
            range = el.attrib["ref"]
            name = formatutils.lcamelcase(el.attrib["ref"])

        for child in el:
            if child.tag == f"{{{XSD}}}complexType":
                # If we find a complex type, the slot defines a new class type
                range = self.visit_complex_type(child)
            if child.tag == f"{{{XSD}}}simpleType":
                # If we find a simple type, the range is a restriction of a primitive type
                simple_type = self.visit_simple_type(child)
                range = simple_type.range
                multivalued = cast(bool | None, simple_type.multivalued)
                any_of = cast(list[AnonymousSlotExpression], simple_type.any_of)
            if child.tag == f"{{{XSD}}}annotation":
                # If we find an annotation, we can use it as documentation
                description = self.visit_annotation(child)

        if "type" in el.attrib:
            range = element_to_linkml_type(el)

        if name is None:
            raise ValueError("Could not find name for element")

        return SlotDefinition(
            name=name,
            slot_uri=urljoin(self.target_ns, name) if self.target_ns else None,
            range=range,
            multivalued=multivalued,
            any_of=any_of,
            description=description,
            keywords=["Child Element"],
        )

    def visit_documentation(self, el: etree.ElementBase) -> str:
        """
        Converts an xsd:documentation into a string
        """
        # return re.sub(r"\w+", " ", dedent(el.text))
        return dedent(el.text).replace("\n", " ").strip()

    def visit_annotation(self, el: etree.ElementBase) -> str:
        """
        Converts an xsd:annotation into a string to be used for documentation

        See https://www.w3.org/TR/2012/REC-xmlschema11-1-20120405/structures.html#declare-annotation
        """
        # Note: This only supports xsd:documentation, other annotation types are ignored
        text = []
        for child in el:
            if child.tag == f"{{{XSD}}}documentation":
                text.append(self.visit_documentation(child))
        return "\n".join(text)

    def visit_simple_type(self, el: etree.ElementBase) -> AnonymousSlotExpression:
        """
        Converts an xsd:simpleType into a LinkML type

        See https://www.w3.org/TR/2012/REC-xmlschema11-2-20120405/datatypes.html#xr-defn
        """
        ret = AnonymousSlotExpression()
        for child in el:
            if child.tag == f"{{{XSD}}}annotation":
                ret.description = self.visit_annotation(child)
            elif child.tag == f"{{{XSD}}}restriction":
                ret.range = child.attrib["base"]
            elif child.tag == f"{{{XSD}}}list":
                ret.multivalued=True
                if "itemType" in child.attrib:
                    ret.range=child.attrib["itemType"]
                else:
                    for list_child in child:
                        ret.range=self.visit_simple_type(list_child),
                raise ValueError("xsd:list must have an itemType attribute or an xsd:simpleType child element")
            elif child.tag == f"{{{XSD}}}union":
                ret.any_of=[self.visit_simple_type(union_child) for union_child in child]

        return ret

    def visit_attribute(self, el: etree.ElementBase) -> SlotDefinition:
        """
        Converts an xsd:attribute into a SlotDefinition
        """
        description: str | None = None

        for child in el:
            if child.tag == f"{{{XSD}}}annotation":
                description = self.visit_annotation(child)

        return SlotDefinition(
            name=formatutils.lcamelcase(el.attrib["name"]),
            slot_uri=(
                urljoin(self.target_ns, el.attrib["name"]) if self.target_ns else None
            ),
            range=element_to_linkml_type(el),
            keywords=["XML Attribute"],
            description=description
        )

    def visit_complex_type(self, el: etree.ElementBase) -> ClassDefinition:
        """
        Converts an xsd:complexType into a ClassDefinition
        """
        name: str | None = el.attrib.get("name")
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
                cls.attributes |= {
                    slot.name: slot for slot in self.visit_sequence(child)
                }
            elif child.tag == f"{{{XSD}}}choice":
                cls.attributes |= {
                    slot.name: slot for slot in self.visit_choice(child)
                }
            elif child.tag == f"{{{XSD}}}attribute":
                slot = self.visit_attribute(child)
                cls.attributes[slot.name] = slot
            elif child.tag == f"{{{XSD}}}annotation":
                cls.description = self.visit_annotation(child)

        return cls

    def visit_choice(self, el: etree.ElementBase) -> Iterable[SlotDefinition]:
        """
        Converts an xsd:choice into a list of SlotDefinitions
        """
        # TODO: indicate that not all slots can be used at the same time
        return self.visit_sequence(el)

    def visit_sequence(self, el: etree.ElementBase) -> Iterable[SlotDefinition]:
        """
        Converts an xsd:sequence into a list of SlotDefinitions
        """
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
        """
        Converts an xsd:schema into a SchemaDefinition
        """
        self.target_ns = schema.attrib.get("targetNamespace")
        if self.target_ns is not None and not self.target_ns.endswith("/"):
            # Ensure that the target namespace ends with a slash
            self.target_ns += "/"

        for child in schema:
            # A top level element can be treated as a class
            if child.tag == f"{{{XSD}}}element":
                slot = self.visit_element(child)
                if isinstance(slot.range, ClassDefinition):
                    self.sb.add_class(slot.range)
            elif child.tag == f"{{{XSD}}}complexType":
                self.sb.add_class(self.visit_complex_type(child))

    def convert(self, file: str, **kwargs) -> SchemaDefinition:
        parser = etree.XMLParser(remove_blank_text=True)
        tree = etree.parse(file, parser=parser)
        self.visit_schema(tree.getroot())
        return self.sb.schema
