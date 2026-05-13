"""Schema-driven XML loader for LinkML.

Loads an XML document into instances of a LinkML class, using the
LinkML schema to drive element/attribute/text mapping.

This is an upstream candidate for ``linkml_runtime.loaders``. It lives
in schema-automator while the design stabilizes against real-world
XML formats (currently dbGaP variable digest XML; planned: EML). When
the API is stable and the upstream linkml team accepts the proposal,
this module moves to ``linkml_runtime.loaders.xml_loader`` and the
import paths in schema-automator swap.

Mapping conventions
-------------------

The loader uses LinkML's ``annotations`` mechanism (no new metamodel
concepts) to direct how XML structure maps to LinkML slots:

- **Default**: a slot is populated from a child element whose tag
  matches the slot name.
- **``annotations.xml_element``**: override the element name for the
  slot (e.g., a slot ``reported_type`` populated from ``<type>``).
  Also valid as a *class-level* annotation, declaring the XML element
  name the class corresponds to (used for root-tag validation).
- **``annotations.xml_attribute``**: ``true`` means the slot is
  populated from the parent element's XML attribute of the same name.
  A string value (e.g., ``xml_attribute: code``) names the attribute
  explicitly.
- **``annotations.xml_text``**: ``true`` means the slot is populated
  from the parent element's text content.
- **``annotations.xml_path``**: a slash-separated traversal expression
  for slots whose source is nested deeper than direct children. Form:
  ``elem/subelem/.../@attr`` (the trailing ``@attr`` indicates an
  attribute on the leaf element; without it, the leaf's text content
  is used). Used for cases like dbGaP's
  ``<variable><total><stats><stat min="..."/></stats></total></variable>``.
- **Repeated child elements** populate multivalued slots automatically.
- **Nested classes**: when a slot's range is a class in the schema,
  the child element is recursed into following the same conventions.

Namespaces
----------

XML namespaces (``<eml:dataTable xmlns:eml="...">``) are handled by
*local-name matching*: the loader strips the ``{namespace}`` prefix
that ElementTree adds and matches against slot annotations using the
local name. This means schema authors don't need to declare prefixes
to parse namespaced XML; ``xml_element: dataTable`` will match
``<eml:dataTable>`` and ``<dataTable>`` equally. The same applies to
attribute names (so ``xsi:type`` matches a slot annotated as
``xml_attribute: type``).

For documents using multiple namespaces with colliding local names,
this loose matching is ambiguous. That case isn't supported in v1;
schema authors should rename slots to disambiguate if it arises.

Strict mode
-----------

By default, XML elements and attributes that don't match any schema
slot are silently skipped (with a debug log). Pass ``strict=True`` to
collect all such issues and raise an aggregating ``XMLLoadErrors``
exception at the end. Errors carry path context so users can locate
the issue in the source. Strict mode is the right choice in CI, in
input validation pipelines, and when iterating on a new schema's
annotations.

Out of scope for v1
-------------------

- Full XPath in ``xml_path``: only ``/`` step traversal and a trailing
  ``/@attr`` are supported. Predicates (``[1]``), wildcards (``*``),
  and other XPath features behave per ElementTree's default
  ``Element.find`` semantics — undefined for special characters; treat
  as plain-step names only.
- Mixed content (text interleaved with elements).
- Processing instructions, comments, DTD entities (ElementTree drops
  these transparently).
- ``xsi:type`` polymorphism (choosing which LinkML class to recurse
  into based on a runtime type tag). Tackle when the first consumer
  needs it.
- A fail-fast variant of strict mode. The current ``strict=True``
  always collects all errors and raises at end; a ``fail_fast=True``
  sub-flag is deferred until gigabyte-scale documents surface the
  need.

These are noted because real-world XML uses them; explicit deferral
is honest scoping rather than promised support.
"""

from __future__ import annotations

import logging
from functools import lru_cache
from pathlib import Path
from typing import TYPE_CHECKING, Any, Optional, TextIO, Union

from defusedxml import ElementTree as ET

from linkml_runtime.loaders.loader_root import Loader
from linkml_runtime.utils.schemaview import SchemaView

if TYPE_CHECKING:
    # These are transitive (via linkml-runtime) and only used in type
    # hints; importing under TYPE_CHECKING keeps deptry happy without
    # pulling them into our direct dep list.
    from hbreader import FileInfo
    from pydantic import BaseModel
    from linkml_runtime.utils.yamlutils import YAMLRoot

logger = logging.getLogger(__name__)


# ----------------------------------------------------------------------
# Annotation helpers
# ----------------------------------------------------------------------


def _annotation_value(definition, key: str) -> Optional[Union[bool, str]]:
    """Read an annotation value off a slot or class, normalizing forms.

    LinkML's induced-slot/class annotations are a ``JsonObj``
    (attribute-style access, ``in`` membership, ``__getitem__``), not a
    plain dict. Each entry is an ``Annotation`` object with a ``.value``
    field. This helper hides the access pattern.
    """
    anns = getattr(definition, "annotations", None)
    if anns is None:
        return None
    try:
        if key not in anns:
            return None
        ann = anns[key]
    except (TypeError, KeyError):
        return None
    return getattr(ann, "value", ann)


# ----------------------------------------------------------------------
# Strict-mode error collection
# ----------------------------------------------------------------------


class XMLLoadErrors(Exception):
    """Aggregating exception raised by ``XMLLoader`` in strict mode.

    Contains one or more error messages collected during a single load
    call. Each message is path-prefixed so the source location is
    identifiable. Access the raw list via the ``errors`` attribute.
    """

    def __init__(self, errors: list[str]) -> None:
        self.errors: list[str] = list(errors)
        plural = "" if len(self.errors) == 1 else "s"
        summary = "\n".join(f"  - {e}" for e in self.errors)
        super().__init__(
            f"{len(self.errors)} XML load error{plural}:\n{summary}"
        )


class _ErrorCollector:
    """Accumulates XML load errors during a single ``load`` call.

    Path context is maintained as a stack: callers ``push`` an element
    tag when recursing into it and ``pop`` on return. Error messages
    are prefixed with the current path so users can locate the issue.

    Lives at the top of the loop structure; threaded through recursion.
    Single-use per ``load`` call (not thread-safe by design — start a
    fresh collector per call).
    """

    def __init__(self) -> None:
        self.errors: list[str] = []
        self._path: list[str] = []

    def push(self, tag: str) -> None:
        self._path.append(tag)

    def pop(self) -> None:
        if self._path:
            self._path.pop()

    @property
    def path(self) -> str:
        return "/" + "/".join(self._path) if self._path else "/"

    def add_unknown_element(self, tag: str, class_name: str) -> None:
        self.errors.append(
            f"{self.path}: unknown element <{tag}> "
            f"(no matching slot in class {class_name!r})"
        )

    def add_unknown_attribute(
        self, attr_name: str, tag: str, class_name: str
    ) -> None:
        self.errors.append(
            f"{self.path}: unknown attribute {attr_name!r} on <{tag}> "
            f"(no matching slot in class {class_name!r})"
        )

    def add_root_mismatch(
        self, expected: str, actual: str, class_name: str
    ) -> None:
        self.errors.append(
            f"/: root element <{actual}> does not match expected "
            f"<{expected}> for class {class_name!r}"
        )

    def has_errors(self) -> bool:
        return bool(self.errors)


# ----------------------------------------------------------------------
# Loader
# ----------------------------------------------------------------------


class XMLLoader(Loader):
    """Load XML into a LinkML target class, schema-driven.

    Usage::

        from schema_automator.loaders.xml_loader import xml_loader
        from linkml_runtime.utils.schemaview import SchemaView

        sv = SchemaView("path/to/schema.yaml")
        result = xml_loader.load(
            "doc.xml",
            target_class="MyClass",
            schemaview=sv,
        )

    Pass ``strict=True`` to collect all unmapped elements/attributes
    and raise ``XMLLoadErrors`` at the end. See the module docstring
    for the full mapping convention reference.
    """

    def load_as_dict(
        self,
        source: Union[str, Path, TextIO],
        *,
        base_dir: Optional[str] = None,
        metadata: Optional[FileInfo] = None,
        schemaview: Optional[SchemaView] = None,
        target_class: Optional[Union[str, type]] = None,
        strict: bool = False,
        **kwargs,
    ) -> dict:
        # `base_dir` and `metadata` are accepted (and ignored) to match
        # the linkml-runtime Loader signature for cross-loader API
        # uniformity. They'd matter if we ever supported URL fetches.
        if schemaview is None:
            raise ValueError("XMLLoader.load_as_dict requires schemaview=")
        if target_class is None:
            raise ValueError("XMLLoader.load_as_dict requires target_class=")

        root = _parse_to_element(source)
        class_name = _class_name(target_class)
        errors = _ErrorCollector() if strict else None

        # Root-tag validation: when the target class is annotated with
        # ``xml_element``, the root XML tag must match that local name.
        cls = schemaview.get_class(class_name)
        if cls is None:
            raise ValueError(
                f"XMLLoader: class {class_name!r} not in schema "
                f"(known: {sorted(schemaview.all_classes())})"
            )
        expected_root = _annotation_value(cls, "xml_element")
        actual_root = _strip_namespace(root.tag)
        if expected_root and actual_root != expected_root:
            if errors is not None:
                errors.add_root_mismatch(expected_root, actual_root, class_name)
            else:
                logger.debug(
                    "XMLLoader: root element <%s> does not match expected <%s> "
                    "for class %r",
                    actual_root, expected_root, class_name,
                )

        result = self._element_to_dict(root, class_name, schemaview, errors=errors)

        if errors is not None and errors.has_errors():
            raise XMLLoadErrors(errors.errors)
        return result

    def load_any(
        self,
        source: Union[str, Path, dict, TextIO],
        target_class: type[Union[BaseModel, YAMLRoot]],
        *,
        base_dir: Optional[str] = None,
        metadata: Optional[FileInfo] = None,
        schemaview: Optional[SchemaView] = None,
        strict: bool = False,
        **_,
    ) -> Union[BaseModel, YAMLRoot]:
        data = self.load_as_dict(
            source,
            base_dir=base_dir,
            metadata=metadata,
            schemaview=schemaview,
            target_class=target_class,
            strict=strict,
        )
        return self._construct_target_class(data, target_class)

    # ------------------------------------------------------------------
    # Internal recursion
    # ------------------------------------------------------------------

    def _element_to_dict(
        self,
        elem,
        class_name: str,
        sv: SchemaView,
        *,
        errors: Optional[_ErrorCollector] = None,
    ) -> dict:
        """Convert one XML element to a dict matching the named class.

        Recursive. When ``errors`` is provided, unmapped elements and
        attributes are accumulated there rather than logged; the caller
        decides whether to raise.
        """
        cls = sv.get_class(class_name)
        if cls is None:
            # Class-lookup errors are always immediate — no recovery
            # path makes sense here, regardless of strict mode.
            raise ValueError(
                f"XMLLoader: class {class_name!r} not in schema "
                f"(known: {sorted(sv.all_classes())})"
            )
        slots = sv.class_induced_slots(class_name)

        result: dict[str, Any] = {}

        # Index slots by how they're sourced from this element.
        attribute_slots: dict[str, Any] = {}  # XML attr name → slot
        element_slots: dict[str, Any] = {}    # XML element tag → slot
        text_slot = None
        path_slots: list[Any] = []

        for slot in slots:
            if _annotation_value(slot, "xml_text"):
                text_slot = slot
                continue
            attr_ann = _annotation_value(slot, "xml_attribute")
            if attr_ann is not None and attr_ann is not False:
                attr_name = slot.name if attr_ann is True else attr_ann
                attribute_slots[attr_name] = slot
                continue
            path_ann = _annotation_value(slot, "xml_path")
            if path_ann:
                path_slots.append((path_ann, slot))
                continue
            element_name = _annotation_value(slot, "xml_element") or slot.name
            element_slots[element_name] = slot

        # In strict mode, xml_path slots reach into descendants whose
        # immediate-child ancestor (e.g. `<total>` for a path of
        # `total/stats/stat/@min`) would otherwise be flagged as an
        # unknown element. Pre-compute the top-level child names that
        # path slots descend through so we can exempt them from the
        # unknown-element accounting.
        path_consumed_children = {
            p.split("/", 1)[0] for p, _ in path_slots if p
        }

        if errors is not None:
            errors.push(_strip_namespace(elem.tag))
        try:
            # XML attributes
            for attr_name, attr_value in elem.attrib.items():
                local = _strip_namespace(attr_name)
                slot = attribute_slots.get(local)
                if slot is None:
                    if errors is not None:
                        errors.add_unknown_attribute(
                            local, _strip_namespace(elem.tag), class_name
                        )
                    else:
                        logger.debug(
                            "XMLLoader: no slot for attribute %r on <%s>",
                            attr_name, elem.tag,
                        )
                    continue
                result[slot.name] = attr_value

            # Element text content (only if any slot wants it)
            if text_slot is not None:
                text = (elem.text or "").strip()
                if text:
                    result[text_slot.name] = text

            # Child elements. Multivalued slots get an empty list by
            # default — LinkML's "multivalued = list, possibly empty"
            # convention. Single-valued slots stay absent if no child
            # matches.
            collected_multivalued: dict[str, list] = {
                slot.name: []
                for slot in element_slots.values()
                if slot.multivalued
            }
            for child in elem:
                tag = _strip_namespace(child.tag)
                slot = element_slots.get(tag)
                if slot is None:
                    if errors is not None and tag not in path_consumed_children:
                        errors.add_unknown_element(tag, class_name)
                    # else: silent (could be source for a path-based
                    # slot resolved below, or just noise we ignore)
                    continue
                value = self._slot_value_from_element(child, slot, sv, errors=errors)
                if slot.multivalued:
                    collected_multivalued[slot.name].append(value)
                else:
                    result[slot.name] = value
            result.update(collected_multivalued)

            # Path-based slots (deep traversal). These don't participate
            # in unknown-element checks since they intentionally reach
            # past direct children.
            for path, slot in path_slots:
                value = _resolve_path(elem, path)
                if value is not None:
                    result[slot.name] = value
        finally:
            if errors is not None:
                errors.pop()

        return result

    def _slot_value_from_element(
        self,
        child,
        slot,
        sv: SchemaView,
        *,
        errors: Optional[_ErrorCollector] = None,
    ):
        """Compute one slot's value from a single child element.

        - If the slot's range is a class in the schema, recurse.
        - Otherwise (scalar range), use the child's text content.
        """
        if slot.range and slot.range in sv.all_classes():
            return self._element_to_dict(child, slot.range, sv, errors=errors)
        return (child.text or "").strip() or None


# ----------------------------------------------------------------------
# Module-level helpers
# ----------------------------------------------------------------------


def _parse_to_element(source: Union[str, Path, TextIO]):
    """Read source into an ElementTree root element.

    Strings starting with ``<`` (after whitespace) are treated as inline
    XML; everything else as a path. Detecting by content avoids calling
    ``Path.exists()`` on strings that aren't valid paths (long inputs,
    NUL bytes, OS-specific illegal characters) which can raise OSError.
    """
    if hasattr(source, "read"):
        return ET.parse(source).getroot()
    if isinstance(source, Path):
        return ET.parse(str(source)).getroot()
    if isinstance(source, str):
        if source.lstrip().startswith("<"):
            return ET.fromstring(source)
        return ET.parse(source).getroot()
    raise ValueError(f"XMLLoader: cannot read source of type {type(source).__name__}")


def _class_name(target_class) -> str:
    if isinstance(target_class, str):
        return target_class
    return getattr(target_class, "class_name", None) or target_class.__name__


def _strip_namespace(tag: str) -> str:
    """Drop the {namespace} prefix from a tag, if any."""
    if "}" in tag:
        return tag.split("}", 1)[1]
    return tag


def _resolve_path(elem, path: str):
    """Resolve an xml_path expression against an element.

    Supports two forms:
      ``a/b/c``         → text content of element at ``a/b/c``
      ``a/b/c/@attr``   → attribute ``attr`` on element at ``a/b/c``

    Step matching is local-name based (namespace-agnostic), matching
    the rest of the loader's contract — ``a/b/c`` will traverse into
    ``<ns:a>``/``<ns:b>``/``<ns:c>`` as well as the unprefixed form.
    For attributes, both ``attr`` and ``{ns}attr`` keys are checked.

    No XPath predicates, no wildcards. Returns None when the path
    doesn't resolve.
    """
    if "/@" in path:
        elem_path, attr_name = path.rsplit("/@", 1)
    else:
        elem_path, attr_name = path, None

    target = elem
    for step in elem_path.split("/"):
        if not step:
            continue
        found = next(
            (child for child in target if _strip_namespace(child.tag) == step),
            None,
        )
        if found is None:
            return None
        target = found

    if attr_name is not None:
        # Try local name first, then any namespaced form ending in /attr_name.
        if attr_name in target.attrib:
            return target.attrib[attr_name]
        for key, value in target.attrib.items():
            if _strip_namespace(key) == attr_name:
                return value
        return None
    text = (target.text or "").strip()
    return text or None


# Module-level instance, matching the convention of other linkml loaders.
xml_loader = XMLLoader()
