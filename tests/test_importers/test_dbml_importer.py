import pytest
from linkml_runtime.linkml_model import SchemaDefinition
from schema_automator.importers.dbml_import_engine import DbmlImportEngine

# Sample DBML content for testing
DBML_SAMPLE = """
Table Users {
  id int [primary key, not null]
  email varchar [unique, not null]
  username varchar
}

Table Orders {
  order_id int [not null]
  user_id int [not null]
  product_id int [not null]
  quantity int
}

Table Countries {
  code varchar [primary key, not null]
  name varchar [not null]
}
"""

@pytest.fixture
def dbml_file(tmp_path):
    """
    Fixture to create a temporary DBML file.
    """
    dbml_path = tmp_path / "test.dbml"
    dbml_path.write_text(DBML_SAMPLE)
    print(dbml_path)
    return dbml_path

@pytest.fixture
def importer():
    """
    Fixture to initialize the DbmlImportEngine.
    """
    return DbmlImportEngine()

def test_dbml_to_linkml_conversion(dbml_file, importer):
    """
    Test the basic conversion of DBML to a LinkML schema.
    """
    schema = importer.convert(file=str(dbml_file), name="TestSchema")

    # Assert the schema object is created
    assert isinstance(schema, SchemaDefinition)

    # Check that expected classes are present
    assert "Users" in schema.classes
    assert "Orders" in schema.classes

    # Check that expected slots are present
    assert "id" in schema.slots
    assert schema.slots["id"].identifier
    assert schema.slots["id"].required


def test_primary_key_handling(dbml_file, importer):
    """
    Test correct handling of primary keys and required attributes.
    """
    schema = importer.convert(file=str(dbml_file), name="TestSchema")

    # Check that primary keys are marked as required and identifiers
    users_class = schema.classes["Users"]
    assert "id" in users_class.slots
    assert schema.slots["id"].identifier
    assert schema.slots["id"].required
