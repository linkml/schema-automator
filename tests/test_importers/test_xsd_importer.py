from linkml_runtime import SchemaView
from schema_automator.importers import XsdImportEngine
import tempfile

def parse_string(xsd: str, preserve_casing: bool = False) -> SchemaView:
    engine = XsdImportEngine()
    with tempfile.NamedTemporaryFile(mode='w', delete=False) as f:
        f.write('''<xsd:schema
            xmlns="http://www.dummy/name/space"
            targetNamespace="http://www.dummy/name/space"
            xmlns:xsd="http://www.w3.org/2001/XMLSchema"
            xmlns:xml="http://www.w3.org/XML/1998/namespace"
            version="2"
            elementFormDefault="qualified">
        ''')
        f.write(xsd)
        f.write("</xsd:schema>")
    schema = engine.convert(f.name, preserve_casing=preserve_casing)
    return SchemaView(schema)

def test_embedded_type():
    schema = parse_string('<xsd:element name="AcquisitionDate" type="xsd:dateTime"/>')
    assert len(schema.all_classes()) == 1
    root = schema.get_class("SchemaRoot")
    assert len(root.attributes) == 1
    assert root.attributes["acquisitionDate"].range == "DateTime"
    assert "xsd:element" in root.attributes["acquisitionDate"].instantiates
    assert "xsd" in schema.schema.prefixes

def test_complex_type():
    schema = parse_string('''
        <xsd:element name="MyClass">
            <xsd:annotation>
                <xsd:documentation>
                    Some docs
                </xsd:documentation>
            </xsd:annotation>
            <xsd:complexType>
                <xsd:sequence>
                    <xsd:element name="elementSlotA" type="xsd:float"/>
                    <xsd:element name="elementSlotB" type="xsd:integer"/>
                </xsd:sequence>
                <xsd:attribute name="attributeSlot" type="xsd:boolean"/>
            </xsd:complexType>
        </xsd:element>
    ''')
    assert len(schema.all_classes()) == 2
    my_class = schema.get_class("MyClass")
    assert len(my_class.attributes) == 3
    assert my_class.attributes["elementSlotA"].range == "Float"
    assert my_class.attributes["elementSlotB"].range == "Integer"
    assert my_class.attributes["attributeSlot"].range == "Boolean"
    # The annotation should be applied to the slot and not the class
    assert my_class.description is None

    root = schema.get_class("SchemaRoot")
    assert len(root.attributes) == 1
    assert root.attributes["myClass"].range == "MyClass"
    assert root.attributes["myClass"].description == "Some docs"


def test_preserve_casing_false_is_lcamelcase():
    schema = parse_string('<xsd:element name="PowersystemUnit" type="xsd:dateTime"/>')
    root = schema.get_class("SchemaRoot")
    assert list(root.attributes) == ["powersystemUnit"]


def test_preserve_casing_true_keeps_source_case():
    schema = parse_string(
        '<xsd:element name="PowersystemUnit" type="xsd:dateTime"/>',
        preserve_casing=True,
    )
    root = schema.get_class("SchemaRoot")
    assert list(root.attributes) == ["PowersystemUnit"]


def test_preserve_casing_true_applies_to_attribute_and_element():
    schema = parse_string(
        '''
        <xsd:element name="AnlageEegBiomasse">
            <xsd:complexType>
                <xsd:sequence>
                    <xsd:element name="Registrierungsdatum" type="xsd:date"/>
                </xsd:sequence>
                <xsd:attribute name="AnlagenkennzifferAnlagenregister" type="xsd:string"/>
            </xsd:complexType>
        </xsd:element>
        ''',
        preserve_casing=True,
    )
    cls = schema.get_class("AnlageEegBiomasse")
    assert cls.attributes["Registrierungsdatum"]
    assert cls.attributes["AnlagenkennzifferAnlagenregister"]
