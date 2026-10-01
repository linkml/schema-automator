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


# ---------------------------------------------------------------------------
# Shapes split across node shapes and files
# ---------------------------------------------------------------------------
#
# The CGMES conformity-assessment shapes are built this way: a class's
# constraints are spread over a main node shape plus supplementary
# ``*-valueTypeNodeShape`` shapes, and spread again over one file per profile
# (301 of its 396 classes appear in more than one file). Importing a single file
# therefore cannot see a whole class, and importing shapes one-per-class raises a
# duplicate-name error.

SPLIT = os.path.join(INPUT_DIR, "shacl_split_profiles")


@pytest.fixture(scope="module")
def split_schema():
    """A directory of two profiles that both constrain ex:Terminal."""
    return ShaclImportEngine().convert(
        SPLIT, default_prefix="ex", model_uri="http://example.org/"
    )


def test_a_directory_loads_every_file_into_one_graph(split_schema):
    assert {"Terminal", "Equipment", "TopologicalNode"} <= set(split_schema.classes)


def test_shapes_for_one_class_merge_instead_of_colliding(split_schema):
    """Three node shapes target ex:Terminal; adding each as a class would raise.

    The merged class must carry the union of their properties -- ``ratedS`` from
    profile_a's main shape, ``node`` from its supplementary value-type shape, and
    ``equip`` from profile_b.
    """
    attributes = split_schema.classes["Terminal"].attributes
    assert {"name", "ratedS", "node", "equip"} <= set(attributes)


def test_required_relaxes_to_the_laxest_profile(split_schema):
    """A property required by one profile but absent from another is optional.

    CGMES requires ``RotatingMachine.ratedS`` in Equipment but not in
    ShortCircuit or SteadyStateHypothesis. Unioning ``required`` across profiles
    would reject a valid file of the laxer profile for omitting it.
    """
    assert not split_schema.classes["Terminal"].attributes["ratedS"].required


def test_required_still_holds_when_every_profile_agrees(split_schema):
    """Relaxing across profiles must not discard a constraint they all state."""
    assert split_schema.classes["Terminal"].attributes["name"].required


def test_value_type_sequence_path_becomes_a_range(split_schema):
    """``sh:path ( ex:node rdf:type )`` with ``sh:in`` states a range.

    This is the only way the CGMES corpus records the permitted classes of an
    association; skipping it as an unmappable complex path leaves every
    association untyped.
    """
    assert split_schema.classes["Terminal"].attributes["node"].range == (
        "TopologicalNode"
    )


def test_multi_member_value_type_becomes_a_union(split_schema):
    """Several permitted classes are a union of ranges, not an enum of values."""
    slot = split_schema.classes["Terminal"].attributes["equip"]
    assert {option["range"] for option in slot.any_of} == {
        "Equipment",
        "TopologicalNode",
    }


def test_a_union_range_does_not_also_carry_a_scalar_range(split_schema):
    """``range`` and ``any_of`` are mutually exclusive; the union is the specific one."""
    assert not split_schema.classes["Terminal"].attributes["equip"].range


def test_a_value_type_shape_does_not_impose_cardinality(split_schema):
    """Its counts bound the rdf:type hop, not the property.

    The sibling ``*-cardinality`` shape carries the property's own bounds.
    """
    assert not split_schema.classes["Terminal"].attributes["node"].required


def test_a_shared_sh_in_shape_registers_its_enum_once(split_schema):
    """One property shape is reached through many node shapes.

    CGMES declares ``Measurement.phases-datatype`` once and references it from
    Analog, Discrete, Accumulator and StringMeasurement; registering its enum
    per reference raises a duplicate-name error.
    """
    assert "kind_enum" in split_schema.enums
    assert set(split_schema.enums["kind_enum"].permissible_values) == {"a", "b"}
    assert split_schema.classes["Equipment"].attributes["kind"].range == "kind_enum"


def test_split_schema_is_valid(split_schema, tmp_path):
    output = tmp_path / "split.yaml"
    write_schema(split_schema, str(output))
    view = SchemaView(str(output))
    assert view.get_class("Terminal")
    assert [s.name for s in view.class_induced_slots("Terminal")]
