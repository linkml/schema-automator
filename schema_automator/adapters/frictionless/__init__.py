"""Frictionless Table Schema adapter.

Translates between the Frictionless Table Schema specification
(https://specs.frictionlessdata.io/table-schema/) and schema-automator's
canonical Data Dictionary format. See issue #203.
"""

from schema_automator.adapters.frictionless.adapter import (
    dd_to_frictionless,
    frictionless_to_dd,
)

__all__ = ["frictionless_to_dd", "dd_to_frictionless"]
