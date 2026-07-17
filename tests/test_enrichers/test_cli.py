"""End-to-end CLI tests for the enrichment surface.

Three commands expose enrichment:

- ``schemauto enrich`` — standalone, applies one or more DDs to an
  existing LinkML schema.
- ``schemauto generalize-tsv --data-dictionary`` — convenience that
  runs single-file inference and enrichment in one shot.
- ``schemauto generalize-tsvs --data-dictionary`` — multi-file
  inference plus multi-DD enrichment.

The standalone ``enrich`` command is the primary surface; the
``--data-dictionary`` flag on generalize is a convenience wrapper that
calls the same enricher with the same matching policy.
"""

from __future__ import annotations

from pathlib import Path

import yaml
from click.testing import CliRunner
from linkml_runtime.loaders import yaml_loader
from linkml_runtime.linkml_model import SchemaDefinition

from schema_automator.cli import main


_FIXTURES = Path(__file__).resolve().parents[1] / "resources" / "dbgap"


def _load_yaml(path: Path) -> dict:
    with path.open() as f:
        return yaml.safe_load(f)


def test_enrich_standalone(tmp_path):
    """``schemauto enrich`` overlays a DD onto an already-inferred schema."""
    # Pre-build an inferred schema so the test exercises only enrichment.
    inferred = tmp_path / "inferred.yaml"
    runner = CliRunner()
    inf_result = runner.invoke(
        main,
        [
            "generalize-tsv",
            "--column-separator", "\t",
            "--class-name", "Subject",
            "--schema-name", "jhs",
            "-o", str(inferred),
            str(_FIXTURES / "JHS_Subject.data.tsv"),
        ],
    )
    assert inf_result.exit_code == 0, inf_result.output

    enriched = tmp_path / "enriched.yaml"
    result = runner.invoke(
        main,
        [
            "enrich",
            "--schema", str(inferred),
            "--data-dictionary", str(_FIXTURES / "JHS_Subject.dd.yaml"),
            "-o", str(enriched),
        ],
    )
    assert result.exit_code == 0, result.output

    # Output round-trips through linkml-runtime's SchemaDefinition loader.
    with enriched.open() as f:
        sch = yaml_loader.load(f.read(), SchemaDefinition)
    consent = sch.slots["CONSENT"]
    # DD-supplied metadata is present.
    assert consent.description == "Consent group as determined by DAC"
    assert consent.slot_uri == "dbgap:phv00124546.v4"


def test_enrich_requires_at_least_one_dd(tmp_path):
    """The ``--data-dictionary`` flag is required."""
    inferred = tmp_path / "inferred.yaml"
    inferred.write_text("id: ex\nname: ex\nclasses: {}\n")
    runner = CliRunner()
    result = runner.invoke(main, ["enrich", "--schema", str(inferred), "-o", str(tmp_path / "out.yaml")])
    assert result.exit_code != 0
    assert "data-dictionary" in result.output.lower() or "data_dictionary" in result.output.lower()


def test_generalize_tsv_with_data_dictionary(tmp_path):
    """The convenience flag on generalize-tsv runs both stages."""
    out = tmp_path / "out.yaml"
    runner = CliRunner()
    result = runner.invoke(
        main,
        [
            "generalize-tsv",
            "--column-separator", "\t",
            "--class-name", "Subject",
            "--schema-name", "jhs",
            "--data-dictionary", str(_FIXTURES / "JHS_Subject.dd.yaml"),
            "-o", str(out),
            str(_FIXTURES / "JHS_Subject.data.tsv"),
        ],
    )
    assert result.exit_code == 0, result.output

    sch = yaml_loader.load(out.read_text(), SchemaDefinition)
    # Enrichment supplied the DD's descriptions and slot URIs.
    assert sch.slots["CONSENT"].description == "Consent group as determined by DAC"
    assert sch.slots["SUBJECT_ID"].slot_uri == "dbgap:phv00124545.v4"


def test_generalize_tsv_multiple_data_dictionaries(tmp_path):
    """``--data-dictionary`` is repeatable; multi-DD applies in order."""
    # Synthesize a second DD that overrides only one field's description.
    # Later DDs see metadata already-written by earlier ones — and the
    # enricher's "apply if absent" policy means the first DD's
    # descriptions stick.
    second_dd = tmp_path / "override.dd.yaml"
    second_dd.write_text(
        "entries:\n"
        "  - name: SUBJECT_ID\n"
        "    type: string\n"
        "    description: Overridden description\n"
    )

    out = tmp_path / "out.yaml"
    runner = CliRunner()
    result = runner.invoke(
        main,
        [
            "generalize-tsv",
            "--column-separator", "\t",
            "--class-name", "Subject",
            "--schema-name", "jhs",
            "--data-dictionary", str(_FIXTURES / "JHS_Subject.dd.yaml"),
            "--data-dictionary", str(second_dd),
            "-o", str(out),
            str(_FIXTURES / "JHS_Subject.data.tsv"),
        ],
    )
    assert result.exit_code == 0, result.output

    sch = yaml_loader.load(out.read_text(), SchemaDefinition)
    # First DD wins on SUBJECT_ID — "apply if absent" prevents the second
    # overlay from overwriting metadata already set by the first.
    assert sch.slots["SUBJECT_ID"].description == "Subject ID"
