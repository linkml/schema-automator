# This module previously provided TableImportEngine, which used schemasheets'
# SchemaMaker to import HTML tables into LinkML schemas. The schemasheets
# dependency was removed because the project has stagnated and its transitive
# deps cause packaging issues under uv.
#
# The column-mapping approach (mapping spreadsheet columns to LinkML schema
# elements) is planned to be reimplemented natively as part of the data
# dictionary input format work (see #191).

raise NotImplementedError(
    "TableImportEngine has been removed. "
    "The schemasheets dependency it relied on is no longer included. "
    "See https://github.com/linkml/schema-automator/issues/191"
)
