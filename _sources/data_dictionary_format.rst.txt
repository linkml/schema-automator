Data Dictionary Format
======================

Schema Automator's canonical data dictionary format — the format we ask
new studies to produce when they're onboarding to a data-sharing pipeline.

This is a forward-looking, prescriptive target spec. The audience is a data
owner at a *new* study, preparing their data for sharing, before any
inconsistent local conventions have set in. Handling of legacy or messy
data dictionaries is a separate concern; those are normalized into this
format by an upstream layer (see `linkml/schema-automator#200
<https://github.com/linkml/schema-automator/issues/200>`_).

Goals
-----

The format provides enough computable information for Schema Automator to
produce maximally-enriched LinkML schemas, while staying simple enough that
any researcher — clinical, environmental, social, business — can author and
maintain it without specialized tooling. The format is row-per-variable and
deliberately minimal.

Substrate
---------

The recommended substrate is **TSV (tab-separated values)**. CSV is also
accepted; tabs avoid quoting issues when code values contain commas.

A YAML form is sanctioned for tooling-friendly authoring (e.g., schema
emission, programmatic generation). YAML and TSV are equivalent — the same
set of rows, the same fields, the same conformance rules. Tooling consumes
either.

The canonical machine-readable definition is the LinkML schema at
``schema_automator/metamodels/data_dictionary.yaml``.

Two specs
---------

The format is structured as two specs:

**Spec A** is the recommended set of fields. This is what we ask researchers
to produce.

**Spec B** is a set of optional columns that researchers may add
independently. Adopting one Spec B column does not require adopting any
other; tooling consumes whichever optional fields are present and ignores
the rest.

Spec A: recommended fields
---------------------------

Each row of a data dictionary describes one column of the data file.

.. list-table::
   :header-rows: 1
   :widths: 15 20 65

   * - Field
     - When required
     - Description
   * - ``name``
     - Always
     - Column name as it appears in the data file. Accepts a string
       identifier or a URI/CURIE; URI/CURIE forms are preferred when the
       column has a known semantic identity in a controlled vocabulary.
   * - ``type``
     - Best-practice required
     - Data type from the canonical type vocabulary (see below).
   * - ``description``
     - Best-practice required
     - Prose description of what the variable represents. **Must not
       contain code lists, unit declarations, value ranges, or example
       values** — those have dedicated fields.
   * - ``codes``
     - When ``type`` is ``permissible_values``
     - The permissible values for this column, encoded as
       ``code, label | code, label | ...``. Bareword shorthand is
       allowed: a token without a comma is interpreted as
       ``value, value``.
   * - ``unit``
     - When ``type`` is ``integer`` or ``decimal``
     - Unit of measure. Use the literal token ``none`` for genuinely
       unitless quantities (counts, ratios). UCUM units are encouraged
       but not required; freeform reasonable units (``mg/dL``,
       ``servings/week``) are accepted.
   * - ``min``
     - When ``type`` is ``integer`` or ``decimal``
     - Minimum permissible value. Use ``none`` for genuinely unbounded
       variables.
   * - ``max``
     - When ``type`` is ``integer`` or ``decimal``
     - Maximum permissible value. Use ``none`` for genuinely unbounded
       variables.

The ``none`` token is distinct from an empty cell. An empty cell means the
author has not declared the field and is reported as a conformance issue.
``none`` is the explicit declaration that the field is genuinely not
applicable.

Spec B: optional columns
-------------------------

Researchers may add any subset of the following columns to a data
dictionary. Each is independently adoptable — including ``label`` does not
imply including ``required``.

.. list-table::
   :header-rows: 1
   :widths: 18 82

   * - Field
     - Description
   * - ``label``
     - Short human-readable name for the variable. Distinct from
       ``description`` (prose) and ``name`` (machine identifier).
   * - ``multivalued``
     - Boolean. Whether each cell of this column contains a list of
       values rather than a single value (e.g., multi-select responses).
   * - ``required``
     - Boolean. Whether this column requires a value in every row.
       Rarely accurately known at authoring time; if absent, schema
       inference fills the gap.
   * - ``pattern``
     - Regular expression that all values of this column must match.
       Power-user field; pattern inference may fill the gap if absent.
   * - ``uri``
     - URI or CURIE that semantically anchors this variable in a
       controlled vocabulary (e.g., ``OMOP:1234567``). Equivalent to
       LinkML's ``slot_uri`` for the emitted slot.
   * - ``see_also``
     - External references — codebooks, study protocols, standards.
       Multivalued in TSV form: see "Multivalued TSV cells" below.
   * - ``example_values``
     - Sample values for this column. Useful as authoring guidance for
       consumers and as a fallback signal for pattern inference when
       ``pattern`` is not provided. Multivalued in TSV form: see
       "Multivalued TSV cells" below.

Multivalued TSV cells
~~~~~~~~~~~~~~~~~~~~~

Multivalued Spec B fields (``see_also``, ``example_values``) encode
multiple values pipe-separated within a single cell, using the same
convention as the ``codes`` field. Whitespace around the ``|`` separator
is trimmed; the values themselves are kept verbatim. If a value contains
a literal pipe, escape it as ``\|`` (same rule as in codes).

Example (a ``see_also`` cell)::

    LOINC:2160-0 | https://example.org/protocol.pdf

In YAML form, multivalued fields are written as plain YAML lists.

Type vocabulary
---------------

The canonical type vocabulary is fixed at ten values. Anything outside this
set is disallowed.

.. list-table::
   :header-rows: 1
   :widths: 25 75

   * - Value
     - Meaning
   * - ``string``
     - Sequence of characters.
   * - ``integer``
     - Whole number.
   * - ``decimal``
     - Real number. Covers ``float`` and ``double`` at the LinkML
       emission layer; Schema Automator chooses the appropriate LinkML
       primitive based on observed data.
   * - ``boolean``
     - True/false value.
   * - ``date``
     - Calendar date, ISO 8601 (``YYYY-MM-DD``) by default.
   * - ``datetime``
     - Date and time, ISO 8601 by default.
   * - ``time``
     - Time of day, ISO 8601 by default.
   * - ``uri``
     - Uniform Resource Identifier (full IRI form).
   * - ``curie``
     - Compact URI (e.g., ``OMOP:1234567``).
   * - ``permissible_values``
     - The variable is enumerated. The ``codes`` field declares its
       permissible values.

The vocabulary is the researcher-comprehensible subset of LinkML's built-in
types. Technical LinkML primitives (``ncname``, ``nodeidentifier``,
``jsonpath``, etc.) are excluded — researchers won't write them, and
emission can't honor the distinction usefully without other context.

Composite or multi-typed declarations (e.g., ``decimal, encoded``) are not
permitted. Enumerated columns use the ``permissible_values`` type and
declare their codes in the ``codes`` field; an integer column whose values
are codes (e.g., ``1=Yes, 0=No``) is declared as ``permissible_values``
with codes, not as ``integer`` with codes.

Codes
-----

The ``codes`` field for ``permissible_values`` columns is a list of
``PermissibleValueDefinition`` records — each carrying a code, an
optional label, and optional per-code metadata (description, semantic
URI). The canonical structured form is used in YAML; TSV authors use a
compact serialization grammar described below.

Canonical (structured) form
~~~~~~~~~~~~~~~~~~~~~~~~~~~

In YAML, ``codes`` is a list of mappings. Each mapping has at least a
``code`` (the literal data value); ``label`` is recommended; ``description``
and ``uri`` are optional Spec B-style additions for richer per-code
metadata.

::

    codes:
      - {code: F, label: Female}
      - {code: M, label: Male}
      - {code: O, label: Other}
      - {code: U, label: Unknown}

For the bareword case (where the literal data value is itself the
human-readable form), the ``label`` is omitted:

::

    codes:
      - {code: EHR}
      - {code: Survey}
      - {code: Lab}

Per-code metadata example::

    codes:
      - code: "1"
        label: Current smoker
        description: Self-reported current daily or occasional smoker.
        uri: SCTID:77176002

TSV serialization
~~~~~~~~~~~~~~~~~

In TSV form, the ``codes`` list is serialized as a single string of
pipe-separated tokens. Each token is either:

- ``code, label`` — a comma-separated pair, where ``code`` is the literal
  value as it appears in the data and ``label`` is the human-readable
  meaning. The first comma in a token separates code from label;
  subsequent commas in the label are literal text. Whitespace around the
  separators is ignored.
- ``value`` — bareword shorthand, interpreted as a code with no label
  (the literal value serves as both code and meaning). Use this when the
  literal data value is itself the human-readable form (e.g., color
  names, country codes, status strings).

Examples::

    1, Yes | 0, No | 2, Unknown
    EHR | Survey | Lab
    F, Female | M, Male | O, Other | U, Unknown

The TSV serialization is lossy with respect to the canonical structured
form — only ``code`` and ``label`` survive the round-trip. Per-code
``description`` and ``uri`` cannot be expressed in the TSV grammar; if
those fields matter, use YAML or write them in a sibling YAML file.

Escaping
~~~~~~~~

To include a literal comma, pipe, or backslash in a code, prefix it with
a backslash:

- ``\,`` — literal comma
- ``\|`` — literal pipe
- ``\\`` — literal backslash

Examples with escaping::

    1, Black\, non-Hispanic | 2, White\, non-Hispanic | 3, Hispanic
    >=$50\,000, Middle income | <$50\,000, Low income

Note that labels (the part after the first comma in a ``code, label``
token) may contain unescaped commas — only the first comma per token is
parsed as the code/label separator. Codes (the part before the comma, or
the entire bareword) must escape commas because the first unescaped comma
would otherwise be parsed as the separator.

Other backslash sequences (e.g., ``\n``, ``\t``) are reserved for future
revisions and are currently invalid.

Conformance
-----------

The format defines two conformance modes:

**Default mode (warn-only).** All best-practice and conditional
requirements are reported as warnings. Tooling continues processing; the
author sees a list of issues to address.

**Strict mode (fail).** Any missing best-practice/conditional field, any
invalid type vocabulary value, malformed codes encoding, or
type-inappropriate field (e.g., ``codes`` on a ``boolean`` row, ``unit``
on a ``string`` row) causes validation to fail. Use this in CI or when
consuming a data dictionary that must be clean.

Both modes are implemented by the same validator running against the same
LinkML schema. Strict mode runs ``linkml-validate`` directly; default mode
wraps it and downgrades non-fatal issues to warnings.

A small number of content-quality concerns cannot be expressed in the
LinkML schema cleanly and are enforced by an additional lint pass:

- Descriptions containing code lists, units, ranges, or example values
  (see "Description content rules" below).
- Numeric ``min``/``max`` values whose numeric form does not match the
  declared type — e.g., a fractional ``0.5`` minimum on an ``integer``
  column. The schema accepts any number for ``min``/``max``; the lint
  pass catches the type mismatch.

Description content rules
-------------------------

The ``description`` field must contain only prose. The following content
is disallowed:

- Code lists or enumerated values (use ``codes``)
- Unit declarations (use ``unit``)
- Numeric ranges (use ``min`` and ``max``)
- Example values (use ``example_values``, optional Spec B)

Descriptions polluted with such content are less useful, not more, and
indicate the author put information in the wrong place. Enforcement is
performed by a content-quality lint (separate from structural validation)
that flags suspicious description content.

Document-level metadata
-----------------------

The format intentionally has no document-level metadata in v1. There is no
header section, no sidecar metadata file, and no filename convention.
Every productive option (header that breaks CSV/TSV format, sidecar that
adds coupling, filename encoding that's fragile to parse) has worse
trade-offs than dropping document-level metadata entirely. If a future
revision adds it, the substrate decision will need to be revisited.

Relationship to existing formats
--------------------------------

Across communities, real-world data dictionaries converge on a small core:
**name, description, and (sometimes, partially) type information**. That
common ground is what nearly every author actually writes, regardless of
which format they nominally produce. This spec is a deliberately small
extension of that core — adding the structure needed to validate and
enrich, while staying close to what people already draft in the wild.

The flat-file shape is a deliberate alignment, not an oversight. Every
format below (with the partial exception of XML codebook standards) starts
from row-per-variable, columns-of-attributes. That's how data dictionaries
naturally exist in researcher hands — a spreadsheet, a CSV, a few columns
deep. Adding hierarchy, sidecar files, or required tooling would make
authoring harder *and* make conversion from existing formats harder. We
chose simplicity at this layer in exchange for keeping the
existing-format-to-this-format adapters tractable.

We are implementing the core of the formats listed below. If our spec ever
diverges substantially from that core, that's a signal we've over-rotated
on novelty and should re-examine the divergence rather than ship it.

**Frictionless Table Schema** (data.gov, OpenML, the ``datasets`` package).
Our type vocabulary is a researcher-comprehensible subset of Frictionless's;
``pattern`` and per-column structure align directly. Where we diverge: we
treat enumerated values as a primary type (``permissible_values``) rather
than a string-with-enum-constraint, matching how researchers think about
multiple-choice columns. We intend to ship a Frictionless adapter
(translator in both directions).

**REDCap data dictionary** (de facto standard in clinical research). Our
codes encoding (``code, label | code, label | ...`` with bareword
shorthand) is taken directly from REDCap. Our type-as-major-axis approach
mirrors REDCap's Field Type. We diverge by collapsing REDCap's UI-flavored
types (``radio``, ``dropdown``, ``checkbox``) into the single semantic
type ``permissible_values`` — a data dictionary describes data, not the
form widget that produced it. We intend to ship a REDCap adapter.

**SchemaSheets** (LinkML community). This format supersedes SchemaSheets
for the data-dictionary use case. Where SchemaSheets requires authors to
work with LinkML conventions (slot/class distinctions, slot URIs, mixin
semantics), we present a researcher-comprehensible flat surface.
SchemaSheets capabilities not directly expressible here will be addressed
during the migration period. A SchemaSheets adapter is part of the
planned tooling.

**DDI / CDISC** (heavyweight institutional standards). These describe a
different scope — full study lifecycle, regulatory submission. Not
displaced; complementary in cases where they apply.

Out of scope
------------

This format intentionally covers a single, flat tabular dataset described
by a single data dictionary. The following use cases need a higher-order
artifact on top of, or alongside, this format, and are explicitly out of
scope:

- **Hierarchical or nested data.** Columns containing JSON-shaped
  structures, repeated groups, document trees. Authoring as a flat
  row-per-column descriptor doesn't fit. Use a structured data model
  (LinkML class definitions, JSON Schema, Avro) for the nesting and
  reference this format for leaf-level columns where applicable.

- **Multi-table datasets with relationships.** Several related tables
  sharing keys (e.g., dbGaP's phs/pht/phv structure, relational
  databases). Each table can have its own data dictionary in this format,
  but the relational structure between them — foreign keys, joins, shared
  dimensions — is the job of a higher-order schema artifact. A simple
  manifest pattern (a list of data dictionaries plus a relations file)
  would address this without burdening per-DD authoring.

- **Variable versioning and lineage.** "This variable was renamed from
  ``old_name`` in v3," "valid from 2020-01 to 2023-06," provenance chains.
  Versioning concerns belong at the dataset/schema level, not per-row.

- **Cross-column constraints.** Conditional required-fields, dependencies
  ("field A is required only if field B is X"), value relationships
  across columns. The general case needs a real expression language, not
  a small format extension.

- **Domain-specific metadata.** Clinical (codeset versions, encounter
  types), survey (question wording, branching logic), environmental
  (sensor calibration, measurement uncertainty). The format is
  intentionally domain-naive. Domain extensions can live in optional
  Spec B columns by convention, but defining them is the responsibility
  of domain communities, not this spec.

Future revisions
----------------

The following are deferred from v1 but may be added as small additive
extensions to *this* format in future revisions:

- Named, reusable enum definitions (e.g., declaring an enum once and
  referencing it from multiple ``permissible_values`` columns).
- A ``format`` field for refining types (``string`` + ``format: email``,
  date format strings, etc.).
- Document-level metadata and file-level conventions.

Examples
--------

Worked examples are provided in ``docs/examples/``:

- ``dd_example_minimal.tsv`` — Spec A only.
- ``dd_example_with_optional.tsv`` — Spec A plus selected Spec B columns.
- ``dd_example_minimal.yaml`` — Spec A in YAML form.
