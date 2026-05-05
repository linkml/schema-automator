Data Dictionary Format
======================

Schema Automator's canonical data dictionary format — the format we ask
new studies to produce when they're onboarding to a data-sharing pipeline.

This is a forward-looking, prescriptive target spec. The audience is a data
owner at a *new* study, preparing their data for sharing, before any
inconsistent local conventions have set in. Handling of legacy or messy
data dictionaries is a separate concern; those are normalized into this
format by an upstream layer (see :ref:`linkml/schema-automator#200`).

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

Codes encoding
--------------

The ``codes`` field for ``permissible_values`` columns is a single string
containing pipe-separated tokens. Each token is either:

- ``code, label`` — a comma-separated pair, where ``code`` is the literal
  value as it appears in the data and ``label`` is the human-readable
  meaning. Whitespace around the separators is ignored.
- ``value`` — bareword shorthand, interpreted as ``value, value``. Use
  this when the literal data value is itself the human-readable form
  (e.g., color names, country codes, status strings).

Example::

    1, Yes | 0, No | 2, Unknown
    EHR | Survey | Lab
    F, Female | M, Male | O, Other | U, Unknown

Limitations: code or label values cannot contain ``|``; values containing
``,`` must use bareword shorthand or wait for a future spec revision that
introduces escaping.

Conformance
-----------

The format defines two conformance modes:

**Default mode (warn-only).** All best-practice and conditional
requirements are reported as warnings. Tooling continues processing; the
author sees a list of issues to address.

**Strict mode (fail).** Any missing best-practice/conditional field, any
invalid type vocabulary value, or any malformed codes encoding causes
validation to fail. Use this in CI or when consuming a data dictionary
that must be clean.

Both modes are implemented by the same validator running against the same
LinkML schema. Strict mode runs ``linkml-validate`` directly; default mode
wraps it and downgrades non-fatal issues to warnings.

Description content rules
-------------------------

The ``description`` field must contain only prose. The following content
is disallowed:

- Code lists or enumerated values (use ``codes``)
- Unit declarations (use ``unit``)
- Numeric ranges (use ``min`` and ``max``)
- Example values (use the optional Spec B field, when added)

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

Future revisions
----------------

The following are explicitly deferred from v1:

- Named, reusable enum definitions (e.g., declaring an enum once and
  referencing it from multiple ``permissible_values`` columns).
- A ``format`` field for refining types (``string`` + ``format: email``,
  date format strings, etc.).
- Escaping for ``|`` and ``,`` in code values.
- Cross-column constraints (conditional requireds, dependencies).
- Document-level metadata and file-level conventions.
- Per-variable provenance, lineage, and versioning.

Examples
--------

Worked examples are provided in ``docs/examples/``:

- ``dd_example_minimal.tsv`` — Spec A only.
- ``dd_example_with_optional.tsv`` — Spec A plus selected Spec B columns.
- ``dd_example_minimal.yaml`` — Spec A in YAML form.
