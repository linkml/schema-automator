from linkml_runtime.linkml_model.meta import SchemaDefinition
from schema_automator.importers import XsdImportEngine
import tempfile

def parse_string(xsd: str) -> SchemaDefinition:
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
    return engine.convert(f.name)

def test_embedded_type():
    schema = parse_string('<xsd:element name="AcquisitionDate" minOccurs="0" maxOccurs="1" type="xsd:dateTime"/>')
    assert True
