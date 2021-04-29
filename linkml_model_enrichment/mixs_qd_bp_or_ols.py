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
import requests

# from sys import stdout
# from yaml import SafeDumper
# import click

# TODO write mapped terms back in as meanings
#    give option for overwriting?
# TODO all user to specify enum classes to process

# assuming that the biosample-analysis directory
# is a sibling of linkml-model-enrichment
# modelfile = '../biosample-analysis/gensc.github.io/src/schema/mixs.yaml'
modelfile = 'target/Ontology_example_20210317_P2B1_allmods_categorytype_different_scores_per_mod-1.yaml'
# outputfile = 'mixs_mappings.tsv'
outputfile = 'target/Ontology_example_20210317_P2B1_allmods_categorytype_different_scores_per_mod-1.yaml_all_ols.tsv'
bpkey = os.getenv('ENUMENRICH_BPKEY')
# can be empty, a single ontology abbreviation, or a comma separate list
# case sensitive?
# some BP ontology abbreviations aren't exactly what you'd expect
# ontoprefix = 'ENVO,PATO,MESH,NCIT,LOINC,SNOMED,MPO,MEO,GAZ,GO,MVC,OBI,OMIT,PO,OCHV,GALEN,EFO,PMO'
# NCBITaxon
ontoprefix = 'NCBITaxon,SO,OMIT'
# species_enum,host_organism_enum
enum_list=''
enum_list = enum_list.split(",")
bpendpoint = 'http://data.bioontology.org'
maxdist = 0.05
verbose = True
min_search_chars = 2
# 'BioPortal' or 'OLS search'
# search_engine = 'BioPortal'
search_engine = 'OLS search'


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


def one_enum_to_bp_dict_list(permitteds, min_search_chars_param, one_enum_param: object):
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
            # eprint(built_url)
            bp_json = get_bp_json(built_url, bpkey)
            if len(bp_json) > 0:
                extracted_mapping_items = extract_mapping_items(bp_json, bpkey)
                # eprint(extracted_mapping_items)
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


# 'envo,pato,mesh,ncit,loinc,snomed,mpo,meo,gaz,' +
# 'go,mvc,obi,omit,po,ochv,galen,efo,pmo' + '&' +
# TODO add filter based on min_search_chars_param?
def one_enum_to_ols_frame_list(permitteds, min_search_chars_param, one_enum_param: object):
    # eprint(one_enum_param)
    result_list = []
    for orig_enum in permitteds:
        # eprint(one_enum_param + " | " + orig_enum)
        tidied_enum = re.sub(r'[_,.\-;@#?!&$ ]+', ' ', orig_enum)
        # eprint(tidied_enum)
        request_string = 'http://www.ebi.ac.uk/ols/api/search?q=' + \
                         urllib.parse.quote(tidied_enum) + '&' + \
                         'ontology=' + ontoprefix.lower() + "&" + \
                         'type=class' + '&' + \
                         'local=true' + '&' + \
                         'rows=10' + '&' + \
                         'exact=false'
        # eprint(request_string)
        response_param = requests.get(request_string)
        rj_param = response_param.json()
        rjrd_param = pds.DataFrame(rj_param['response']['docs'])
        r, c = rjrd_param.shape
        if r == 0:
            temp_dict = {'description': '', 'id': orig_enum, 'iri': '', 'is_defining_ontology': '', 'label': '',
                         'obo_id': '', 'ontology_name': '', 'ontology_prefix': '', 'short_form': '', 'type': ''}
            temp_list = [temp_dict]
            temp_df = pds.DataFrame(temp_list)
            rjrd_param = rjrd_param.append(temp_df)
        rjrd_param['query'] = orig_enum
        rjrd_param['enum_class'] = one_enum_param
        inner_cosine_obj = Cosine(1)
        # rjrd_param['query_preferred_cosine'] = \
        #     rjrd_param.apply(lambda row: inner_cosine_obj.distance(row['query'].lower(), row['label'].lower()), axis=1)
        rjrd_param['query_preferred_cosine'] = \
            rjrd_param.apply(lambda row: inner_cosine_obj.distance(tidied_enum.lower(), row['label'].lower()), axis=1)

        # eprint(rjrd_param)
        result_list.append(rjrd_param)
        # insert meaning
        bestline = rjrd_param.iloc[0, :]
        # eprint(bestline)
        # eprint(bestline['query_preferred_cosine'])

        # retrieve the "best" matching term to check it's synonyms
        # eprint(bestline['iri'])
        once = urllib.parse.quote(bestline['iri'], safe='')
        # eprint(once)
        twice = urllib.parse.quote(once, safe='')
        # eprint(twice)
        # eprint(bestline['ontology_name'])
        term_request_base = 'https://www.ebi.ac.uk/ols/api/ontologies/'
        term_iri = term_request_base + bestline['ontology_name'] + '/terms/' + twice
        eprint(term_iri)

        term_details = requests.get(term_iri)
        term_json = term_details.json()
        eprint(term_json)

        #
        # https://www.ebi.ac.uk/ols/api/ontologies/ncbitaxon/terms/http%253A%252F%252Fpurl.obolibrary.org%252Fobo%252FNCBITaxon_33169
        #

        if bestline['query_preferred_cosine'] < maxdist:
            inferred_model['enums'][one_enum_param]['permissible_values'][orig_enum]['meaning'] = bestline['obo_id']
            eprint(str(one_enum_param) + " | " + str(orig_enum) + " : " + str(bestline['obo_id']))
        else:
            eprint(str(one_enum_param) + " | " + str(orig_enum))
    return result_list


# add ontoprefix parameter (instead of using it as a global?
# or allow a list of ontoprefixes instead of just one?
def all_enums_to_ols(inferred_model_param, the_enums_param):
    per_enum_class_list = []
    for one_enum in the_enums_param:
        inner_permitted_param = get_one_enum_class(inferred_model_param, one_enum)
        one_enum_class_list = one_enum_to_ols_frame_list(inner_permitted_param, min_search_chars, one_enum)
        # eprint(one_enum_class_list)
        per_enum_class_list.extend(one_enum_class_list)
        # eprint(per_enum_class_list)
    return per_enum_class_list


# add ontoprefix parameter (instead of using it as a global?
def all_enums_to_bp(inferred_model_param, the_enums_param):
    per_enum_class_list = []
    for one_enum in the_enums_param:
        inner_permitted_param = get_one_enum_class(inferred_model_param, one_enum)
        one_enum_class_list = one_enum_to_bp_dict_list(inner_permitted_param, min_search_chars, one_enum)
        # eprint(one_enum_class_list)
        per_enum_class_list.extend(one_enum_class_list)
        # eprint(per_enum_class_list)
    return per_enum_class_list


###

inferred_model = read_yaml_model(modelfile)

# eprint(enum_list)
# eprint(len(enum_list))

# enum_list[0] should not be empty
# should also test whether user specified enums are actually present in model
if len(enum_list) == 0 or len(enum_list[0]) == 0:
    the_enums = get_enum_list(inferred_model)
else:
    the_enums = enum_list
    # eprint(enum_list[0])
# eprint(the_enums)

sorted_enums = case_fold_list_sort(the_enums)

###

# BP and OLS dataframe structures are not the same yet
# different columns
# BP shows one best
# OLS lists up to N best
# not filtering out small queries in OLS approach yet
# no string similarity in OLS dataframe yet
#    OLS doesn't report what the matching text was
#    match from query to preferred label can be misleadingly low
#    could retrieve all annotations, calculate cosine distance against each
#    and then report the best?
# (OLS approach?) neither handling nor optimizing for repeat values
# not merging results back into model yet
if search_engine == 'BioPortal':
    ontoprefix = str(ontoprefix).upper()
    op_url_part = ''
    if len(ontoprefix) > 0 and ontoprefix != 'NONE':
        op_url_part = '&ontologies=' + ontoprefix
    else:
        eprint('NO ONTOPREFIX PROVIDED. SEARCHING ALL OF BIOPORTAL!')
    results_list = all_enums_to_bp(inferred_model, sorted_enums)
    results_frame = pds.DataFrame(results_list)
    results_frame.to_csv(outputfile, index=False, sep='\t')
elif search_engine == 'OLS search':
    all_ols_results = all_enums_to_ols(inferred_model, sorted_enums)
    # len(all_ols_results)
    # 1015
    ols_results_single_frame = pds.concat(all_ols_results)
    ols_results_single_frame = ols_results_single_frame[['enum_class', 'query', 'obo_id', 'label',
                                                         'description', 'ontology_prefix']]
    # cosine_obj = Cosine(1)
    # ols_results_single_frame['query_preferred_cosine'] = \
    #     ols_results_single_frame.apply(lambda row: cosine_obj.distance(row['query'].lower(), row['label'].lower()),
    #                                    axis=1)
    ols_results_single_frame.to_csv(outputfile, index=False, sep='\t')
    yaml.safe_dump(inferred_model, sys.stdout, default_flow_style=False)
else:
    eprint('No valid search engine specified')

# https://www.ebi.ac.uk/ols/docs/api

# fieldList
#    defaults are {iri,label,short_form,obo_id,ontology_name,ontology_prefix,description,type}
# queryFields
#    defaults are {label, synonym, description, short_form, obo_id, annotations, logical_description, iri}
# groupField
# obsoletes
# childrenOf
# allChildrenOf
# start

# list(ols_results_single_frame.columns)
#
# ['id', 'iri', 'short_form', 'obo_id', 'label', 'description', 'ontology_name', 'ontology_prefix', 'type',
#  'is_defining_ontology', 'query', 'enum_class']
