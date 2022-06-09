import logging

import click
import yaml
from linkml_runtime import SchemaView
from linkml_runtime.dumpers import yaml_dumper
from linkml_runtime.linkml_model import SlotDefinitionName
from linkml_runtime.utils.introspection import package_schemaview
from linkml_runtime.utils.schema_as_dict import schema_as_dict, schema_as_yaml_dump

from schema_automator.utils.instance_extractor import InstanceView
from schema_automator.utils.schemautils import minify_schema


@click.command()
@click.argument('elements', nargs=-1)
@click.option('--mergeimports/--no-mergeimports', help="Merge imports closure")
@click.option('--input', '-i', help="Data input")
@click.option('--output', '-o', help="Path to saved yaml schema")
@click.option("-v", "--verbose", count=True)
def cli(elements, input, mergeimports, output, verbose: int, **args):
    """
    Extract from instance data
    """
    if verbose >= 2:
        logging.basicConfig(level=logging.DEBUG)
    elif verbose == 1:
        logging.basicConfig(level=logging.INFO)
    else:
        logging.basicConfig(level=logging.WARNING)
    metamodel_sv = package_schemaview('linkml_runtime.linkml_model.meta')
    input_sv = SchemaView(input)
    #schema = yaml_loader.load(source=input, target_class=SchemaDefinition)
    #print(yaml_dumper.dumps(root))
    if mergeimports:
        input_sv.merge_imports()
    input_schema = input_sv.schema
    iv = InstanceView(root=input_schema, schemaview=metamodel_sv)
    logging.info(f'Creating index')
    iv.create_index()
    subschema = iv.extract(list(elements),
                           preserve_slots=[SlotDefinitionName('name'),
                                           SlotDefinitionName('prefixes'),
                                           ])
    ys = schema_as_yaml_dump(subschema)
    if output:
        with open(output, 'w') as stream:
            stream.write(ys)
    else:
        print(ys)


if __name__ == '__main__':
    cli()



