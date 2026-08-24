"""Tests for the SHACL import engine.

SHACL relates shapes to classes in two ways and both appear in the wild, so both
are covered: ``sh:targetClass`` (used by DCAT-AP and most hand-written shape
files) and implicit-class, where the shape *is* the class (used by large published
ontologies such as ASHRAE 223P and Brick).
"""

import os

import pytest
from linkml_runtime import SchemaView

from schema_automator.importers.shacl_import_engine import ShaclImportEngine
from schema_automator.utils.schemautils import write_schema
from tests import INPUT_DIR, OUTPUT_DIR

SIMPLE = os.path.join(INPUT_DIR, "shacl_simple.ttl")
OUTSCHEMA = os.path.join(OUTPUT_DIR, "user_from_shacl_simple.yaml")


@pytest.fixture(scope="module")
def simple_schema():
    """shacl_simple.ttl imported: one sh:targetClass shape with four properties."""
    engine = ShaclImportEngine()
    return engine.convert(
        SIMPLE, default_prefix="usr", model_uri="http://example.org/", identifier="id"
    )


def test_target_class_becomes_the_class(simple_schema):
    """ex:UserShape targets ex:User, so the class is User -- not UserShape."""
    assert "User" in simple_schema.classes
    assert "UserShape" not in simple_schema.classes
    assert simple_schema.classes["User"].class_uri == "ex:User"


def test_property_shapes_become_attributes(simple_schema):
    """The whole point: an RDFS import of this file yields no attributes at all."""
    attributes = simple_schema.classes["User"].attributes
    assert {"schema1_name", "schema1_gender", "schema1_birthDate", "schema1_knows"} <= set(
        attributes
    )


def test_datatype_maps_to_a_linkml_type(simple_schema):
    attributes = simple_schema.classes["User"].attributes
    assert attributes["schema1_name"].range == "string"
    assert attributes["schema1_birthDate"].range == "date"


def test_sh_class_maps_to_a_class_range(simple_schema):
    assert simple_schema.classes["User"].attributes["schema1_knows"].range == "User"


def test_cardinality_is_translated(simple_schema):
    attributes = simple_schema.classes["User"].attributes
    # minCount 1 / maxCount 1
    assert attributes["schema1_name"].required
    assert not attributes["schema1_name"].multivalued
    # maxCount 1 only
    assert not attributes["schema1_birthDate"].required
    assert not attributes["schema1_birthDate"].multivalued
    # no counts at all
    assert attributes["schema1_knows"].multivalued


def test_identifier_is_opt_in(simple_schema):
    """SHACL has no identifier concept, so one is added only when asked for."""
    assert simple_schema.classes["User"].attributes["id"].identifier

    without = ShaclImportEngine().convert(
        SIMPLE, default_prefix="usr", model_uri="http://example.org/"
    )
    assert not any(
        slot.identifier for slot in without.classes["User"].attributes.values()
    )


def test_names_outside_the_schema_namespace_are_prefixed():
    """Terms from another namespace must not collide with the schema's own.

    Without this, a vocabulary that redeclares an imported name silently loses one
    of the two -- rdf:Property and ex:Property both localise to "Property".
    Declaring model_uri is what tells the importer which namespace is its own.
    """
    engine = ShaclImportEngine()
    schema = engine.convert(SIMPLE, default_prefix="usr")
    # No model_uri, so http://example.org/ is foreign and gets prefixed.
    assert "ex_User" in schema.classes

    engine = ShaclImportEngine()
    schema = engine.convert(SIMPLE, default_prefix="usr", model_uri="http://example.org/")
    assert "User" in schema.classes


def test_slot_uris_are_preserved(simple_schema):
    assert simple_schema.classes["User"].attributes["schema1_name"].slot_uri == (
        "schema1:name"
    )


def test_imported_schema_is_valid(simple_schema, tmp_path):
    """The emitted schema must load in LinkML, not merely serialise."""
    output = tmp_path / "schema.yaml"
    write_schema(simple_schema, str(output))
    view = SchemaView(str(output))
    assert view.get_class("User")
    assert [s.name for s in view.class_induced_slots("User")]


def test_writes_to_the_expected_output_path(simple_schema):
    write_schema(simple_schema, OUTSCHEMA)
    assert os.path.exists(OUTSCHEMA)


# ---------------------------------------------------------------------------
# Implicit-class shapes
# ---------------------------------------------------------------------------

IMPLICIT = os.path.join(INPUT_DIR, "shacl_implicit_class.ttl")


@pytest.fixture(scope="module")
def implicit_schema():
    """shacl_implicit_class.ttl: shapes that are themselves the classes."""
    return ShaclImportEngine().convert(
        IMPLICIT,
        default_prefix="ex",
        model_uri="http://example.org/",
        identifier="id",
        enum_root="ex:Enumeration",
    )


def test_shape_is_the_class_when_no_target_class(implicit_schema):
    assert {"Device", "Pump", "Port"} <= set(implicit_schema.classes)


def test_subclass_of_becomes_is_a(implicit_schema):
    assert implicit_schema.classes["Pump"].is_a == "Device"


def test_qualified_value_shape_supplies_the_range(implicit_schema):
    """Large ontologies express cardinality with qualified shapes, not min/maxCount."""
    assert implicit_schema.classes["Device"].attributes["hasPort"].range == "Port"


def test_disjoint_qualified_max_count_does_not_cap_the_slot(implicit_schema):
    """sh:qualifiedMaxCount bounds only values matching its nested shape.

    It caps the slot as a whole only when there is a single, non-disjoint
    qualified shape -- otherwise a property with two disjoint qualified shapes
    (at most one A *and* at most one B) would wrongly become single-valued.
    """
    assert implicit_schema.classes["Device"].attributes["hasPort"].multivalued


def test_inverse_path_becomes_its_own_slot(implicit_schema):
    """sh:inversePath states the triple on the other node."""
    attributes = implicit_schema.classes["Port"].attributes
    assert "inverseOf_hasPort" in attributes
    assert attributes["inverseOf_hasPort"].range == "Device"
    assert attributes["inverseOf_hasPort"].slot_uri == "ex:hasPort"


def test_sparql_only_shapes_do_not_become_slots(implicit_schema):
    """A shape carrying only sh:sparql states a rule, not a property.

    Emitting a slot for it invents an untyped attribute, which then shadows the
    real, typed one on every subclass.
    """
    assert "forbidden" not in implicit_schema.classes["Device"].attributes


def test_class_punned_enums_are_recovered(implicit_schema):
    """Enum members are rdfs:subClassOf their kind, never rdf:type instances.

    Querying instances finds nothing, so membership must come from the subclass
    closure.
    """
    assert "Medium" in implicit_schema.enums
    values = implicit_schema.enums["Medium"].permissible_values
    assert set(values) == {"Medium-Air", "Medium-Water"}
    assert values["Medium-Air"].meaning == "ex:Medium-Air"


def test_enum_members_are_not_also_emitted_as_classes(implicit_schema):
    assert "Medium_Air" not in implicit_schema.classes
    assert "Medium-Air" not in implicit_schema.classes


def test_a_slot_ranged_on_an_enum_names_the_enum(implicit_schema):
    assert implicit_schema.classes["Pump"].attributes["medium"].range == "Medium"


def test_implicit_schema_is_valid(implicit_schema, tmp_path):
    output = tmp_path / "implicit.yaml"
    write_schema(implicit_schema, str(output))
    view = SchemaView(str(output))
    assert view.get_class("Pump")
    # is_a inheritance must survive the round trip through YAML.
    assert "label" in {s.name for s in view.class_induced_slots("Pump")}


def test_mode_is_detected_by_majority():
    """A few sh:targetClass shapes must not flip an otherwise implicit graph.

    ASHRAE 223P carries 52 target-class shapes against 647 node shapes; treating
    it as target-class mode collapses nearly every class onto a few targets.
    """
    engine = ShaclImportEngine()
    engine.convert(IMPLICIT, default_prefix="ex")
    assert engine.use_target_class is False

    engine = ShaclImportEngine()
    engine.convert(SIMPLE, default_prefix="usr")
    assert engine.use_target_class is True
