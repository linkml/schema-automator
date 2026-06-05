"""dbGaP variable digest → canonical Data Dictionary adapter.

dbGaP publishes two complementary XML files per pheno table:

- ``*.data_dict.xml`` — the declared data dictionary. One ``<variable>``
  per column with ``<name>``, ``<description>``, ``<type>``, and
  ``<value code="X">label</value>`` children for encoded values.
- ``*.var_report.xml`` — the empirical summary report. Multiple
  ``<variable>`` rows per column: one for the total set and one per
  consent group (suffixed ``.c1``, ``.c2``, …). Carries
  ``calculated_type``, ``reported_type``, and a ``<stat>`` element with
  ``n``, ``nulls``, ``min``, ``max`` for numerics, plus per-code
  ``<enum>`` counts for enumerated types.

This adapter:

1. Parses one or both XML files with ``lxml``.
2. Merges them by phv-id into a structured ``VariableDigest`` dict —
   data_dict provides declared name/type/codes, var_report provides
   empirical bounds and the ``calculated_type`` fallback.
3. Invokes the linkml-map trans-spec at ``dbgap_to_dd.transform.yaml``
   to produce a canonical Data Dictionary.

Per-consent-group rows in var_report (IDs containing ``.c<N>``) are
ignored — only the total-set row contributes empirical signal.
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any

from lxml import etree
from linkml_map.transformer.object_transformer import ObjectTransformer
from linkml_map.utils.loaders import load_specification
from functools import lru_cache

from linkml_runtime.utils.schemaview import SchemaView

from schema_automator.loaders.xml_loader import safe_xml_parser, xml_loader


_PKG_ROOT = Path(__file__).resolve().parents[2]
_DD_SCHEMA = _PKG_ROOT / "metamodels" / "data_dictionary.yaml"
_DBGAP_SCHEMA = _PKG_ROOT / "metamodels" / "dbgap.yaml"
_DBGAP_TO_DD_SPEC = _PKG_ROOT / "adapters" / "dbgap" / "dbgap_to_dd.transform.yaml"


@lru_cache(maxsize=1)
def _dbgap_schemaview() -> SchemaView:
    """Cached SchemaView for the dbGaP source schema.

    Construction is non-trivial; lru_cache provides thread-safe lazy
    initialization (atomic in CPython under the GIL).
    """
    return SchemaView(str(_DBGAP_SCHEMA))


# A var_report variable ID per-consent-group is ``<phv>.v<N>.p<M>.c<K>``;
# the total-set row drops the ``.c<K>`` suffix and looks like
# ``<phv>.v<N>.p<M>``. We match the trailing ``.p<digits>`` and reject
# anything followed by ``.c``.
_TOTAL_SET_RE = re.compile(r"\.p\d+$")


def _text(elem) -> str | None:
    if elem is None:
        return None
    return (elem.text or "").strip() or None


def _parse_data_dict(path: Path) -> dict:
    """Parse a dbGaP data_dict.xml file into a structured dict.

    Schema-driven via :mod:`schema_automator.loaders.xml_loader` —
    the dbGaP LinkML schema's annotations on ``VariableDigest``,
    ``Variable`` and ``EncodedValue`` describe how the XML maps to
    slots. Output shape matches the ``data_dict`` portion of the
    merged ``VariableDigest`` form expected by the trans-spec.
    """
    return xml_loader.load_as_dict(
        path,
        target_class="VariableDigest",
        schemaview=_dbgap_schemaview(),
    )


def _parse_var_report(path: Path) -> dict:
    """Parse a dbGaP var_report.xml file into a structured dict.

    Only the *total-set* variable rows are kept (IDs ending in
    ``.p<N>`` with no ``.c<M>`` suffix). Per-consent-group rows are
    ignored — they're useful for slicing studies but mix poorly with
    the generic DD format.
    """
    root = etree.parse(str(path), safe_xml_parser()).getroot()
    if root.tag != "data_table":
        raise ValueError(
            f"{path}: expected <data_table> root, got <{root.tag}>"
        )
    variables = []
    for v_elem in root.findall("variable"):
        vid = v_elem.get("id", "")
        if not _TOTAL_SET_RE.search(vid):
            # Per-consent-group row; skip.
            continue
        stat = v_elem.find("./total/stats/stat")
        min_v = stat.get("min") if stat is not None else None
        max_v = stat.get("max") if stat is not None else None
        # dbGaP sometimes emits empty string for min/max; normalize.
        min_v = min_v if min_v else None
        max_v = max_v if max_v else None
        variables.append(
            {
                "id": vid,
                "var_name": v_elem.get("var_name", ""),
                "calculated_type": v_elem.get("calculated_type"),
                "reported_type": v_elem.get("reported_type"),
                "description": _text(v_elem.find("description")),
                "min": min_v,
                "max": max_v,
            }
        )
    return {
        "data_table_name": root.get("name", ""),
        "data_table_id": root.get("dataset_id", ""),
        "study_id": root.get("study_id", ""),
        "study_name": root.get("study_name"),
        "participant_set": root.get("participant_set"),
        "date_created": root.get("date_created"),
        "description": _text(root.find("description")),
        "variables": variables,
    }


def _strip_phv_suffix(vid: str) -> str:
    """Reduce a var_report-flavored variable id to the bare phv form.

    ``phv00124545.v4.p2`` → ``phv00124545.v4``.
    """
    return re.sub(r"\.p\d+$", "", vid)


def _merge(data_dict: dict, var_report: dict | None) -> dict:
    """Merge a data_dict and an optional var_report into a VariableDigest."""
    if var_report is None:
        merged_vars = data_dict["variables"]
        return {
            "data_table_id": data_dict.get("data_table_id", ""),
            "study_id": data_dict.get("study_id", ""),
            "participant_set": data_dict.get("participant_set"),
            "date_created": data_dict.get("date_created"),
            "description": data_dict.get("description"),
            "variables": merged_vars,
        }

    # Index var_report rows by bare phv id.
    vr_by_phv = {
        _strip_phv_suffix(v["id"]): v for v in var_report.get("variables", [])
    }

    merged_vars = []
    for dv in data_dict["variables"]:
        bare = _strip_phv_suffix(dv["id"])
        vr = vr_by_phv.get(bare, {})
        merged = {
            "id": dv["id"],
            "name": dv["name"],
            # Description: data_dict wins; var_report is fallback.
            "description": dv.get("description") or vr.get("description"),
            "reported_type": dv.get("reported_type") or vr.get("reported_type"),
            "calculated_type": vr.get("calculated_type"),
            "values": dv.get("values", []),
            "min": vr.get("min"),
            "max": vr.get("max"),
        }
        merged_vars.append(merged)

    return {
        "data_table_id": data_dict.get("data_table_id", "")
        or var_report.get("data_table_id", ""),
        "study_id": data_dict.get("study_id", "")
        or var_report.get("study_id", ""),
        "participant_set": data_dict.get("participant_set")
        or var_report.get("participant_set"),
        "date_created": data_dict.get("date_created")
        or var_report.get("date_created"),
        "data_table_name": var_report.get("data_table_name"),
        "study_name": var_report.get("study_name"),
        "description": data_dict.get("description") or var_report.get("description"),
        "variables": merged_vars,
    }


def parse_dbgap_digest(
    data_dict_path: str | Path,
    var_report_path: str | Path | None = None,
) -> dict:
    """Parse a dbGaP digest pair into a merged VariableDigest dict.

    Parameters
    ----------
    data_dict_path : path-like
        Path to the dbGaP ``*.data_dict.xml`` file. Required.
    var_report_path : path-like or None
        Path to the matching ``*.var_report.xml`` file. Optional;
        when provided, enriches the merged digest with empirical
        ``calculated_type`` and ``min``/``max`` per variable.

    Returns
    -------
    dict
        Structured ``VariableDigest`` form expected by the
        ``dbgap_to_dd`` trans-spec.
    """
    data_dict = _parse_data_dict(Path(data_dict_path))
    var_report = (
        _parse_var_report(Path(var_report_path)) if var_report_path else None
    )
    return _merge(data_dict, var_report)


def _strip_nulls(obj: Any) -> Any:
    """Recursively drop dict entries with None values and empty lists."""
    if isinstance(obj, dict):
        cleaned = {k: _strip_nulls(v) for k, v in obj.items() if v is not None}
        return {k: v for k, v in cleaned.items() if not (isinstance(v, (dict, list)) and not v)}
    if isinstance(obj, list):
        return [_strip_nulls(x) for x in obj]
    return obj


def dbgap_to_dd(
    data_dict_path: str | Path,
    var_report_path: str | Path | None = None,
) -> dict:
    """Translate a dbGaP digest pair into the canonical DD format.

    Parameters
    ----------
    data_dict_path : path-like
        Path to ``*.data_dict.xml``. Required.
    var_report_path : path-like or None
        Path to the matching ``*.var_report.xml``. Optional but
        recommended — provides empirical bounds for numeric variables
        and the ``calculated_type`` fallback used when data_dict's
        ``<type>`` is empty or ambiguous.

    Returns
    -------
    dict
        A canonical Data Dictionary matching
        ``schema_automator/metamodels/data_dictionary.yaml``.
    """
    source = parse_dbgap_digest(data_dict_path, var_report_path)
    spec = load_specification(str(_DBGAP_TO_DD_SPEC))
    source_sv = SchemaView(str(_DBGAP_SCHEMA))
    target_sv = SchemaView(str(_DD_SCHEMA))
    tr = ObjectTransformer(source_schemaview=source_sv, specification=spec)
    tr.target_schemaview = target_sv
    return _strip_nulls(tr.map_object(source, source_type="VariableDigest"))


def dbgap_output_filename(digest: dict, *, suffix: str = "yaml") -> str:
    """Build a stable output filename ``<phs>.<pht>.dd.<suffix>``.

    Matches the convention used by dm-bip's pipeline.
    """
    phs = (digest.get("study_id") or "unknown_phs").split(".")[0]
    pht = (digest.get("data_table_id") or "unknown_pht").split(".")[0]
    return f"{phs}.{pht}.dd.{suffix}"
