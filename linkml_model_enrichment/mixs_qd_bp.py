#!/usr/bin/env python3

from __future__ import print_function
import json
import sys
import urllib.error
import urllib.parse
import urllib.request
from strsimpy.cosine import Cosine
import yaml
import re
import os
import pandas as pds

# from sys import stdout
# from yaml import SafeDumper
# import click

# assuming that the biosample-analysis directory
# is a sibling of linkml-model-enrichment
modelfile = '../biosample-analysis/gensc.github.io/src/schema/mixs.yaml'
outputfile =
bpkey = os.getenv('ENUMENRICH_BPKEY')
# can be empty, a single ontology abbreviation, or a comma separate list
# case sensitive
# some BP ontology abbreviations aren't exactly what you'd expect
ontoprefix = 'ENVO,PATO,MESH,NCIT,LOINC,SNOMED,MPO,MEO,GAZ,GO,MVC,OBI,OMIT,PO,OCHV,GALEN,EFO,PMO'
ontoprefix = ''
bpendpoint = 'http://data.bioontology.org'
maxdist = 0.1
verbose = True
min_search_chars = 2


def eprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)


def read_yaml_model(modelfile_param):
    with open(modelfile_param) as file:
        inferred_model_param = yaml.load(file, Loader=yaml.FullLoader)
    return inferred_model_param


def get_enum_list(inferred_model_param):
    the_enums_param = list(inferred_model_param['enums'].keys())
    return the_enums_param


def case_fold_list_sort(input_list):
    output_list = input_list
    output_list.sort(key=str.casefold)
    return output_list


def get_one_enum_class(inferred_model_param, enum_class_param):
    inferred_enums = inferred_model_param['enums'][enum_class_param]['permissible_values']
    inferred_keys = list(inferred_enums.keys())
    inferred_keys.sort(key=str.casefold)
    return inferred_keys


def extract_mapping_items(annotation_json, bpkey_param):
    for result in annotation_json:
        # assuming a single annotation because requesting longest match only
        annotated_text = result['annotations'][0]
        try:
            class_details = get_bp_json(result['annotatedClass']['links']['self'], bpkey_param)
        except urllib.error.HTTPError:
            eprint(f'Error retrieving {result["annotatedClass"]["@id"]}')
            continue
        result_dict = {'text': annotated_text['text'], 'matchType': annotated_text['matchType'],
                       'id': class_details['@id'], 'prefLabel': class_details['prefLabel']}
        return result_dict


def get_bp_json(url, bpkey_param):
    opener = urllib.request.build_opener()
    opener.addheaders = [('Authorization', 'apikey token=' + bpkey_param)]
    return json.loads(opener.open(url).read())


def submit_bp_get_df(permitteds, min_search_chars_param, one_enum_param: object):
    result_list = []
    for orig_enum in permitteds:

        final_joined_mapping = dict(one_enum_param='', orig_enum='', tidied_enum='',
                                    orig_matched_dist='', matched_pref_dist='', matched_text='', matchType='',
                                    id='', prefLabel='')

        final_joined_mapping['one_enum_param'] = one_enum_param
        final_joined_mapping['orig_enum'] = orig_enum

        # strip punct
        # could also url encode?
        tidied_enum = re.sub(r'[_,.\-;@#?!&$ ]+', ' ', orig_enum)
        final_joined_mapping['tidied_enum'] = tidied_enum

        if len(tidied_enum) >= min_search_chars_param:
            built_url = bpendpoint + '/annotator?longest_only=true' + op_url_part + \
                        '&text=' + urllib.parse.quote(tidied_enum)
            # make longest_only a parameter?
            #   if off,  extract_mapping_items will make multiple returns?
            # print(built_url)
            bp_json = get_bp_json(built_url, bpkey)
            if len(bp_json) > 0:
                extracted_mapping_items = extract_mapping_items(bp_json, bpkey)
                # print(extracted_mapping_items)
                cosine_obj = Cosine(1)
                orig_matched_dist_num = cosine_obj.distance(orig_enum.lower(), extracted_mapping_items['text'].lower())
                orig_matched_dist = '{:0.3f}'.format(orig_matched_dist_num)
                matched_pref_dist_num = cosine_obj.distance(extracted_mapping_items['text'].lower(),
                                                            extracted_mapping_items['prefLabel'].lower())
                matched_pref_dist = '{:0.3f}'.format(matched_pref_dist_num)

                final_joined_mapping['orig_matched_dist'] = orig_matched_dist
                final_joined_mapping['matched_pref_dist'] = matched_pref_dist
                final_joined_mapping['matched_text'] = extracted_mapping_items['text']
                final_joined_mapping['matchType'] = extracted_mapping_items['matchType']
                final_joined_mapping['id'] = extracted_mapping_items['id']
                final_joined_mapping['prefLabel'] = extracted_mapping_items['prefLabel']

                # add meaning slots to the enums if a matches are found
                #   and the cosine distance is acceptable
                # if orig_matched_dist_num < maxdist:
                #     curie = replace(str(extracted_mapping_items['id']), iri_curie_substitutions)
                #     inferred_enums[orig_enum]['meaning'] = curie

        # if verbose:
        #     eprint(final_joined_mapping)
        result_list.append(final_joined_mapping)
        eprint(final_joined_mapping)
        # eprint(result_list)
    return result_list


# add ontoprefix parameter (instead of using it as a global?
# or allow a list of ontoprefixes instead of just one?
def loop_enums(inferred_model_param, the_enums_param):
    per_enum_class_list = []
    for one_enum in the_enums_param:
        inner_permitted = get_one_enum_class(inferred_model_param, one_enum)
        one_enum_class_list = submit_bp_get_df(inner_permitted, min_search_chars, one_enum)
        # eprint(one_enum_class_list)
        per_enum_class_list.extend(one_enum_class_list)
        # eprint(per_enum_class_list)
    return per_enum_class_list


inferred_model = read_yaml_model(modelfile)

the_enums = get_enum_list(inferred_model)

sorted_enums = case_fold_list_sort(the_enums)

ontoprefix = str(ontoprefix).upper()

op_url_part = ''
if len(ontoprefix) > 0 and ontoprefix != 'NONE':
    op_url_part = '&ontologies=' + ontoprefix
else:
    eprint('NO ONTOPREFIX PROVIDED. SEARCHING ALL OF BIOPORTAL!')

results_list = loop_enums(inferred_model, sorted_enums)

results_frame = pds.DataFrame(results_list)

results_frame.to_csv('mixs_qd_bp.tsv', index=False, sep='\t')
