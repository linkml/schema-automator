"""dbGaP variable digest adapter.

Translates between dbGaP variable digest XML (data_dict.xml +
optional var_report.xml) and schema-automator's canonical Data
Dictionary format. See issue #206.
"""

from schema_automator.adapters.dbgap.adapter import (
    dbgap_to_dd,
    parse_dbgap_digest,
)

__all__ = ["dbgap_to_dd", "parse_dbgap_digest"]
