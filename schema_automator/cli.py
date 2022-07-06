"""
Command Line Interface to Schema Automator
-----------------------------

"""
import logging
import os
import click

import yaml
from linkml_runtime.linkml_model import SchemaDefinition
from oaklib.selector import get_resource_from_shorthand, get_implementation_from_shorthand

from schema_automator import JsonLdAnnotator
from schema_automator.annotators.schema_annotator import SchemaAnnotator
from schema_automator.generalizers.csv_data_generalizer import CsvDataGeneralizer
from schema_automator.importers.dosdp_import_engine import DOSDPImportEngine
from schema_automator.generalizers.json_instance_generalizer import JsonDataGeneralizer
from schema_automator.importers.jsonschema_import_engine import JsonSchemaImportEngine
from schema_automator.importers.owl_import_engine import OwlImportEngine
from schema_automator.generalizers.rdf_data_generalizer import RdfDataGeneralizer
from schema_automator.utils.schemautils import minify_schema, write_schema

input_option = click.option(
    "-i",
    "--input",
    help="path to input file"
)
output_option = click.option(
    "-o",
    "--output",
    help="path to output file."
)
schema_name_option = click.option(
    '--schema-name',
    '-n',
    default='example',
    show_default=True,
    help='Schema name')


@click.group()
@click.option("-v", "--verbose",
              count=True,
              help="Set the level of verbosity")
@click.option("-q", "--quiet",
              help="Silence all diagnostics")
def main(verbose: int, quiet: bool):
    """Run the LinkML Schema Automator Command Line.

    A subcommand must be passed, for example:

        schemauto -v SUBCOMMAND [OPTIONS] ARGUMENTS
    """
    if verbose >= 2:
        logging.basicConfig(level=logging.DEBUG)
    elif verbose == 1:
        logging.basicConfig(level=logging.INFO)
    else:
        logging.basicConfig(level=logging.WARNING)
    if quiet:
        logging.basicConfig(level=logging.ERROR)


@main.command()
@click.argument('tsvfile')  # input TSV (must have column headers
@output_option
@schema_name_option
@click.option('--class-name', '-c', default='example', help='Core class name in schema')
@click.option('--column-separator', '-s', default='\t', help='separator')
@click.option('--downcase-header/--no-downcase-header', default=False, help='if true make headers lowercase')
@click.option('--enum-columns', '-E', multiple=True, help='column that is forced to be an enum')
@click.option('--robot/--no-robot', default=False, help='set if the TSV is a ROBOT template')
def generalize_tsv(tsvfile, output, class_name, schema_name, **kwargs):
    """
    Generalizes from a single TSV file to a single-class schema

    See :ref:`generalizers` for more on the generalization framework

    Example:

        schemauto generalize-tsv --class-name Person --schema-name PersonInfo my/data/persons.tsv
    """
    ie = CsvDataGeneralizer(**kwargs)
    schema = ie.convert(tsvfile, class_name=class_name, schema_name=schema_name)
    write_schema(schema, output)


@main.command()
@click.argument('tsvfiles', nargs=-1)  # input TSV (must have column headers
@output_option
@schema_name_option
@click.option('--column-separator', '-s', default='\t', help='separator')
@click.option('--downcase-header/--no-downcase-header', default=False, help='if true make headers lowercase')
@click.option('--infer-foreign-keys/--no-infer-foreign-keys', default=False, help='infer ranges/foreign keys')
@click.option('--enum-columns', '-E', multiple=True, help='column(s) that is forced to be an enum')
@click.option('--enum-mask-columns', multiple=True, help='column(s) that are excluded from being enums')
@click.option('--max-enum-size', default=50, help='do not create an enum if more than max distinct members')
@click.option('--enum-threshold', default=0.1, help='if the number of distinct values / rows is less than this, do not make an enum')
@click.option('--robot/--no-robot', default=False, help='set if the TSV is a ROBOT template')
def generalize_tsvs(tsvfiles, output, schema_name, **kwargs):
    """
    Generalizes from a multiple TSV files to a multi-class schema

    See :ref:`generalizers` for more on the generalization framework

    This uses :ref:`CsvDataGeneralizer.convert_multiple`

    Example:

        schemauto generalize-tsvs --class-name Person --schema-name PersonInfo my/data/*.tsv
    """
    ie = CsvDataGeneralizer(**kwargs)
    schema = ie.convert_multiple(tsvfiles, schema_name=schema_name)
    write_schema(schema, output)


@main.command()
@click.argument('dpfiles', nargs=-1) ## input DOSDPs
@output_option
@schema_name_option
@click.option('--range-as-enum/--no-range-as-enums',
              default=True,
              help="Model range ontology classes as enums")
def import_dosdps(dpfiles, output, **args):
    """
    Imports DOSDP pattern YAML to a LinkML schema

    See :ref:`importers` for more on the importers framework
    """
    ie = DOSDPImportEngine()
    schema = ie.convert(dpfiles, **args)
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
def generalize_json(input, output, schema_name, format, omit_null, **kwargs):
    """
    Generalizes from a JSON file to a schema

    See :ref:`generalizers` for more on the generalization framework

    Example:

        schemauto generalize-json my/data/persons.json
    """
    ie = JsonDataGeneralizer(omit_null=omit_null)
    schema = ie.convert(input, format=format, **kwargs)
    write_schema(schema, output)


@main.command()
@click.argument('input')
@output_option
@schema_name_option
@click.option('--format', '-f', default='json', help='JSON Schema format - yaml or json')
def import_json_schema(input, output, schema_name, format, **args):
    """
    Imports from JSON Schema to LinkML

    See :ref:`importers` for more on the importer framework

    Example:

        schemauto import-json-schema my/schema/personinfo.schema.json
    """
    loader = JsonSchemaImportEngine()
    schema = loader.load(input, name=schema_name, format=format)
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

    Note this works best for "schema-style" ontologies

    See :ref:`importers` for more on the importer framework

    Note: input must be in functional syntax
    """
    sie = OwlImportEngine()
    schema = sie.convert(owlfile, **args)
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

        schemauto generalize-json my/data/persons.ttl
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
@click.option('--input', '-i', help="OAK input ontology selector")
@output_option
def annotate_schema(schema: str, input: str, output: str, curie_only: bool, **args):
    """
    Annotate all elements of a schema

    Requires Bioportal API key
    """
    impl = get_implementation_from_shorthand(input)
    logging.basicConfig(level=logging.INFO)
    annr = SchemaAnnotator(impl)
    schema = annr.annotate_schema(schema, curie_only=curie_only)
    write_schema(schema, output)


@main.command()
@click.argument('schema')
@click.option('--input', '-i', help="OAK input ontology selector")
@output_option
def enrich_schema(schema: str, input: str, output: str, **args):
    """
    Annotate all elements of a schema

    Requires Bioportal API key
    """
    impl = get_implementation_from_shorthand(input)
    logging.basicConfig(level=logging.INFO)
    annr = SchemaAnnotator(impl)
    schema = annr.enrich(schema)
    write_schema(schema, output)


@main.command()
@click.argument('schema')
@output_option
def annotate_using_jsonld(schema: str, output: str, **args):
    """
    Annotates a schema using a Json-LD context file
    """
    logging.basicConfig(level=logging.INFO)
    annr = JsonLdAnnotator()
    schemadef = SchemaDefinition(schema)
    annr.annotate_schema(schemadef)
    write_schema(schemadef, output)


if __name__ == "__main__":
    main()
