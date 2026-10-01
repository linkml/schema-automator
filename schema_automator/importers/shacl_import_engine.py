"""Import a SHACL shapes graph as a LinkML schema.

SHACL expresses a data model the way LinkML does -- classes with typed,
cardinality-constrained slots -- but stores it in a shape graph rather than in
``rdfs:domain``/``rdfs:range``. That makes :class:`RdfsImportEngine` unable to see
it: an ontology whose properties live entirely in ``sh:property`` shapes imports as
a class hierarchy with no attributes.

Two conventions for relating shapes to classes are both supported, because real
vocabularies split between them:

*Explicit* -- a shape names the class it constrains, which is the style used by
DCAT-AP and by most hand-written shape files::

    ex:UserShape a sh:NodeShape ; sh:targetClass ex:User ;
        sh:property [ sh:path schema:name ; sh:datatype xsd:string ] .

*Implicit* -- the shape *is* the class, which is the style used by large published
ontologies such as ASHRAE 223P and Brick::

    s223:Equipment a rdfs:Class, sh:NodeShape ;
        rdfs:subClassOf s223:Connectable ;
        sh:property [ sh:path s223:hasProperty ; sh:class s223:Property ] .

*Split* -- one class's constraints spread over several shapes, and over several
files, which is the style used by the IEC/ENTSO-E CGMES conformity-assessment
shapes. A main shape carries the bulk, supplementary shapes add one constraint
each, and each profile restates the class::

    eq:Terminal a sh:NodeShape ; sh:targetClass cim:Terminal ;
        sh:property ido:IdentifiedObject.name-cardinality , ... .
    eq:Terminal.Node-valueTypeNodeShape a sh:NodeShape ; sh:targetClass cim:Terminal ;
        sh:property eq:Terminal.Node-valueType .

Shapes therefore merge rather than collide, in two tiers: within a file they are
conjunctive, across files the laxest bound wins -- see
:meth:`ShaclImportEngine.merge_classes`. Passing a directory to
:meth:`ShaclImportEngine.convert` loads every file into one graph, which is what
makes the second tier possible.

Limitations
-----------

A LinkML schema is a data model; a shapes graph is a validation program. The
overlap is large but proper, so an import is lossy by construction and does not
round-trip -- neither byte-for-byte nor shape-for-shape. What is dropped:

``sh:sparql`` constraints
    Nothing in LinkML corresponds. Some are ordinary predicates awkwardly
    expressed (a ``STRLEN`` bound is close to ``pattern``); most are genuinely
    beyond a schema. CGMES 3.0.2 carries 194 of them, and the majority are
    multi-hop invariants over several objects -- "this ACLineSegment has a
    different ``BaseVoltage.nominalVoltage`` at its two ends" traverses terminal
    to topological node to base voltage. A schema language cannot state that, and
    should not try.

    A related case is worth knowing about because it is a *source* defect rather
    than an expressiveness gap. Some published shapes encode exclusive-choice
    ("exactly one of these 13 associations") as a combinatorial
    ``BIND(EXISTS{...})`` filter over every pair -- 6 files in CGMES 3.0.2 use the
    pattern. Standard SHACL states the same thing as an ``sh:alternativePath``
    carrying ``sh:minCount``/``sh:maxCount``. ENTSO-E is correcting these upstream
    (entsoe/application-profiles-library#142). Supporting the corrected form is a
    bounded change to :meth:`ShaclImportEngine.visit_property_shape` -- an
    alternative path over N predicates is an ``any_of`` of N slots -- and is a
    better use of effort than parsing the SPARQL.

``sh:severity``, ``sh:message``, ``sh:name``, ``sh:order``, ``sh:group``
    Diagnostics and presentation. CGMES 3.0.2 attaches a message and a severity to
    all 8,738 of its constraints; they describe how a validator should report, not
    what the data is. ``rdfs:comment`` and ``sh:description`` are kept as
    ``description``.

Sequence and alternative property paths
    Skipped, with one exception: a two-step path ending in ``rdf:type`` is
    recognised as a value-type constraint, because it is the only way CGMES states
    the permitted classes of an association (see
    :meth:`ShaclImportEngine._value_type_path`). Longer sequences, general
    alternatives and ``sh:zeroOrMorePath`` have no LinkML equivalent.

Per-profile constraint variation
    Collapsed. Where profiles disagree on whether a property is required, the
    merge keeps the laxest bound, so the distinction between "Equipment requires
    ``ratedS``" and "SteadyStateHypothesis does not" is not recoverable from the
    output. Representing it would need a schema per profile.

Class hierarchy, when the shapes omit it
    Taken from ``rdfs:subClassOf`` where present, so 223P and Brick import with
    ``is_a`` intact. CGMES states no hierarchy in its shapes at all -- it lives in
    separate RDFS vocabulary files -- so that corpus imports flat, with inherited
    constraints repeated on each class as the shapes themselves repeat them.

Validation therefore stays with ``pyshacl`` against the original shapes graph. The
imported schema is for generation and documentation, not a replacement for it.

To do
-----

* No override for mode detection; a graph evenly split between explicit and
  implicit shapes is decided by a coin toss.
* ``sh:node`` is treated as a class range like ``sh:class``, which is right for the
  vocabularies tested but wrong in general -- it may name an arbitrary shape.
* ``sh:minInclusive``/``sh:maxInclusive`` are not read, though LinkML has
  ``minimum_value``/``maximum_value``. The clearest gap of the four: CGMES 3.0.2
  states 853 of them, all currently dropped.
* ``sh:pattern`` counts as substantive but is not carried onto the slot, though
  LinkML has ``pattern``.
* A directory is parsed with a single ``format``, so mixed serialisations need
  separate runs.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Iterable

from linkml_runtime.utils.schema_builder import SchemaBuilder
from linkml_runtime.linkml_model import (
    ClassDefinition,
    EnumDefinition,
    PermissibleValue,
    SchemaDefinition,
    SlotDefinition,
)
from rdflib import OWL, RDF, RDFS, SH, BNode, Graph, Literal, URIRef
from rdflib.term import Node

from schema_automator.importers.import_engine import ImportEngine

logger = logging.getLogger(__name__)

#: XSD datatypes mapped to LinkML built-in types.
TYPE_MAP = {
    "anyURI": "uri",
    "boolean": "boolean",
    "date": "date",
    "dateTime": "datetime",
    "decimal": "decimal",
    "double": "double",
    "float": "float",
    "int": "integer",
    "integer": "integer",
    "long": "integer",
    "string": "string",
    "time": "time",
}

#: Fallback range when a shape expresses no type at all.
DEFAULT_RANGE = "uriorcurie"

#: Predicates that always carry literals. Shapes frequently omit ``sh:datatype``
#: for these, and the fallback range would make prose fail URI validation.
LITERAL_PREDICATES = {
    RDFS.comment: "string",
    RDFS.label: "string",
}

#: Constraint components that give a shape substance beyond a SPARQL rule.
SUBSTANTIVE = (
    SH["class"],
    SH.node,
    SH.datatype,
    SH.qualifiedValueShape,
    SH["in"],
    SH["or"],
    SH.xone,
    SH.minCount,
    SH.maxCount,
    SH.qualifiedMinCount,
    SH.qualifiedMaxCount,
    SH.hasValue,
    SH.pattern,
)


#: Extensions treated as shapes files when loading a directory.
SHAPE_SUFFIXES = (".ttl", ".n3", ".nt", ".rdf", ".xml", ".owl", ".jsonld")


def _expand_sources(file: str) -> list[str]:
    """The shapes files *file* names: itself, or the contents of a directory.

    A directory is loaded into a single graph, which is what lets constraints for
    one class merge across files -- CGMES splits 301 of its 396 classes over
    several profile files, so importing them one at a time cannot see the whole
    class. Sorted so a run is reproducible, and non-shape files are skipped rather
    than handed to the parser.

    Every file in a directory is parsed with the same *format* as the caller
    passed, so a directory must hold one serialisation.
    """
    path = Path(file)
    if not path.is_dir():
        return [file]
    sources = sorted(
        str(child)
        for child in path.rglob("*")
        if child.is_file() and child.suffix.lower() in SHAPE_SUFFIXES
    )
    if not sources:
        raise ValueError(f"no shapes files found in {file}")
    logger.info("loading %d shapes file(s) from %s", len(sources), file)
    return sources


def _local_name(term: Node) -> str:
    """Last path or fragment component of a URI."""
    text = str(term)
    for separator in ("#", "/"):
        if separator in text:
            tail = text.rsplit(separator, 1)[-1]
            if tail:
                return tail
    return text


@dataclass
class ShaclImportEngine(ImportEngine):
    """An ImportEngine that converts a SHACL shapes graph to LinkML."""

    sb: SchemaBuilder = field(default_factory=lambda: SchemaBuilder())

    #: Set when the shapes graph uses ``sh:targetClass``; controls whether a shape
    #: or its target becomes the class.
    use_target_class: bool = False

    #: Namespace of the schema being imported. Names outside it are prefixed so
    #: that, for example, ``rdf:Property`` cannot collide with ``ex:Property``.
    default_namespace: str | None = None

    graph: Graph = field(default_factory=Graph)

    _prefixes: dict[str, str] = field(default_factory=dict)
    #: Source file each node shape was first seen in; see :meth:`_profile_of`.
    _profiles: dict[Node, str] = field(default_factory=dict)
    _enums: dict[URIRef, str] = field(default_factory=dict)

    # ------------------------------------------------------------------ naming

    def element_name(self, term: Node) -> str:
        """A LinkML element name for *term*, unique across namespaces.

        Terms from a namespace other than the schema's own are prefixed. Without
        this, a vocabulary that redeclares an imported name silently loses one of
        the two: ``rdf:Property`` and ``s223:Property`` both localise to
        ``Property``, and whichever is visited last wins.
        """
        name = _local_name(term)
        text = str(term)
        if self.default_namespace and not text.startswith(self.default_namespace):
            for prefix, namespace in self._prefixes.items():
                if text.startswith(namespace) and prefix:
                    return f"{prefix}_{name}"
        return name

    def class_name(self, term: Node) -> str:
        """A LinkML *class* name, which must also be a valid identifier.

        Hyphens are legal in a permissible value but not in a generated class, so
        they are replaced here and kept in :meth:`element_name`.
        """
        return self.element_name(term).replace("-", "_")

    def curie(self, term: Node) -> str:
        """*term* shortened against the graph's own prefixes, if possible."""
        text = str(term)
        for prefix, namespace in self._prefixes.items():
            if prefix and text.startswith(namespace):
                return f"{prefix}:{text[len(namespace):]}"
        return text

    # ------------------------------------------------------------------ shapes

    def _detect_target_class_mode(self) -> bool:
        """Decide whether shapes are declared separately from their classes.

        Decided by majority rather than by presence: a vocabulary can be
        overwhelmingly implicit and still carry a few ``sh:targetClass`` shapes for
        supplementary constraints on classes defined elsewhere. ASHRAE 223P has 52
        such shapes against 647 node shapes, and treating it as target-class mode
        collapses nearly every class onto a handful of targets.
        """
        shapes = [s for s in set(self.graph.subjects(RDF.type, SH.NodeShape))
                  if isinstance(s, URIRef)]
        if not shapes:
            return False
        targeted = sum(
            1 for shape in shapes if self.graph.value(shape, SH.targetClass) is not None
        )
        return targeted * 2 > len(shapes)

    def node_shapes(self) -> list[URIRef]:
        """Named node shapes, excluding anything that is only an enum member."""
        return sorted(
            (
                shape
                for shape in set(self.graph.subjects(RDF.type, SH.NodeShape))
                if isinstance(shape, URIRef) and shape not in self._enums
            ),
            key=str,
        )

    def visit_shape(self, shape: URIRef) -> ClassDefinition:
        """Convert one node shape into a class definition.

        In target-class mode the shape describes some other class, so the target
        supplies the name and URI; otherwise the shape is the class.
        """
        target = self.graph.value(shape, SH.targetClass)
        subject = target if (self.use_target_class and target is not None) else shape

        parents = [
            self.class_name(parent)
            for parent in self.graph.objects(subject, RDFS.subClassOf)
            if isinstance(parent, URIRef) and parent != OWL.Thing
        ]
        cls = ClassDefinition(
            name=self.class_name(subject),
            class_uri=self.curie(subject),
            description=self._comment(subject) or self._comment(shape),
            # LinkML allows a single is_a; further parents become mixins.
            is_a=parents[0] if parents else None,
            mixins=parents[1:],
        )
        for slot in self.visit_property_shapes(shape):
            existing = cls.attributes.get(slot.name)
            cls.attributes[slot.name] = (
                self.merge_slots(existing, slot) if existing else slot
            )
        return cls

    def visit_property_shapes(self, shape: URIRef) -> Iterable[SlotDefinition]:
        """Yield a slot for each usable ``sh:property`` of *shape*."""
        for property_shape in self.graph.objects(shape, SH.property):
            slot = self.visit_property_shape(property_shape)
            if slot is not None:
                yield slot

    def visit_property_shape(self, property_shape: Node) -> SlotDefinition | None:
        """Convert one property shape to a slot, or None if it carries no data."""
        path = self.graph.value(property_shape, SH.path)
        if path is None:
            return None

        inverse = None
        value_type_of = None
        if isinstance(path, BNode):
            inverse = self.graph.value(path, SH.inversePath)
            if inverse is None:
                value_type_of = self._value_type_path(path)
            if inverse is None and value_type_of is None:
                # Other sequence and alternative paths have no LinkML equivalent.
                logger.debug("skipping complex property path on %s", property_shape)
                return None

        if value_type_of is not None:
            # A value-type shape states the range of the property it follows, so it
            # merges into that property's slot rather than becoming one of its own.
            path = value_type_of

        if not self._is_substantive(property_shape):
            # A shape with only sh:sparql states a rule, not a property.
            logger.debug("skipping SPARQL-only shape for %s", path)
            return None

        predicate = inverse if inverse is not None else path
        name = self.element_name(predicate)
        if inverse is not None:
            name = f"inverseOf_{name}"

        slot = SlotDefinition(
            name=name,
            slot_uri=self.curie(predicate),
            description=self._comment(property_shape),
        )
        if inverse is not None:
            slot.annotations["inverse_of"] = self.element_name(inverse)
        self.apply_range(
            property_shape, path, slot, value_type=value_type_of is not None
        )
        if value_type_of is None:
            # A value-type shape's counts bound the rdf:type hop, not the property;
            # the sibling *-cardinality shape carries the property's own bounds.
            self.apply_cardinality(property_shape, slot)
        return slot

    def _value_type_path(self, path: BNode) -> URIRef | None:
        """The property a ``(property rdf:type)`` value-type path constrains.

        CGMES states the class of an association's target with a two-step sequence
        path ending in ``rdf:type``, listing the permitted classes in ``sh:in``::

            sh:path ( cim:Terminal.TopologicalNode rdf:type ) ;
            sh:in   ( cim:TopologicalNode ) .

        This is the only place CGMES records association ranges, so skipping it as
        an unmappable complex path leaves every association untyped. Returns None
        for any other sequence path, which stays unmapped.
        """
        items = list(self.graph.items(path))
        if len(items) != 2 or items[-1] != RDF.type:
            return None
        return items[0] if isinstance(items[0], URIRef) else None

    # ------------------------------------------------------------------ ranges

    def apply_range(
        self,
        property_shape: Node,
        path: Node,
        slot: SlotDefinition,
        value_type: bool = False,
    ) -> None:
        """Set ``range`` or ``any_of`` from the shape's type constraints.

        When *value_type* is set the shape reached its target through a
        ``(property rdf:type)`` path, so its ``sh:in`` list names classes rather
        than literal values.
        """
        if isinstance(path, URIRef) and path in LITERAL_PREDICATES:
            slot.range = LITERAL_PREDICATES[path]
            return

        target = self.graph.value(property_shape, SH["class"]) or self.graph.value(
            property_shape, SH.node
        )
        if target is None:
            # sh:qualifiedValueShape nests the type inside another shape.
            qualified = self.graph.value(property_shape, SH.qualifiedValueShape)
            if qualified is not None:
                target = self.graph.value(qualified, SH["class"]) or self.graph.value(
                    qualified, SH.node
                )
        if isinstance(target, URIRef):
            slot.range = self.range_for(target)
            return

        datatype = self.graph.value(property_shape, SH.datatype)
        if datatype is not None:
            slot.range = TYPE_MAP.get(_local_name(datatype), "string")
            return

        for operator in (SH["or"], SH.xone):
            collection = self.graph.value(property_shape, operator)
            if collection is None:
                continue
            options = list(self._union_members(collection))
            if len(options) > 1:
                slot.any_of = [{"range": option} for option in options]
                return
            if options:
                slot.range = options[0]
                return

        collection = self.graph.value(property_shape, SH["in"])
        if collection is not None:
            if value_type:
                # Here sh:in lists the permitted classes of the association, so it
                # is a range (or a union of them), not a set of literal values.
                options = [
                    self.range_for(member)
                    for member in self.graph.items(collection)
                    if isinstance(member, URIRef)
                ]
                if len(options) > 1:
                    slot.any_of = [{"range": option} for option in options]
                    return
                if options:
                    slot.range = options[0]
                    return
            else:
                # An inline sh:in list becomes an enum on the slot itself.
                slot.range = self.visit_inline_enum(property_shape, slot)
                return

        # Deliberately left unset rather than defaulted: several shapes may
        # describe one property, and a premature default would win the merge.
        slot.range = None

    def _union_members(self, collection: Node) -> Iterable[str]:
        """Ranges named by the members of an ``sh:or``/``sh:xone`` list."""
        for member in self.graph.items(collection):
            target = self.graph.value(member, SH["class"]) or self.graph.value(
                member, SH.node
            )
            if isinstance(target, URIRef):
                yield self.range_for(target)
                continue
            datatype = self.graph.value(member, SH.datatype)
            if datatype is not None:
                yield TYPE_MAP.get(_local_name(datatype), "string")

    def range_for(self, target: URIRef) -> str:
        """The LinkML range naming *target*: an enum, a class, or a built-in."""
        if target in self._enums:
            return self._enums[target]
        return self.class_name(target)

    def visit_inline_enum(self, property_shape: Node, slot: SlotDefinition) -> str:
        """Turn an ``sh:in`` list into an enum named after the slot.

        One property shape is often shared by many node shapes -- CGMES declares
        ``Measurement.phases-datatype`` once and references it from Analog,
        Discrete, Accumulator and StringMeasurement -- so the same enum is reached
        repeatedly. Registering it again raises a duplicate-name error, and the
        second registration would be identical anyway, so the enum is built once
        and reused.
        """
        name = f"{slot.name}_enum"
        if name in self.sb.schema.enums:
            return name
        enum = EnumDefinition(name=name)
        for member in self.graph.items(self.graph.value(property_shape, SH["in"])):
            text = str(member) if isinstance(member, Literal) else _local_name(member)
            value = PermissibleValue(text=text)
            if isinstance(member, URIRef):
                value.meaning = self.curie(member)
            enum.permissible_values[text] = value
        self.sb.add_enum(enum)
        return name

    # ------------------------------------------------------------- cardinality

    def apply_cardinality(self, property_shape: Node, slot: SlotDefinition) -> None:
        """Set ``required`` and ``multivalued`` from the shape's counts."""
        minimum = self.graph.value(property_shape, SH.minCount)
        if minimum is not None and int(minimum) >= 1:
            slot.required = True

        maximum = self.graph.value(property_shape, SH.maxCount)
        if maximum is None:
            # sh:qualifiedMaxCount bounds only the values matching its nested
            # shape, so it caps the slot as a whole only when there is exactly one
            # such shape and they are not declared disjoint.
            qualified = list(self.graph.objects(property_shape, SH.qualifiedValueShape))
            disjoint = self.graph.value(property_shape, SH.qualifiedValueShapesDisjoint)
            if len(qualified) == 1 and not disjoint:
                maximum = self.graph.value(property_shape, SH.qualifiedMaxCount)
        slot.multivalued = not (maximum is not None and int(maximum) == 1)

    def merge_classes(
        self,
        existing: ClassDefinition,
        addition: ClassDefinition,
        across_profiles: bool,
    ) -> ClassDefinition:
        """Fold two node shapes that constrain the same class into one.

        Several shapes may target one class -- CGMES splits a class's constraints
        across a main shape and supplementary ``*-valueTypeNodeShape`` shapes, and
        does so again across profile files. Adding each as its own class raises a
        duplicate-name error, so shapes accumulate here the way
        :meth:`merge_slots` accumulates property shapes.

        *across_profiles* says which boundary is being crossed. Within a profile
        the shapes are conjunctive and ``required`` accumulates: a supplementary
        ``*-valueTypeNodeShape`` carries one property and says nothing about the
        rest, so its silence must not relax them. Across profiles the laxest bound
        wins, and a property a profile omits entirely is the laxest case of all --
        CGMES requires ``RotatingMachine.ratedS`` in Equipment but not in
        SteadyStateHypothesis, and demanding it everywhere would reject a valid SSH
        file. See :meth:`merge_slots`.
        """
        existing.description = existing.description or addition.description
        existing.is_a = existing.is_a or addition.is_a
        for mixin in addition.mixins or []:
            if mixin != existing.is_a and mixin not in existing.mixins:
                existing.mixins.append(mixin)
        for name, slot in addition.attributes.items():
            present = existing.attributes.get(name)
            if present is None:
                if across_profiles:
                    slot.required = False
                existing.attributes[name] = slot
            else:
                existing.attributes[name] = self.merge_slots(
                    present, slot, across_shapes=across_profiles
                )
        if across_profiles:
            for name, slot in existing.attributes.items():
                if name not in addition.attributes:
                    slot.required = False
        return existing

    def merge_slots(
        self,
        existing: SlotDefinition,
        addition: SlotDefinition,
        across_shapes: bool = False,
    ) -> SlotDefinition:
        """Fold two shapes for the same path into one slot.

        Shape graphs routinely split a property across several shapes -- one
        carrying the range, another the cardinality, others pure SPARQL rules --
        so shapes must accumulate. A concrete range always beats the fallback,
        whichever shape happened to be visited first.

        ``required`` depends on where the two shapes met, which is what
        *across_shapes* distinguishes. Within one node shape SHACL constraints are
        conjunctive, so any shape demanding the property makes it required. Across
        node shapes -- separate profiles constraining the same class -- the laxest
        bound wins instead: CGMES requires ``RotatingMachine.ratedS`` in Equipment
        but not in ShortCircuit or SteadyStateHypothesis, and unioning would reject
        a valid SSH file for omitting it. ``multivalued`` takes the strictest bound
        either way, because an upper bound holds wherever it is stated.
        """
        # A union range supersedes a scalar one: the scalar came from a shape naming
        # a single class, and a slot cannot state both a range and a union of ranges.
        existing.any_of = existing.any_of or addition.any_of
        if existing.any_of:
            existing.range = None
        elif existing.range in (None, DEFAULT_RANGE):
            existing.range = addition.range or existing.range
        existing.required = (
            bool(existing.required and addition.required)
            if across_shapes
            else bool(existing.required or addition.required)
        )
        existing.multivalued = bool(existing.multivalued and addition.multivalued)
        existing.description = existing.description or addition.description
        return existing

    # ------------------------------------------------------------------- enums

    def collect_enums(self, root: URIRef) -> None:
        """Register enums for the subclass tree beneath *root*.

        Published ontologies model enumerations by punning class and instance: a
        member is ``rdfs:subClassOf`` its kind and typed as itself, never an
        ``rdf:type`` instance of the kind. Membership therefore comes from the
        subclass closure -- querying instances finds nothing.
        """
        children: dict[Node, set[URIRef]] = {}
        for subject, _, parent in self.graph.triples((None, RDFS.subClassOf, None)):
            if isinstance(subject, URIRef):
                children.setdefault(parent, set()).add(subject)

        def descendants(node: Node) -> set[URIRef]:
            seen: set[URIRef] = set()
            frontier = [node]
            while frontier:
                for child in children.get(frontier.pop(), ()):
                    if child not in seen:
                        seen.add(child)
                        frontier.append(child)
            return seen

        for kind in sorted(children.get(root, ()), key=str):
            members = descendants(kind)
            if not members:
                continue
            enum = EnumDefinition(
                name=self.class_name(kind),
                enum_uri=self.curie(kind),
                description=self._comment(kind),
            )
            for member in sorted(members, key=str):
                text = self.element_name(member)
                enum.permissible_values[text] = PermissibleValue(
                    text=text,
                    meaning=self.curie(member),
                    description=self._comment(member),
                )
            self.sb.add_enum(enum)
            self._enums[kind] = enum.name
            for member in members:
                self._enums[member] = enum.name

    # ------------------------------------------------------------------- utils

    def _profile_of(self, shape: Node) -> str:
        """The file *shape* came from, which is the profile boundary.

        CGMES publishes one file per profile, and a class's shapes within a file --
        a main shape plus supplementary ``*-valueTypeNodeShape`` shapes -- jointly
        describe it. The file is therefore the unit across which a missing property
        means "this profile does not constrain it" rather than "this shape happens
        not to mention it".
        """
        return self._profiles.get(shape, "")

    def _comment(self, subject: Node) -> str | None:
        value = self.graph.value(subject, RDFS.comment)
        return str(value).strip() if isinstance(value, Literal) else None

    def _is_substantive(self, property_shape: Node) -> bool:
        """True unless the shape's only content is a SPARQL constraint."""
        if self.graph.value(property_shape, SH.sparql) is None:
            return True
        return any(
            self.graph.value(property_shape, component) is not None
            for component in SUBSTANTIVE
        )

    def prune_dangling_ranges(self) -> list[str]:
        """Replace ranges that name nothing the schema defines.

        A range pointing at an undefined element makes the emitted schema fail
        LinkML validation, so those degrade to ``uriorcurie``.
        """
        schema = self.sb.schema
        known = set(schema.classes) | set(schema.enums) | set(TYPE_MAP.values())
        known |= {DEFAULT_RANGE, "uri", "string"}
        dangling: set[str] = set()
        for cls in schema.classes.values():
            for slot in cls.attributes.values():
                kept = [
                    option
                    for option in (slot.any_of or [])
                    if _option_range(option) in known
                ]
                if slot.any_of and len(kept) != len(slot.any_of):
                    dangling.update(
                        str(_option_range(o)) for o in slot.any_of if o not in kept
                    )
                    slot.any_of = kept
                if slot.any_of:
                    # A union range and a scalar one are mutually exclusive, and
                    # the union is the more specific of the two.
                    slot.range = None
                    continue
                if slot.range is None:
                    slot.range = DEFAULT_RANGE
                elif slot.range not in known:
                    dangling.add(slot.range)
                    slot.range = DEFAULT_RANGE
        return sorted(dangling)

    def inherit_constraints(self) -> int:
        """Tighten a slot to match the strictest definition it inherits.

        SHACL constraints are conjunctive: a subclass shape adds to its parent's
        rather than replacing it. A subclass that redeclares a path without a
        count therefore still inherits the parent's ``sh:maxCount``, and every
        ancestor matters -- not only the nearest, since an intervening class may
        redeclare the path with no count of its own.
        """
        schema = self.sb.schema
        narrowed = 0

        def ancestors(name: str) -> Iterable[ClassDefinition]:
            seen = {name}
            pending = list(_parents(schema.classes.get(name)))
            while pending:
                parent_name = pending.pop(0)
                if parent_name in seen or parent_name not in schema.classes:
                    continue
                seen.add(parent_name)
                parent = schema.classes[parent_name]
                yield parent
                pending.extend(_parents(parent))

        for name, cls in schema.classes.items():
            for slot_name, slot in cls.attributes.items():
                inherited = [
                    parent.attributes[slot_name]
                    for parent in ancestors(name)
                    if slot_name in parent.attributes
                ]
                if not inherited:
                    continue
                if slot.multivalued and any(not other.multivalued for other in inherited):
                    slot.multivalued = False
                    narrowed += 1
                if slot.range in (None, DEFAULT_RANGE):
                    for other in inherited:
                        if other.range not in (None, DEFAULT_RANGE):
                            slot.range = other.range
                            break
        return narrowed

    # ----------------------------------------------------------------- convert

    def convert(
        self,
        file: str,
        name: str | None = None,
        format: str = "turtle",
        default_prefix: str | None = None,
        model_uri: str | None = None,
        identifier: str | None = None,
        enum_root: str | None = None,
        **kwargs: Any,
    ) -> SchemaDefinition:
        """Convert a SHACL shapes file to a LinkML schema.

        Args:
            file: Path or URL of the shapes graph, or a directory of them.
                A directory loads every shapes file inside it into one graph,
                which is what lets constraints for a class that are split across
                several files merge into a single class.
            name: Schema name; defaults to *default_prefix*, else ``example``.
            format: rdflib parser name.
            default_prefix: Prefix treated as the schema's own namespace.
            model_uri: URI for *default_prefix* when the graph does not declare it.
            identifier: Name of an identifier slot to add to root classes. SHACL
                has no identifier concept, so this is opt-in.
            enum_root: Class whose subclass tree is imported as enumerations, for
                ontologies that pun class and instance to model enums.
        """
        self.graph = Graph()
        self._profiles = {}
        for source in _expand_sources(file):
            before = set(self.graph.subjects(RDF.type, SH.NodeShape))
            self.graph.parse(source, format=format)
            for shape in set(self.graph.subjects(RDF.type, SH.NodeShape)) - before:
                self._profiles[shape] = source
        self._prefixes = {
            str(prefix): str(namespace) for prefix, namespace in self.graph.namespaces()
        }

        name = name or default_prefix or "example"
        self.sb = SchemaBuilder(name=name)
        self.sb.add_defaults()
        schema = self.sb.schema
        for prefix, namespace in self._prefixes.items():
            if prefix == "schema" and namespace != "http://schema.org/":
                continue
            self.sb.add_prefix(prefix, namespace, replace_if_present=True)
        if default_prefix is not None:
            schema.default_prefix = default_prefix
            if model_uri is not None:
                self.sb.add_prefix(default_prefix, model_uri, replace_if_present=True)
            if default_prefix in schema.prefixes:
                schema.id = schema.prefixes[default_prefix].prefix_reference
                self.default_namespace = str(schema.id)

        self.use_target_class = self._detect_target_class_mode()
        logger.info(
            "importing %d node shape(s) in %s mode",
            len(self.node_shapes()),
            "target-class" if self.use_target_class else "implicit-class",
        )

        if enum_root is not None:
            self.collect_enums(URIRef(self._expand(enum_root)))

        # Two tiers, because the two levels carry different meaning. Shapes within
        # one profile are conjunctive -- a main shape plus its supplementary
        # value-type shapes jointly describe the class. Separate profiles are
        # separate documents, and a property one profile omits is optional there.
        per_profile: dict[str, dict[str, ClassDefinition]] = {}
        for shape in self.node_shapes():
            cls = self.visit_shape(shape)
            profile = per_profile.setdefault(self._profile_of(shape), {})
            existing = profile.get(cls.name)
            profile[cls.name] = (
                self.merge_classes(existing, cls, across_profiles=False)
                if existing
                else cls
            )
        classes: dict[str, ClassDefinition] = {}
        for profile in per_profile.values():
            for name, cls in profile.items():
                existing = classes.get(name)
                classes[name] = (
                    self.merge_classes(existing, cls, across_profiles=True)
                    if existing
                    else cls
                )
        for cls in classes.values():
            self.sb.add_class(cls)

        narrowed = self.inherit_constraints()
        dangling = self.prune_dangling_ranges()
        if narrowed:
            logger.info("narrowed %d slot(s) to an inherited constraint", narrowed)
        if dangling:
            logger.warning(
                "%d range(s) named no known element and became %s: %s",
                len(dangling),
                DEFAULT_RANGE,
                ", ".join(dangling[:10]),
            )

        if identifier is not None:
            self._add_identifier(identifier)
        return schema

    def _expand(self, curie_or_uri: str) -> str:
        prefix, separator, local = curie_or_uri.partition(":")
        if separator and prefix in self._prefixes:
            return self._prefixes[prefix] + local
        return curie_or_uri

    def _add_identifier(self, identifier: str) -> None:
        """Add an identifier slot to every root class.

        SHACL models no notion of identity, but LinkML classes need a key to be
        addressable. Declared on roots only, so subclasses inherit it.
        """
        schema = self.sb.schema
        for cls in schema.classes.values():
            if cls.is_a or cls.mixins or identifier in cls.attributes:
                continue
            cls.attributes[identifier] = SlotDefinition(
                name=identifier,
                identifier=True,
                range="uriorcurie",
                description="Identifier of this node, not modelled by SHACL.",
            )


def _option_range(option: Any) -> Any:
    """Range of an ``any_of`` member, whether a dict or a slot expression."""
    if isinstance(option, dict):
        return option.get("range")
    return getattr(option, "range", None)


def _parents(cls: ClassDefinition | None) -> list[str]:
    if cls is None:
        return []
    return [name for name in [cls.is_a, *(cls.mixins or [])] if name]
