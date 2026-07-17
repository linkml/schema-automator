"""Schema enrichers.

Modules in this package take an inferred LinkML ``SchemaDefinition`` and
overlay external metadata onto it — descriptions, semantic URIs, units,
permissible-value labels, constraints — producing a richer schema for
downstream validation and transformation tools.

The data-dictionary enricher (:mod:`.data_dictionary_enricher`) is the
primary entry point: it consumes a canonical data dictionary (as
defined in ``schema_automator/metamodels/data_dictionary.yaml``) and
merges it into an inferred schema. See umbrella issue #190.
"""

from schema_automator.enrichers.data_dictionary_enricher import (
    EnrichmentReport,
    enrich_with_data_dictionary,
)

__all__ = ["EnrichmentReport", "enrich_with_data_dictionary"]
