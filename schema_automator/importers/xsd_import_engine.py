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

def get_value_element(cls: ClassDefinition) -> SlotDefinition:
    if not isinstance(cls.attributes, dict):
        raise ValueError("cls.attributes should be a dictionary at this point")
    if "value" not in cls.attributes:
        raise ValueError("Value element should have been added by this stage")
    return cast(SlotDefinition, cls.attributes["value"])

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

    def visit_annotation(self, el: etree.ElementBase, existing: str | None = None) -> str:
        """
        Converts an annotation into a string to be used for documentation

        See https://www.w3.org/TR/2012/REC-xmlschema11-1-20120405/structures.html#declare-annotation

        Params:
            el: the <xsd:annotation> element
            existing: any existing documentation to append to
        """
        # Note: This only supports xsd:documentation, other annotation types are ignored
        text = []
        if existing is not None:
            text.append(existing)
        for child in el:
            if child.tag == f"{{{XSD}}}documentation":
                text.append(self.visit_documentation(child))
        return "\n".join(text)

    def visit_simple_type_restriction(self, el: etree.ElementBase, slot: SlotDefinition | AnonymousSlotExpression) -> None:
        """"
        Visits an <xsd:restriction> and applies type restrictions to a slot.

        Despite the name, this can be used for both simple types:
            ```xml
            <xsd:simpleType>
                <xsd:restriction>
                ...
                </xsd:restriction>
            </xsd:simpleType>
            ```
        and complex types:
            ```xml
            <xsd:complexType>
                <xsd:simpleContent>
                    <xsd:restriction>
                    ...
                    </xsd:restriction>
                </xsd:simpleContent>
            </xsd:complexType>
            ```
        Since there are a subset of elements that can be used inside both.
        """
        slot.is_a = el.attrib["base"]
        for child in el:
            if child.tag == f"{{{XSD}}}minInclusive":
                slot.minimum_value = child.attrib["value"]
            elif child.tag == f"{{{XSD}}}maxInclusive":
                slot.maximum_value = child.attrib["value"]
            elif child.tag == f"{{{XSD}}}pattern":
                slot.pattern = child.attrib["value"]
            elif child.tag == f"{{{XSD}}}minLength":
                slot.minimum_cardinality = child.attrib["value"]
            elif child.tag == f"{{{XSD}}}maxLength":
                slot.maximum_cardinality = child.attrib["value"]

    def visit_simple_content_restriction(self, el: etree.ElementBase, cls: ClassDefinition) -> None:
        """
        Visit a restriction inside a simple content element:
        ```xml
        <xsd:complexType>
            <xsd:simpleContent>
                <xsd:restriction>
                ...
                </xsd:restriction>
            </xsd:simpleContent>
        </xsd:complexType>
        ```
        """
        value = get_value_element(cls)
        self.visit_simple_type_restriction(el, value)
        for child in el:
            if child.tag == f"{{{XSD}}}attribute":
                if cls.attributes is None:
                    cls.attributes = {}
                cls.attributes[child.attrib["name"]] = self.visit_attribute(child)

    def visit_simple_content_extension(self, el: etree.ElementBase, cls: ClassDefinition) -> None:
        """
        Visit a:
        ```xml
        <xsd:complexType>
            <xsd:simpleContent>
                <xsd:extension>
                ...
                </xsd:extension>
            </xsd:simpleContent>
        </xsd:complexType>
        ```
        """
        cls.is_a = el.attrib["base"]
        for child in el:
            if child.tag == f"{{{XSD}}}attribute":
                cls.attributes[child.attrib["name"]] = self.visit_attribute(child)

    def visit_simple_content(self, el: etree.ElementBase, cls: ClassDefinition) -> None:
        """
        Visit a:
        ```xml
        <xsd:complexType>
            <xsd:simpleContent>
                ...
            </xsd:simpleContent>
        </xsd:complexType>
        ```
        See 3.4.2.2 Mapping Rules for Complex Types with Simple Content: https://www.w3.org/TR/2012/REC-xmlschema11-2-20120405/datatypes.html#xr-defn

        simpleContent maps to a ClassDefinition as it can have multiple values due to XML attributes. 
        It must also have a main value which is the content inside the XML element. Therefore:
        ```xml
        <xsd:complexType name="SomeClass">
            <xsd:simpleContent>
                <xsd:restriction base="xsd:string">
                    <xsd:attribute name="someAttr" type="xsd:integer"/>
                </xsd:restriction>
            </xsd:simpleContent>
        </xsd:complexType>
        ```
        Would be represented as:
        ```yaml
        SomeClass:
            attributes:
                someAttr:
                    range: integer
                value:
                    range: string
        ```
        """
        value_slot = SlotDefinition(
            name="value",
            comments=["Mapped from the main content of the element"],
        )

        cls.attributes["value"] = value_slot
        for child in el:
            if child.tag == f"{{{XSD}}}restriction":
                self.visit_simple_content_restriction(child, cls)
            elif child.tag == f"{{{XSD}}}extension":
                self.visit_simple_content_extension(child, cls)
            elif child.tag == f"{{{XSD}}}annotation":
                # Annotations inside simple content are applied to the value slot, not the class
                value_slot.description = self.visit_annotation(child, value_slot.description)

    def visit_simple_type(self, el: etree.ElementBase, slot: SlotDefinition | AnonymousSlotExpression) -> None:
        """
        Converts an xsd:simpleType into a LinkML type

        A simple type always maps to a slot in LinkML since it cannnot have attributes or children.
        e.g.
        ```xml
        <xsd:attribute>
            <xsd:simpleType>
             ...
            </xsd:simpleType>
          </xsd:attribute>
        ```

        See 3.16.2 XML Representation of Simple Type Definition Schema Components: https://www.w3.org/TR/xmlschema11-1/#declare-datatype

        Params:
            el: a <xsd:simpleType> element
            slot: the slot to annotate
        """
        for child in el:
            if child.tag == f"{{{XSD}}}annotation":
                slot.description = self.visit_annotation(child, slot.description)
            elif child.tag == f"{{{XSD}}}restriction":
                self.visit_simple_type_restriction(child, slot)
            elif child.tag == f"{{{XSD}}}list":
                slot.multivalued = True
                if "itemType" in child.attrib:
                    slot.range = child.attrib["itemType"]
                else:
                    slot.range = AnonymousSlotExpression()
                    for list_child in child:
                        if list_child.tag == f"{{{XSD}}}simpleType":
                            self.visit_simple_type(list_child, slot.range)
                        else:
                            raise ValueError("Only xsd:simpleType is allowed inside xsd:list")
                raise ValueError("xsd:list must have an itemType attribute or an xsd:simpleType child element")
            elif child.tag == f"{{{XSD}}}union":
                slot.any_of = []
                for union_child in child:
                    union_slot = AnonymousSlotExpression()
                    self.visit_simple_type(union_child, union_slot)
                    slot.any_of.append(union_slot)

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
    
    def visit_complex_content_child(self, el: etree.ElementBase, cls: ClassDefinition) -> None:
        """
        Visit any of the following children of an xsd:complexContent element.
        We can re-use the functionality since each of these elements can contain sequence, group, choice etc

        ```xml
        <xsd:complexType>
            <xsd:complexContent>
                <xsd:extension>
                    ...
                </xsd:extension>
            </xsd:complexContent>
        </xsd:complexType>,
        ```, or

        ```xml
        <xsd:complexType>
            <xsd:complexContent>
                <xsd:restriction>
                    ...
                </xsd:restriction>
            </xsd:complexContent>
        </xsd:complexType>
        ```
        """
        if "base" in el.attrib:
            cls.is_a = el.attrib["base"]

        if el.tag == f"{{{XSD}}}sequence":
            cls.attributes |= {
                slot.name: slot for slot in self.visit_sequence(el)
            }
        elif el.tag == f"{{{XSD}}}group":
            raise NotImplementedError("xsd:group is not yet supported")
        elif el.tag == f"{{{XSD}}}all":
            raise NotImplementedError("xsd:all is not yet supported")
        elif el.tag == f"{{{XSD}}}choice":
            cls.attributes |= {
                slot.name: slot for slot in self.visit_choice(el)
            }
        elif el.tag == f"{{{XSD}}}attribute":
            slot = self.visit_attribute(el)
            cls.attributes[slot.name] = slot
        elif el.tag == f"{{{XSD}}}annotation":
            cls.description = self.visit_annotation(el, cls.description)
    
    def visit_complex_content(self, el: etree.ElementBase, cls: ClassDefinition) -> None:
        """
        Visit a:
        ```xml
        <xsd:complexType>
            <xsd:complexContent>
                ...
            </xsd:complexContent>
        </xsd:complexType>

        See 3.4.2.3 Mapping Rules for Complex Types with Complex Content: https://www.w3.org/TR/xmlschema11-1/#dcl.ctd.ctcc

        Params:
            el: the <xsd:complexContent> element
            cls: the class to annotate, derived from the enclosing <xsd:complexType> element
        """
        #: If we have found an extension or restriction
        for child in el:
            if child.tag == f"{{{XSD}}}extension":
                self.visit_complex_content_child(child, cls)
            elif child.tag == f"{{{XSD}}}restriction":
                self.visit_complex_content_child(child, cls)
            elif child.tag == f"{{{XSD}}}annotation":
                cls.description = self.visit_annotation(child, cls.description)
                
    def visit_complex_type(self, el: etree.ElementBase) -> ClassDefinition:
        """
        Converts an `<xsd:complexType>` into a ClassDefinition

        See 3.4 Complex Type Definitions: https://www.w3.org/TR/xmlschema11-1/#Complex_Type_Definitions
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

        found_content = False
        for child in el:
            if child.tag == f"{{{XSD}}}complexContent":
                self.visit_complex_content(child, cls)
                found_content = True
            elif child.tag == f"{{{XSD}}}simpleContent":
                self.visit_simple_content(child, cls)
                found_content = True

        if not found_content:
            """ 
            3.4.2.3.2 Mapping Rules for Complex Types with Implicit Complex Content:
            > When the <complexType> source declaration has neither <simpleContent> nor <complexContent> as a child, it is taken as shorthand for complex content restricting ·xs:anyType·. 
            """
            for child in el:
                self.visit_complex_content_child(child, cls)

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
