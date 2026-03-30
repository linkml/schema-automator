from importlib import metadata

try:
    __version__ = metadata.version(__package__)
except metadata.PackageNotFoundError:
    __version__ = "0.0.0"  # pragma: no cover

_LAZY_IMPORTS = {
    # annotators
    "SchemaAnnotator": "schema_automator.annotators.schema_annotator",
    "JsonLdAnnotator": "schema_automator.annotators.jsonld_annotator",
    "LLMAnnotator": "schema_automator.annotators.llm_annotator",
    # importers
    "JsonSchemaImportEngine": "schema_automator.importers.jsonschema_import_engine",
    "OwlImportEngine": "schema_automator.importers.owl_import_engine",
    "DOSDPImportEngine": "schema_automator.importers.dosdp_import_engine",
    "FrictionlessImportEngine": "schema_automator.importers.frictionless_import_engine",
    "CADSRImportEngine": "schema_automator.importers.cadsr_import_engine",
    "XsdImportEngine": "schema_automator.importers.xsd_import_engine",
    "KwalifyImportEngine": "schema_automator.importers.kwalify_import_engine",
    "DbmlImportEngine": "schema_automator.importers.dbml_import_engine",
    "RdfsImportEngine": "schema_automator.importers.rdfs_import_engine",
    "SqlImportEngine": "schema_automator.importers.sql_import_engine",
    "TableImportEngine": "schema_automator.importers.tabular_import_engine",
    # generalizers
    "CsvDataGeneralizer": "schema_automator.generalizers.csv_data_generalizer",
    "JsonDataGeneralizer": "schema_automator.generalizers.json_instance_generalizer",
    "RdfDataGeneralizer": "schema_automator.generalizers.rdf_data_generalizer",
    "PandasDataGeneralizer": "schema_automator.generalizers.pandas_generalizer",
    "TomlDataGeneralizer": "schema_automator.generalizers.toml_instance_generalizer",
}


def __getattr__(name):
    if name in _LAZY_IMPORTS:
        import importlib
        module = importlib.import_module(_LAZY_IMPORTS[name])
        return getattr(module, name)
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


__all__ = list(_LAZY_IMPORTS.keys())
