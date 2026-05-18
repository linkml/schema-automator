"""REDCap data dictionary adapter.

Translates between the REDCap data dictionary CSV format (as exported
from a REDCap project) and schema-automator's canonical Data Dictionary
format. See issue #204.
"""

from schema_automator.adapters.redcap.adapter import (
    dd_to_redcap,
    load_redcap_csv,
    redcap_to_dd,
)

__all__ = ["redcap_to_dd", "dd_to_redcap", "load_redcap_csv"]
