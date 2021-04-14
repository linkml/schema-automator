from __future__ import print_function
import json
import sys
import urllib.error
import urllib.parse
import urllib.request
from sys import stdout
from strsimpy.cosine import Cosine
import yaml
import re
from yaml import SafeDumper
import click

# import os
# import requests
# from curieutil import CurieUtil
# from prefixcommons import contract_uri

# go_prefixes_url = 'https://raw.githubusercontent.com/prefixcommons/biocontext/master/registry/go_context.jsonld'
# r = requests.get(go_prefixes_url)
#
# mapping = CurieUtil.parseContext(r.json())
# curie = CurieUtil(mapping)

# WRITES OUTPUT TO STDOUT

# 2021-04-14
# CURIE HANDLING
# enums besides species
# different spreadsheet input
# would go through Chris' initial inference stage
# or try from postgres?
# ask for ontology target if no code_set asserted
# may not be retaining original yaml ordering

# low priority
# is cosine the best string distance for this task?


# TODO gets bioportal key from $ENUMENRICH_BPKEY or --bpkey
#   complains if neither is set but doesn't tell user to use $ENUMENRICH_BPKEY
#   UNLESS --help is explicitly invoked

# TODO writing output to STDOUT
#   add option for writing directly to file?

# TODO overwrites meanings if they already exist

# TODO also try RunNER (and OLS?)

# TODO handling of prefix resolution could be improved
#   might want to map from bioportal http://purl.bioontology.org/ontology/NCBITAXON/
#   to prefix NCBItaxon: to when writing meanings
#   but include a different mapping, eg
#   from NCBItaxon: to OBO EXAMPLE
#   in the prefix assertion block

# TODO assuming at least one prefix asserted in linkml model
# TODO just import prefixes from somewhere else?

# TODO interpret code_set in order to determine target ontologies?
#   what if there is no asserted code_set?
#   what about ontoprefix click option?

# TODO regex = re.compile('|'.join(map(re.escape, substrings)))
#     Expected type 'Iterable[Union[Union[str, bytes], Any]]'
#     (matched generic type 'Iterable[_T1]'), got 'List[Sized]' instead

# TODO make longest_only a parameter?

# TODO not handling unauthorized access to bioportal yet
#   bad API key, etc
#   or any other REST failures

# inspired by
#   https://github.com/ncbo/ncbo_rest_sample_code/blob/master/python/python3/annotate_text.py
# see also
#   https://github.com/biolink/biolinkml/blob/master/biolinkml/generators/infer_model.py
#   which uses zooma

# https://stackoverflow.com/a/14981125/3860847
def eprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)


def get_bp_json(url, bpkey):
    opener = urllib.request.build_opener()
    opener.addheaders = [('Authorization', 'apikey token=' + bpkey)]
    return json.loads(opener.open(url).read())


def extract_mapping_items(annotation_json, bpkey):
    for result in annotation_json:
        # assuming a single annotation because requesting longest match only
        annotated_text = result['annotations'][0]
        try:
            class_details = get_bp_json(result['annotatedClass']['links']['self'], bpkey)
        except urllib.error.HTTPError:
            eprint(f'Error retrieving {result["annotatedClass"]["@id"]}')
            continue
        result_dict = {'text': annotated_text['text'], 'matchType': annotated_text['matchType'],
                       'id': class_details['@id'], 'prefLabel': class_details['prefLabel']}
        return result_dict


# https://gist.github.com/carlsmith/b2e6ba538ca6f58689b4c18f46fef11c
def replace(string, substitutions):
    substrings = sorted(substitutions, key=len, reverse=True)
    regex = re.compile('|'.join(map(re.escape, substrings)))
    # Expected type 'Iterable[Union[Union[str, bytes], Any]]'
    #   (matched generic type 'Iterable[_T1]'), got 'List[Sized]' instead
    return regex.sub(lambda match: substitutions[match.group(0)], string)


@click.command()
# what's the right term
@click.option('--modelfile', '-f',
              # default='inferred-models/synbio.yaml',
              help='Path to a YAML linkml file containing enumerated values.',
              required=True,
              type=click.Path(exists=True),
              # show_default=True
              )
@click.option('--enum_source', '-e',
              # default='species_enum',
              help='In which part of the model do you want to look for enums?.',
              required=True,
              type=str,
              # show_default=True
              )
@click.option('--ontoprefix', '-p',
              # default='NCBITAXON',
              help='What BioPortal ontology do you want to use as a reference?.',
              required=True,
              type=str,
              # show_default=True
              )
@click.option('--bpkey', '-k',
              help='API key for BioPortal or OntoPortal endpoint. Taken from $ENUMENRICH_BPKEY by default.',
              envvar='ENUMENRICH_BPKEY',
              required=True,
              type=str)
@click.option('--bpendpoint', '-e',
              default="http://data.bioontology.org",
              help='URL for a BioPortal or OntoPortal API endpoint.',
              required=True,
              type=str,
              show_default=True)
@click.option('--maxdist', '-x',
              help='Maximum cosine distance between input and BioPortal PREFERRED match.',
              default=0.1,
              required=True,
              type=float,
              show_default=True)
@click.option('--delim',
              default='\t',
              help='Delimiter for verbose tabular progress report. Defaults to horizontal tab.',
              required=True,
              type=str,
              show_default=False)
@click.option('--quiet', '-q',
              is_flag=True,
              help="Don't send BioPortal progress to STDOUT.")
def clickmain(bpendpoint, bpkey, maxdist, delim, modelfile, enum_source, ontoprefix, quiet):
    # # don't emit nulls in YAML
    # # but is this really necessary?
    SafeDumper.add_representer(
        type(None),
        lambda dumper, value: dumper.represent_scalar(u'tag:yaml.org,2002:null', '')
    )

    verbose = not quiet

    # not necessary if always writing to STDOUT
    # modelfile_bits = os.path.splitext(modelfile)

    with open(modelfile) as file:
        inferred_model = yaml.load(file, Loader=yaml.FullLoader)

    # # interpret code_set in order to determine target ontologies?
    # # what if there is no asserted code_set?
    # ontoprefix = inferred_model['enums'][enum_source]['code_set']
    ontoprefix = str(ontoprefix).upper()

    # maybe there's a better way of doing this?
    #   a IRI <-> CURIE converter in the BBOP ecosystem,
    #   or some other public package?
    # OOPS http://purl.bioontology.org/ontology/NCBITAXON/ is the base for NCBI Taxonomy in BioPortal's eyes
    # But not in OBO's
    iri_curie_substitutions = {'http://purl.bioontology.org/ontology/NCBITAXON/': "NCBItaxon:"}

    # assuming at least one prefix has been defined
    asserted_prefixes = inferred_model['prefixes']

    inferred_enums = inferred_model['enums'][enum_source]['permissible_values']

    # for key in inferred_enums.keys():
    #     print(key)

    # eprint(inferred_enums)

    for text_line in inferred_enums:
        tidied_line = re.sub(r'[_,.\-;@#?!&$]+ *', ' ', text_line)
        built_url = bpendpoint + '/annotator?longest_only=true&ontologies=' + ontoprefix + \
                    '&text=' + urllib.parse.quote(tidied_line)
        # make longest_only a parameter?
        #   if off,  extract_mapping_items will make multiple returns?
        bp_json = get_bp_json(built_url, bpkey)
        if len(bp_json) > 0:
            extracted_mapping_items = extract_mapping_items(bp_json, bpkey)
            cosine_obj = Cosine(1)
            input_used_dist = cosine_obj.distance(text_line.lower(), extracted_mapping_items['text'].lower())
            input_used_dist_str = '{:0.3f}'.format(input_used_dist)
            used_pref_dist = cosine_obj.distance(extracted_mapping_items['text'].lower(),
                                                 extracted_mapping_items['prefLabel'].lower())
            used_pref_dist_str = '{:0.3f}'.format(used_pref_dist)

            # for non-quiet/verbose reporting
            joined_mapping_items = delim.join(extracted_mapping_items.values())
            final_joined_mapping = text_line + '\t' + tidied_line + '\t' + joined_mapping_items + '\t' + \
                                   input_used_dist_str + '\t' + used_pref_dist_str
            # add meaning slots to the enums if a matches are found
            #   and the cosine distance is acceptable
            if input_used_dist < maxdist:
                curie = replace(str(extracted_mapping_items['id']), iri_curie_substitutions)
                inferred_enums[text_line] = {'meaning': curie}

        else:
            final_joined_mapping = text_line

        if verbose:
            eprint(final_joined_mapping)

    # not necessary if always writing to STDOUT
    # updated_yaml_file = modelfile_bits[0] + '_updated' + modelfile_bits[1]

    inferred_model['enums'][enum_source]['permissible_values'] = inferred_enums

    # eprint(inferred_model)
    yaml.safe_dump(inferred_model, stdout, default_flow_style=False)

    # TODO explicitly close in and out files
    # close SQLite connections (not relevant here)
    # TODO also resume support for writing directly to a file?
    # with open(updated_yaml_file, 'w') as file:
    #     yaml.safe_dump(inferred_model, file, default_flow_style=False)
    # yaml.safe_dump(inferred_model, stdout, default_flow_style=False)
    # doesn't even seem to need the default_flow_style=False


if __name__ == '__main__':
    clickmain(auto_envvar_prefix='ENUMENRICH')

# # add prefix declarations for iri_curie_substitutions
# for my_key, my_value in iri_curie_substitutions.items():
#     my_value = my_value[:-1]
#     my_value = my_value.lower()
#     defined_keys = list(asserted_prefixes.keys())
#     if my_value not in defined_keys:
#         asserted_prefixes[my_value] = my_key
# print(asserted_prefixes)
# inferred_model['prefixes'] = asserted_prefixes
