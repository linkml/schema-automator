"""Enrich an inferred LinkML schema with a canonical data dictionary.

The enricher is format-agnostic: it consumes a canonical Data Dictionary
dict (matching ``schema_automator/metamodels/data_dictionary.yaml``) and
an inferred ``SchemaDefinition``, and overlays the DD's declared
metadata onto the inferred slots. Sources of canonical DDs include the
adapter family in ``schema_automator/adapters/`` (Frictionless, dbGaP,
REDCap) and direct YAML authoring.

Merge policy (see issue #192 / umbrella #190):

- ``description``, ``label`` (→ ``title``), ``uri`` (→ ``slot_uri``),
  ``unit``, ``pattern``, ``see_also``, ``multivalued``: DD-declared
  values are applied when the inferred slot lacks them. DD always wins
  on the metadata layer because inference cannot see this information.
- ``required``: DD's ``True`` is applied; conflicts with observed nulls
  are logged. Inference's ``required: False`` is preserved as a signal
  to ``--infer-optional`` users.
- ``type`` (DD) vs inferred ``range``: **inference wins on type
  mismatch** (the data is the data). The conflict is logged so the
  user can decide whether to trust the DD or fix the data.
- ``min`` / ``max``: applied to ``minimum_value`` / ``maximum_value``
  on the slot. The literal sentinel ``none`` is treated as "explicitly
  unbounded" and not applied.
- ``codes`` (``permissible_values`` type): three cases, distinguished
  by what inference produced and what evidence it left behind:

  - If the slot's range is already an enum (inference enum-ified a
    low-cardinality column), the DD's codes are merged into it. DD
    codes contribute labels / descriptions / URIs; codes seen only in
    the data and codes declared only in the DD are both preserved in
    the enriched enum and logged.

  - If the slot's range is a primitive AND ``CsvDataGeneralizer``
    recorded ``num_distinct_values`` as a slot annotation AND the DD
    declares ≤ that many codes, the DD's enum is provably incomplete
    by count (it can't cover all observed distinct values). The
    inferred range is kept; DD codes are stashed on the slot as a
    structured annotation (``declared_permissible_values``) for
    downstream tools to surface; the discrepancy is logged.

  - Otherwise (no annotation, or DD has more codes than were observed):
    the slot is upgraded to an enum populated from the DD's codes.

All discrepancies are collected in an :class:`EnrichmentReport` and
emitted as logger warnings. This v1 stops short of the structured
reconciliation report (issue #193); the report object is the
machine-readable form behind the warnings.

Known limitation: the enricher matches DD entries against
``schema.slots[name]``. Schemas produced by ``PandasDataGeneralizer``
(``--pandera`` path) put inferred slots on each class's ``attributes``
inline, leaving ``schema.slots`` empty — so the enricher detects the
shape up-front, emits a single warning, and returns without enrichment
(rather than logging one "unmatched" warning per DD entry). The default
``CsvDataGeneralizer`` path is fully supported. Pandera support is
tracked as a follow-up.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Any

from linkml_runtime.linkml_model import (
    Annotation,
    EnumDefinition,
    PermissibleValue,
    SchemaDefinition,
    SlotDefinition,
)


logger = logging.getLogger(__name__)


# Mapping from canonical DD type vocabulary to LinkML primitive ranges.
# Used to detect inference-vs-DD type conflicts. ``permissible_values``
# isn't in this map — it's handled separately as the "this slot has an
# enum" signal.
_DD_TYPE_TO_RANGE = {
    "string": "string",
    "integer": "integer",
    "decimal": "float",
    "boolean": "boolean",
    "date": "date",
    "datetime": "datetime",
    "time": "time",
    "uri": "uri",
    "curie": "uriorcurie",
}


@dataclass
class EnrichmentReport:
    """Structured record of discrepancies surfaced during enrichment.

    Each field is a list of tuples describing one discrepancy. The
    report is also emitted as logger warnings during enrichment; this
    object is the machine-readable form for callers that want to act
    on the discrepancies (e.g., reconciliation report in #193).
    """

    type_conflicts: list[tuple[str, str, str]] = field(default_factory=list)
    """(slot_name, inferred_range, declared_dd_type) — DD said one type,
    inference saw another."""

    required_conflicts: list[str] = field(default_factory=list)
    """slot_name — DD declared the slot required but inference saw nulls."""

    range_violations: list[tuple[str, str, str]] = field(default_factory=list)
    """(slot_name, kind, detail) — observed values fall outside the DD's
    declared bounds. ``kind`` is one of ``min`` or ``max``."""

    extra_data_codes: list[tuple[str, list[str]]] = field(default_factory=list)
    """(slot_name, codes) — codes present in the data but not declared
    in the DD's permissible values."""

    extra_dd_codes: list[tuple[str, list[str]]] = field(default_factory=list)
    """(slot_name, codes) — codes declared in the DD but never observed
    in the data. Retained in the enriched schema."""

    incomplete_dd_enums: list[tuple[str, int, int]] = field(default_factory=list)
    """(slot_name, dd_code_count, observed_distinct_count) — slots where
    the DD declares ``permissible_values`` but inference produced a
    primitive range AND the DD declares fewer codes than were observed
    (provably incomplete by count). The slot's inferred range is kept;
    the DD's codes are stashed as a slot annotation instead of replacing
    the range with an enum."""

    unmatched_dd_entries: list[str] = field(default_factory=list)
    """DD entry names with no matching slot in the inferred schema."""

    @property
    def is_clean(self) -> bool:
        """True iff no discrepancies were recorded."""
        return not (
            self.type_conflicts
            or self.required_conflicts
            or self.range_violations
            or self.extra_data_codes
            or self.extra_dd_codes
            or self.incomplete_dd_enums
            or self.unmatched_dd_entries
        )


def enrich_with_data_dictionary(
    schema: SchemaDefinition,
    data_dictionary: dict[str, Any],
) -> EnrichmentReport:
    """Overlay a canonical data dictionary onto an inferred LinkML schema.

    Mutates *schema* in place. Returns an :class:`EnrichmentReport`
    describing every discrepancy surfaced during the merge.

    Parameters
    ----------
    schema : SchemaDefinition
        Inferred schema produced by a generalizer (e.g.,
        ``CsvDataGeneralizer``). Slots in ``schema.slots`` are matched
        against DD entry names.
    data_dictionary : dict
        Canonical DD with ``entries: [{name, type, ...}, ...]`` per
        ``schema_automator/metamodels/data_dictionary.yaml``.
    """
    report = EnrichmentReport()
    entries = data_dictionary.get("entries", [])

    # Pandera-shaped schemas put slots on each class's ``attributes``
    # inline and leave ``schema.slots`` empty. Without this guard, every
    # DD entry would log as "unmatched" — noisy and misleading. Detect
    # the shape up-front and emit a single, clear warning instead.
    if not schema.slots and any(
        getattr(cls, "attributes", None) for cls in (schema.classes or {}).values()
    ):
        logger.warning(
            "Schema has no top-level slots but classes carry inline "
            "attributes (PandasDataGeneralizer / pandera shape). The "
            "enricher does not yet support attributes-on-class form; "
            "no enrichment applied."
        )
        return report

    for entry in entries:
        name = entry.get("name")
        if name is None:
            continue
        # schema.slots is a JsonObj-flavored mapping; .get() is not
        # available, but __contains__ / __getitem__ are.
        if name not in schema.slots:
            report.unmatched_dd_entries.append(name)
            logger.warning(
                "Data dictionary declares variable %r that has no "
                "matching slot in the inferred schema (column missing "
                "from data?)",
                name,
            )
            continue
        _enrich_slot(schema, schema.slots[name], entry, report)

    return report


def _enrich_slot(
    schema: SchemaDefinition,
    slot: SlotDefinition,
    entry: dict[str, Any],
    report: EnrichmentReport,
) -> None:
    """Apply one DD entry's metadata to its matching slot."""
    name = slot.name

    # ---- Pure-metadata layer: DD wins when slot lacks the field. ----
    _apply_if_absent(slot, "description", entry.get("description"))
    _apply_if_absent(slot, "title", entry.get("label"))
    _apply_if_absent(slot, "slot_uri", entry.get("uri"))
    _apply_if_absent(slot, "pattern", entry.get("pattern"))

    see_also = entry.get("see_also") or []
    if see_also and not slot.see_also:
        slot.see_also = list(see_also)

    unit = entry.get("unit")
    if unit and unit != "none" and not slot.unit:
        slot.unit = {"ucum_code": unit}

    # ---- Constraint layer with conflict handling. ----
    if entry.get("multivalued") is True and slot.multivalued is not True:
        slot.multivalued = True

    declared_required = entry.get("required")
    if declared_required is True:
        if slot.required is False:
            # Inference set required=False because data has nulls.
            report.required_conflicts.append(name)
            logger.warning(
                "Data dictionary declares %r as required, but inferred "
                "schema marks it required=False (data contains nulls).",
                name,
            )
        # Apply the DD's True regardless — declared constraint wins.
        slot.required = True

    # min / max → minimum_value / maximum_value (drop the literal
    # 'none' sentinel from DD; it means "explicitly unbounded").
    declared_min = entry.get("min")
    if declared_min is not None and declared_min != "none":
        if slot.minimum_value is None:
            slot.minimum_value = declared_min
    declared_max = entry.get("max")
    if declared_max is not None and declared_max != "none":
        if slot.maximum_value is None:
            slot.maximum_value = declared_max

    # ---- Type / range layer. ----
    declared_type = entry.get("type")
    if declared_type == "permissible_values":
        _enrich_permissible_values(schema, slot, entry, report)
    elif declared_type is not None:
        _check_type_consistency(schema, slot, declared_type, report)


def _read_num_distinct_values(slot: SlotDefinition) -> int | None:
    """Return inference's recorded observed-distinct-value count for the
    slot, or ``None`` if the slot has no such annotation (e.g., the
    schema was hand-authored or produced by a generalizer that doesn't
    expose this signal).

    ``CsvDataGeneralizer`` attaches the value as
    ``slot.annotations['num_distinct_values'].value`` (string-cast int).
    """
    if not slot.annotations or "num_distinct_values" not in slot.annotations:
        return None
    ann = slot.annotations["num_distinct_values"]
    try:
        return int(ann.value)
    except (TypeError, ValueError):
        return None


def _attach_declared_codes_annotation(
    slot: SlotDefinition, dd_codes: list[dict[str, Any]]
) -> None:
    """Stash the DD's codes on the slot as a structured annotation.

    Used when the DD declares ``permissible_values`` but the count
    heuristic indicates the DD enum cannot cover all observed values —
    we don't replace the inferred range, but we don't want to lose the
    DD's authoritative labels either. Tools that want to surface the
    declared codes (reconciliation reporters, documentation generators)
    can read the annotation.
    """
    slot.annotations["declared_permissible_values"] = Annotation(
        tag="declared_permissible_values",
        value=dd_codes,
    )


def _apply_if_absent(slot: SlotDefinition, attr: str, value: Any) -> None:
    """Set ``slot.attr = value`` only if the slot doesn't already have
    a non-empty value for that attribute."""
    if value is None or value == "":
        return
    current = getattr(slot, attr, None)
    if current:
        return
    setattr(slot, attr, value)


def _check_type_consistency(
    schema: SchemaDefinition,
    slot: SlotDefinition,
    declared_type: str,
    report: EnrichmentReport,
) -> None:
    """Compare DD's declared scalar type to the slot's inferred range.

    Inference wins on conflict — we don't rewrite the range — but the
    discrepancy is logged. Type mismatches are real signal: the data
    doesn't match the dictionary's expectation, and a human should
    decide whether to trust the data, fix the data, or fix the
    dictionary.
    """
    expected_range = _DD_TYPE_TO_RANGE.get(declared_type)
    if expected_range is None:
        return
    inferred_range = slot.range
    # Slots whose range points at an enum (regardless of naming
    # convention) are skipped here — they're the territory of
    # _enrich_permissible_values. Membership in schema.enums is the
    # authoritative check; the prior heuristic of matching ``_enum``
    # suffix would false-positive on importers that use different
    # naming (e.g., ``*_options`` from jsonschema_import_engine).
    if inferred_range and inferred_range in schema.enums:
        return
    if inferred_range and inferred_range != expected_range:
        report.type_conflicts.append((slot.name, inferred_range, declared_type))
        logger.warning(
            "Type conflict on %r: data dictionary declares %r, "
            "inference saw %r. Keeping inferred range; user should "
            "reconcile.",
            slot.name,
            declared_type,
            inferred_range,
        )


def _enrich_permissible_values(
    schema: SchemaDefinition,
    slot: SlotDefinition,
    entry: dict[str, Any],
    report: EnrichmentReport,
) -> None:
    """Merge DD-declared codes into the slot's enum.

    Cases:

    1. Slot's range is already an enum (inference found a low-cardinality
       categorical). Merge DD's labels in; union code sets; log diffs.
    2. Slot's range is a primitive and inference recorded ``num_distinct_values``
       on the slot showing the DD declares fewer codes than were observed.
       The DD's enum is provably incomplete by count: keep the inferred
       range, stash the DD codes as a slot annotation, and log.
    3. Slot's range is a primitive (no contradicting evidence): upgrade
       to an enum populated from the DD's codes.
    """
    dd_codes = entry.get("codes") or []
    dd_code_values = [c["code"] for c in dd_codes if "code" in c]

    inferred_range = slot.range
    enum_name = (
        inferred_range
        if inferred_range and inferred_range in schema.enums
        else None
    )

    if enum_name is None:
        # Case 2 vs. 3: decide whether to upgrade the primitive range to
        # an enum, or refuse to upgrade because the DD looks incomplete
        # relative to what inference observed.
        observed_distinct = _read_num_distinct_values(slot)
        if observed_distinct is not None and len(dd_codes) <= observed_distinct:
            # DD declares <= as many codes as inference saw distinct
            # values. By pigeonhole, the DD cannot cover all observed
            # values (unless its set is exactly the same — which we
            # can't verify without value-level comparison). Treat as
            # incomplete: keep the inferred primitive range and stash
            # the DD codes as a slot annotation.
            report.incomplete_dd_enums.append(
                (slot.name, len(dd_codes), observed_distinct)
            )
            logger.warning(
                "Permissible-values mismatch on %r: data dictionary "
                "declares %d code(s) but inference observed %d distinct "
                "value(s) in the data. Keeping inferred range %r and "
                "attaching DD codes as a slot annotation rather than "
                "collapsing to an enum that would silently drop "
                "observed values.",
                slot.name,
                len(dd_codes),
                observed_distinct,
                slot.range,
            )
            _attach_declared_codes_annotation(slot, dd_codes)
            return

        # Case 3: upgrade.
        enum_name = f"{slot.name}_enum"
        schema.enums[enum_name] = EnumDefinition(name=enum_name)
        slot.range = enum_name

    enum_def = schema.enums[enum_name]
    observed = dict(enum_def.permissible_values or {})

    observed_codes = set(observed.keys())
    declared_codes = set(dd_code_values)

    only_in_data = observed_codes - declared_codes
    only_in_dd = declared_codes - observed_codes

    if only_in_data:
        sorted_extra = sorted(only_in_data)
        report.extra_data_codes.append((slot.name, sorted_extra))
        logger.warning(
            "Permissible-value mismatch on %r: data contains code(s) "
            "%s that the data dictionary does not declare. Keeping "
            "them in the enriched enum.",
            slot.name,
            sorted_extra,
        )

    if only_in_dd:
        sorted_extra = sorted(only_in_dd)
        report.extra_dd_codes.append((slot.name, sorted_extra))
        logger.warning(
            "Permissible-value mismatch on %r: data dictionary "
            "declares code(s) %s that were not observed in the data. "
            "Keeping them in the enriched enum.",
            slot.name,
            sorted_extra,
        )

    # Union-merge: DD codes supply labels/descriptions/URIs; inferred
    # codes that the DD doesn't cover keep their inferred shape.
    for dd_code in dd_codes:
        code = dd_code.get("code")
        if code is None:
            continue
        existing = observed.get(code)
        pv = existing if existing is not None else PermissibleValue(text=code)
        if "label" in dd_code and dd_code["label"]:
            pv.title = dd_code["label"]
        if "description" in dd_code and dd_code["description"]:
            pv.description = dd_code["description"]
        if "uri" in dd_code and dd_code["uri"]:
            pv.meaning = dd_code["uri"]
        observed[code] = pv

    enum_def.permissible_values = observed
