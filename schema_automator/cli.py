"""
Command Line Interface to Schema Automator
-----------------------------

"""
import logging
import os
from pathlib import Path

import click


import pandas as pd

import yaml
from linkml_runtime.linkml_model import SchemaDefinition
from oaklib.selector import get_implementation_from_shorthand

from schema_automator import JsonLdAnnotator, FrictionlessImportEngine
from schema_automator.annotators import llm_annotator
from schema_automator.annotators.schema_annotator import SchemaAnnotator
from schema_automator.generalizers.csv_data_generalizer import CsvDataGeneralizer
from schema_automator.generalizers.generalizer import DEFAULT_CLASS_NAME, DEFAULT_SCHEMA_NAME
from schema_automator.generalizers.pandas_generalizer import PandasDataGeneralizer
from schema_automator.importers.cadsr_import_engine import CADSRImportEngine
from schema_automator.importers.dosdp_import_engine import DOSDPImportEngine
from schema_automator.generalizers.json_instance_generalizer import JsonDataGeneralizer
from schema_automator.importers.jsonschema_import_engine import JsonSchemaImportEngine
from schema_automator.importers.kwalify_import_engine import KwalifyImportEngine
from schema_automator.importers.owl_import_engine import OwlImportEngine
from schema_automator.generalizers.rdf_data_generalizer import RdfDataGeneralizer
from schema_automator.importers.rdfs_import_engine import RdfsImportEngine
from schema_automator.importers.sql_import_engine import SqlImportEngine
from schema_automator.importers.tabular_import_engine import TableImportEngine
from schema_automator.utils.schemautils import write_schema
from schema_automator import __version__

input_option = click.option(
    "-i",
    "--input",
    help="path to input file"
)
output_option = click.option(
    "-o",
    "--output",
    help="path to output file or directory."
)
schema_name_option = click.option(
    '--schema-name',
    '-n',
    default=DEFAULT_SCHEMA_NAME,
    show_default=True,
    help='Schema name')
schema_id_option = click.option(
    '--schema-id',
    help='Schema id')
annotator_option = click.option(
    '--annotator',
    '-A',
    help='name of annotator to use for auto-annotating results. Must be an OAK selector')
use_attributes_option = click.option(
    "--use-attributes/--no-use-attributes",
    help="If true, use attributes over slots/slot_usage"
)
column_separator_option = click.option('--column-separator', '-s', default='\t', help='separator')

# generalizer options

downcase_header_option = click.option('--downcase-header/--no-downcase-header', default=False, help='if true make headers lowercase')
snakecase_header_option = click.option('--snakecase-header/--no-snakecase-header', default=False, help='if true make headers snakecase')
infer_foreign_keys_option = click.option('--infer-foreign-keys/--no-infer-foreign-keys', default=False, help='infer ranges/foreign keys')
enum_columns_option = click.option('--enum-columns', '-E', multiple=True, help='column(s) that is forced to be an enum')
enum_mask_columns_option = click.option('--enum-mask-columns', multiple=True, help='column(s) that are excluded from being enums')
max_enum_size_option = click.option('--max-enum-size', default=50, help='do not create an enum if more than max distinct members')
enum_threshold_option = click.option('--enum-threshold', default=0.1, help='if the number of distinct values / rows is less than this, do not make an enum')


@click.group()
@click.option("-v", "--verbose",
              count=True,
              help="Set the level of verbosity")
@click.option("-q", "--quiet",
              help="Silence all diagnostics")
@click.version_option(__version__, "-V", "--version")
def main(verbose: int, quiet: bool):
    """Run the LinkML Schema Automator Command Line.

    A subcommand must be passed, for example:

        schemauto SUBCOMMAND [OPTIONS] ARGUMENTS

    To see logging or debugging info, the verbosity
    flag should be specified BEFORE the subcommand:

        schemauto -vv SUBCOMMAND [OPTIONS] ARGUMENTS
    """
    logger = logging.getLogger()
    if verbose >= 2:
        logger.setLevel(logging.DEBUG)
    elif verbose == 1:
        logger.setLevel(logging.INFO)
    else:
        logger.setLevel(logging.WARNING)
    if quiet:
        logger.setLevel(logging.ERROR)
    logging.info(f"Log level={verbose}")


@main.command()
@click.argument('tsvfile')  # input TSV (must have column headers
@output_option
@schema_name_option
@annotator_option
@click.option('--class-name', '-c', default=DEFAULT_CLASS_NAME, help='Core class name in schema')
@column_separator_option
@downcase_header_option
@snakecase_header_option
@enum_columns_option
@enum_threshold_option
@max_enum_size_option
@click.option('--data-dictionary-row-count',
              type=click.INT,
              help='rows that provide metadata about columns')
@click.option('--robot/--no-robot', default=False, help='set if the TSV is a ROBOT template')
@click.option('--pandera/--no-pandera', default=False, help='set to use panderas as inference engine')
def generalize_tsv(tsvfile, output, class_name, schema_name, pandera: bool, annotator, **kwargs):
    """
    Generalizes from a single TSV file to a single-class schema

    See :ref:`generalizers` for more on the generalization framework

    Example:

        ``schemauto generalize-tsv --class-name Person --schema-name PersonInfo my/data/persons.tsv``
    """
    kwargs = {k:v for k, v in kwargs.items() if v is not None}
    if pandera:
        ie = PandasDataGeneralizer(**kwargs)
    else:
        ie = CsvDataGeneralizer(**kwargs)
    schema = ie.convert(tsvfile, class_name=class_name, schema_name=schema_name)
    if annotator:
        impl = get_implementation_from_shorthand(annotator)
        sa = SchemaAnnotator(impl)
        schema = sa.annotate_schema(schema)
    write_schema(schema, output)


@main.command()
@click.argument('tsvfiles', nargs=-1)  # input TSV (must have column headers
@output_option
@schema_name_option
@column_separator_option
@downcase_header_option
@snakecase_header_option
@enum_columns_option
@enum_threshold_option
@max_enum_size_option
@click.option('--robot/--no-robot', default=False, help='set if the TSV is a ROBOT template')
def generalize_tsvs(tsvfiles, output, schema_name, **kwargs):
    """
    Generalizes from a multiple TSV files to a multi-class schema

    See :ref:`generalizers` for more on the generalization framework

    This uses CsvDataGeneralizer.convert_multiple

    Example:

        ``schemauto generalize-tsvs --class-name Person --schema-name PersonInfo my/data/*.tsv``
    """
    ie = CsvDataGeneralizer(**kwargs)
    schema = ie.convert_multiple(tsvfiles, schema_name=schema_name)
    write_schema(schema, output)


@main.command()
@click.argument('url')  # input TSV (must have column headers
@output_option
@schema_name_option
@column_separator_option
@downcase_header_option
@snakecase_header_option
@enum_columns_option
@enum_threshold_option
@max_enum_size_option
@click.option('--class-name', '-c', default=DEFAULT_CLASS_NAME, help='Core class name in schema')
@click.option('--pandera/--no-pandera', default=False, help='set to use panderas as inference engine')
@click.option('--data-output', help='Path to file of downloaded data')
@click.option('--table-number',
              type=int,
              default=0,
              show_default=True,
              help='If URL has multiple tables, use this one (zero-based)')
def generalize_htmltable(url, output, class_name, schema_name, pandera: bool,
                         table_number: int, data_output,
                         **kwargs):
    """
    Generalizes from a table parsed from a URL

    Uses pandas/beautiful soup.

    Note: if the website cannot be accessed directly, you can download the HTML
    and pass in an argument of the form file:///absolute/path/to/file.html
    """
    dfs = pd.read_html(url)
    logging.info(f"{url} has {len(dfs)} tables")
    df = dfs[table_number]
    if data_output:
        df.to_csv(data_output, index=False, sep="\t")
    if pandera:
        ge = PandasDataGeneralizer(**kwargs)
    else:
        ge = CsvDataGeneralizer(**kwargs)
    schema = ge.convert_from_dataframe(df, class_name=class_name, schema_name=schema_name)
    write_schema(schema, output)


@main.command()
@click.argument('dpfiles', nargs=-1) ## input DOSDPs
@output_option
@schema_name_option
@click.option('--range-as-enums/--no-range-as-enums',
              default=True,
              help="Model range ontology classes as enums")
def import_dosdps(dpfiles, output, **args):
    """
    Imports DOSDP pattern YAML to a LinkML schema

    See :ref:`importers` for more on the importers framework

    Example:

        ``schemauto import-dosdps --range-as-enums patterns/*.yaml -o my-schema.yaml``
    """
    ie = DOSDPImportEngine()
    schema = ie.convert(dpfiles, **args)
    write_schema(schema, output)


@main.command()
@click.argument('db')
@output_option
@schema_name_option
def import_sql(db, output, **args):
    """
    Imports a schema by introspecting a relational database

    See :ref:`importers` for more on the importers framework
    """
    ie = SqlImportEngine()
    schema = ie.convert(db, **args)
    write_schema(schema, output)


@main.command()
@output_option
@schema_name_option
@click.option('--class-name', '-c', default=DEFAULT_CLASS_NAME, help='Core class name in schema')
@click.option('--data-output', help='Path to file of downloaded data')
@click.option('--element-type', help='E.g. class, enum')
@click.option('--parent', help='parent ID')
@click.option('--columns',
              required=True,
              help='comma-separated schemasheets descriptors of each column. Must be in same order')
@click.option('--table-number',
              type=int,
              default=0,
              show_default=True,
              help='If URL has multiple tables, use this one (zero-based)')
@click.argument('url')  # input TSV (must have column headers
def import_htmltable(url, output, class_name, schema_name, columns,
                         table_number: int, data_output,
                         **kwargs):
    """
    Imports from a table parsed from a URL using SchemaSheets

    Uses pandas/beautiful soup
    """
    dfs = pd.read_html(url)
    logging.info(f"{url} has {len(dfs)} tables")
    df = dfs[table_number]
    if data_output:
        df.to_csv(data_output, index=False, sep="\t")
    ie = TableImportEngine(columns=columns.split(","), **kwargs)
    schema = ie.import_from_dataframe(df)
    write_schema(schema, output)


@main.command()
@click.argument('input')
@output_option
@schema_name_option
@click.option('--container-class-name', default='Container', help="name of root class")
@click.option('--format', '-f', default='json', help="json or yaml (or json.gz or yaml.gz) or frontmatter")
@click.option('--enum-columns', '-E', multiple=True, help='column(s) that is forced to be an enum')
@click.option('--enum-mask-columns', multiple=True, help='column(s) that are excluded from being enums')
@click.option('--max-enum-size', default=50, help='do not create an enum if more than max distinct members')
@click.option('--enum-threshold', default=0.1, help='if the number of distinct values / rows is less than this, do not make an enum')
@click.option('--omit-null/--no-omit-null', default=False, help="if true, ignore null values")
@click.option('--inlined-map', multiple=True, help="SLOT_NAME.KEY pairs indicating which slots are inlined as dict")
@click.option('--depluralize/--no-depluralized',
              default=True,
              show_default=True,
              help="Auto-depluralize class names to singular form")
def generalize_json(input, output, schema_name, depluralize: bool, format, omit_null, inlined_map, **kwargs):
    """
    Generalizes from a JSON file to a schema

    See :ref:`generalizers` for more on the generalization framework

    Example:

        ``schemauto generalize-json my/data/persons.json -o my.yaml``
    """
    ie = JsonDataGeneralizer(omit_null=omit_null, depluralize_class_names=depluralize)
    if inlined_map:
        ie.inline_as_dict_slot_keys = dict([tuple(x.split(".")) for x in inlined_map])
    schema = ie.convert(input, format=format, **kwargs)
    write_schema(schema, output)


@main.command()
@click.argument('input')
@output_option
@schema_name_option
@click.option('--container-class-name', default='Container', help="name of root class")
@click.option('--enum-columns', '-E', multiple=True, help='column(s) that is forced to be an enum')
@click.option('--enum-mask-columns', multiple=True, help='column(s) that are excluded from being enums')
@click.option('--max-enum-size', default=50, help='do not create an enum if more than max distinct members')
@click.option('--enum-threshold', default=0.1, help='if the number of distinct values / rows is less than this, do not make an enum')
@click.option('--omit-null/--no-omit-null', default=False, help="if true, ignore null values")
def generalize_toml(input, output, schema_name, omit_null, **kwargs):
    """
    Generalizes from a TOML file to a schema

    See :ref:`generalizers` for more on the generalization framework

    Example:

        ``schemauto generalize-toml my/data/conf.toml -o my.yaml``
    """
    ie = JsonDataGeneralizer(omit_null=omit_null)
    schema = ie.convert(input, format='toml', **kwargs)
    write_schema(schema, output)


@main.command()
@click.argument('input')
@output_option
@schema_name_option
@use_attributes_option
@click.option(
    "--is-openapi/--no-is-openapi",
    default=False,
    show_default=True,
    help="If true, use OpenAPI schema style"
)
@click.option("--import-project/--no-import-project",
              help="If true, then the input path should be a directory with multiple schema files")
@click.option('--format', '-f', default='json', help='JSON Schema format - yaml or json')
def import_json_schema(input, output, import_project: bool, schema_name, format, **kwargs):
    """
    Imports from JSON Schema to LinkML

    See :ref:`importers` for more on the importer framework

    Example:

        ``schemauto import-json-schema my/schema/personinfo.schema.json``
    """
    ie = JsonSchemaImportEngine(**kwargs)
    if not import_project:
        schema = ie.convert(input, name=schema_name, format=format)
        write_schema(schema, output)
    else:
        if output is None:
            raise ValueError(f"You must pass an export directory with --output")
        ie.import_project(input, output, name=schema_name, format=format)


@main.command()
@click.argument('input')
@output_option
@schema_name_option
@use_attributes_option
def import_kwalify(input, output, schema_name, **kwargs):
    """
    Imports from Kwalify Schema to LinkML

    See :ref:`importers` for more on the importer framework

    Example:

        ``schemauto import-kwalify my/schema/personinfo.kwalify.yaml``
    """
    ie = KwalifyImportEngine(**kwargs)
    schema = ie.convert(input, output, name=schema_name, format=format)
    write_schema(schema, output)

@main.command()
@click.argument('input')
@output_option
@schema_name_option
@schema_id_option
def import_frictionless(input, output, schema_name, schema_id, **kwargs):
    """
    Imports from Frictionless data package to LinkML

    See :ref:`importers` for more on the importer framework

    Example:

        ``schemauto import-frictionless cfde.package.json``
    """
    ie = FrictionlessImportEngine(**kwargs)
    schema = ie.convert(input, name=schema_name, id=schema_id)
    write_schema(schema, output)


@main.command()
@output_option
@schema_name_option
@schema_id_option
@click.argument('input')
def import_cadsr(input, output, schema_name, schema_id, **kwargs):
    """
    Imports from CADSR CDE JSON API output to LinkML

    See :ref:`importers` for more on the importer framework

    Example:

        ``schemauto import-cadsr "cdes/*.json"``
    """
    ie = CADSRImportEngine()
    paths = [str(gf.absolute())  for gf in Path().glob(input) if gf.is_file()]
    schema = ie.convert(paths, name=schema_name, id=schema_id)
    write_schema(schema, output)


@main.command()
@click.argument('owlfile')
@output_option
@schema_name_option
@click.option('--identifier', '-I', help="Slot to use as identifier")
@click.option('--model-uri', help="Model URI prefix")
@click.option('--output', '-o', help="Path to saved yaml schema")
def import_owl(owlfile, output, **args):
    """
    Import an OWL ontology to LinkML

    Note:
         - this works best for "schema-style" ontologies
         - input must be in functional syntax

    See :ref:`importers` for more on the importer framework

    For a list of caveats on LinkML to OWL mapping, see:

    - https://linkml.io/linkml/generators/owl.html

    Example:

        ``schemauto import-owl prov.ofn -o my.yaml``
    """
    sie = OwlImportEngine()
    schema = sie.convert(owlfile, **args)
    write_schema(schema, output)


@main.command()
@click.argument('rdfsfile')
@output_option
@schema_name_option
@click.option('--input-type', '-I',
              default='turtle',
              help="Input format, eg. turtle")
@click.option('--identifier', '-I', help="Slot to use as identifier")
@click.option('--model-uri', help="Model URI prefix")
@click.option('--metamodel-mappings',
              help="Path to metamodel mappings YAML dictionary")
@click.option('--output', '-o', help="Path to saved yaml schema")
def import_rdfs(rdfsfile, output, metamodel_mappings, **args):
    """
    Import an RDFS schema to LinkML

    Example:

        schemauto import-rdfs prov.rdfs.ttl -o prov.yaml
    """
    mappings_obj = None
    if metamodel_mappings:
        with open(metamodel_mappings) as f:
            mappings_obj = yaml.safe_load(f)
    sie = RdfsImportEngine(initial_metamodel_mappings=mappings_obj)
    schema = sie.convert(rdfsfile, **args)
    write_schema(schema, output)

@main.command()
@click.argument('rdffile')
@output_option
@click.option('--dir', '-d', required=True)
def generalize_rdf(rdffile, dir, output, **args):
    """
    Generalizes from an RDF file to a schema

    See :ref:`generalizers` for more on the generalization framework

    The input must be in turtle

    Example:

        ``schemauto generalize-rdf my/data/persons.ttl``
    """
    sie = RdfDataGeneralizer()
    if not os.path.exists(dir):
        os.makedirs(dir)
    schema_dict = sie.convert(rdffile, dir=dir, format='ttl')
    write_schema(schema_dict, output)


@main.command()
@click.argument('schema')
@click.option('--curie-only/--no-curie-only',
              default=False,
              show_default=True,
              help="if set, only use results that are mapped to CURIEs")
@click.option('--input',
              '-i',
              help="OAK input ontology selector")
@output_option
def annotate_schema(schema: str, input: str, output: str, **kwargs):
    """
    Annotate all elements of a schema.

    This uses OAK (https://incatools.github.io/ontology-access-kit),
    and you can provide any OAK backend that supports text annotation.
    
    At this time, the best choice is likely the bioportal backend
    
    Example:
    
        ``schemauto annotate-schema -i bioportal: my-schema.yaml -o annotated.yaml``
        
    This will require you setting the API key via OAK - see OAK docs.
        
    You can specify a specific ontology
    
        ``schemauto annotate-schema -i bioportal:ncbitaxon my-schema.yaml -o annotated.yaml``

    In future OAK will support a much wider variety of annotators including:
    
       - OLS
       - SciSpacy
       - NLTK
       - OGER

    To see all possible selectors, see the OAK docs:
    
      - https://incatools.github.io/ontology-access-kit/selectors.html
    """
    impl = get_implementation_from_shorthand(input)
    annr = SchemaAnnotator(impl, **kwargs)
    schema = annr.annotate_schema(schema)
    write_schema(schema, output)

@main.command()
#@main.command()
@click.argument('schema')
@click.option('--input', '-i', help="OAK input ontology selector")
@click.option('--annotate/--no-annotate', default=True, help="If true, annotate the schema")
@output_option
def enrich_using_ontology(schema: str, input: str, output: str, annotate: bool, **args):
    """
    Enrich a schema using an ontology.

    Here, "enrich" means copying over metadata from the ontology to the schema.
    For example, if the schema has a class "Gene" that is mapped to a SO class for "gene",
    then calling this command will copy the SO class definition to the schema class.

    This will use OAK to add additional metadata using uris and mappings in the schema.

    See the OAK docs for options for which annotators to use; examples include:

     - bioportal:   # (include the colon) any ontology in bioportal

     - bioportal:umls   # a specific ontology in bioportal

     - my.obo       # any local OBO file

     - sqlite:obo:cl   # a specific OBO file or semsql registered ontology

    For example, if your schema has a class with a mapping to a SO class,
    then the definition of that will be copied to the class description.

    Example:

        ``schemauto enrich-using-ontology -i bioportal: my-schema.yaml -o my-enriched.yaml``

    If your schema has no mappings you can use --annotate to add them

    Example:

        ``schemauto enrich-using-ontology -i so.obo --annotate my-schema.yaml -o my-enriched.yaml --annotate``
    """
    impl = get_implementation_from_shorthand(input)
    annr = SchemaAnnotator(impl)
    logging.info(f"Enriching: {schema}")
    if annotate:
        schema = annr.annotate_schema(schema)
    schema = annr.enrich(schema)
    write_schema(schema, output)


@main.command()
@click.option('--model', '-m', help="Name of model")
@output_option
@click.argument('schema')
def enrich_using_llm(schema: str, model: str, output: str, **args):
    """
    Enrich a schema using an LLM.

    Example:

        schemauto enrich-using-llm -m gpt-4-turbo my-schema.yaml -o my-enriched.yaml

    This will enrich the schema by adding missing description fields. In future
    other enrichments may be possible.

    Note for this to work, you will need to have LLM installed as an extra.

    Example:

        ``pip install schema-automator[llm]``

    """
    logging.info(f"Enriching: {schema}")
    schema = llm_annotator.enrich_using_llm(schema, model)
    write_schema(schema, output)


@main.command()
@click.argument('schema')
@output_option
def annotate_using_jsonld(schema: str, output: str, **args):
    """
    Annotates a schema using a Json-LD context file
    """
    annr = JsonLdAnnotator()
    schemadef = SchemaDefinition(schema)
    annr.annotate_schema(schemadef)
    write_schema(schemadef, output)


if __name__ == "__main__":
    main()
