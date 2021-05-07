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
import pandas as pds
import requests
import click

# BIOPORTAL SEARCHING DISABLED
# MIN CHARACTERS FOR SEARCH NOT BEING ENFORCED
# THESE THINGS MAY NOT YET BE REFLECTED IN THE CLICK HELP


# import os
# from sys import stdout
# from yaml import SafeDumper


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
    if vg:
        eprint(enum_class_param)
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


# def one_enum_to_bp_dict_list(permitteds, min_search_chars_param, one_enum_param: object):
#     result_list = []
#     for orig_enum in permitteds:
#
#         final_joined_mapping = dict(one_enum_param='', orig_enum='', tidied_enum='',
#                                     orig_matched_dist='', matched_pref_dist='', matched_text='', matchType='',
#                                     id='', prefLabel='')
#
#         final_joined_mapping['one_enum_param'] = one_enum_param
#         final_joined_mapping['orig_enum'] = orig_enum
#
#         # strip punct
#         # could also url encode?
#         tidied_enum = re.sub(r'[_,.\-;@#?!&$ ]+', ' ', orig_enum)
#         final_joined_mapping['tidied_enum'] = tidied_enum
#
#         if len(tidied_enum) >= min_search_chars_param:
#             built_url = bpendpoint + '/annotator?longest_only=true' + op_url_part + \
#                         '&text=' + urllib.parse.quote(tidied_enum)
#             # make longest_only a parameter?
#             #   if off,  extract_mapping_items will make multiple returns?
#             # eprint(built_url)
#             bp_json = get_bp_json(built_url, bpkey)
#             if len(bp_json) > 0:
#                 extracted_mapping_items = extract_mapping_items(bp_json, bpkey)
#                 # eprint(extracted_mapping_items)
#                 cosine_obj = Cosine(1)
#                 orig_matched_dist_num = cosine_obj.distance(orig_enum.lower(), extracted_mapping_items['text'].lower())
#                 orig_matched_dist = '{:0.3f}'.format(orig_matched_dist_num)
#                 matched_pref_dist_num = cosine_obj.distance(extracted_mapping_items['text'].lower(),
#                                                             extracted_mapping_items['prefLabel'].lower())
#                 matched_pref_dist = '{:0.3f}'.format(matched_pref_dist_num)
#
#                 final_joined_mapping['orig_matched_dist'] = orig_matched_dist
#                 final_joined_mapping['matched_pref_dist'] = matched_pref_dist
#                 final_joined_mapping['matched_text'] = extracted_mapping_items['text']
#                 final_joined_mapping['matchType'] = extracted_mapping_items['matchType']
#                 final_joined_mapping['id'] = extracted_mapping_items['id']
#                 final_joined_mapping['prefLabel'] = extracted_mapping_items['prefLabel']
#
#                 # add meaning slots to the enums if matches are found
#                 #   and the cosine distance is acceptable
#                 # if orig_matched_dist_num < maxdist:
#                 #     curie = replace(str(extracted_mapping_items['id']), iri_curie_substitutions)
#                 #     inferred_enums[orig_enum]['meaning'] = curie
#
#         # if verbose:
#         #     eprint(final_joined_mapping)
#         result_list.append(final_joined_mapping)
#         eprint(final_joined_mapping)
#     return result_list

# TODO add filter based on min_search_chars_param?
# no longer requiring a minimum search length
def one_enum_to_ols_frame_list(permitteds, one_enum_param: object):
    per_enum_frame = pds.DataFrame(columns=['enum_class', 'orig_enum', 'query', 'obo_id', 'pref_lab',
                                            'name', 'cosine_dist', 'dist_ok', 'type', 'scope'])
    for orig_enum in permitteds:
        if vg:
            eprint(one_enum_param, orig_enum)

        # check if permitted value already has a meaning
        meaning_search = list(inferred_model['enums'][one_enum_param]['permissible_values'][orig_enum].keys())
        if 'meaning' in meaning_search:
            has_meaning = True
        else:
            has_meaning = False

        # tidied_enum = re.sub(r'[_,.\-;@#?!&$ ]+', ' ', orig_enum)
        tidied_enum = re.sub(r'[' + ecg + ']+', ' ', orig_enum)

        ontologies_phrase = ''
        if len(opg) > 1:
            ontologies_phrase = 'ontology=' + opg.lower()

        qf_phrase = ''
        if len(qfg) > 1:
            qf_phrase = 'queryFields=' + qfg.lower()

        request_string = 'http://www.ebi.ac.uk/ols/api/search?q=' + \
                         urllib.parse.quote(tidied_enum) + '&' + \
                         'type=class' + '&' + \
                         'local=true' + '&' + \
                         'exact=false' + '&' + \
                         ontologies_phrase + "&" + \
                         'rows=' + str(rrg) + '&' + \
                         qf_phrase

        # if vg:
        #     eprint(request_string)

        response_param = requests.get(request_string)
        ols_string_search_res_j = response_param.json()
        ols_string_search_res_frame = pds.DataFrame(ols_string_search_res_j['response']['docs'])
        ols_string_search_res_frame.insert(0, "query", tidied_enum)

        # did the string search get any result rows?
        r, c = ols_string_search_res_frame.shape
        if r == 0:
            no_search_res_dict = {'description': '', 'id': orig_enum, 'iri': '', 'is_defining_ontology': '',
                                  'label': '', 'obo_id': '', 'ontology_name': '', 'ontology_prefix': '',
                                  'short_form': '', 'type': ''}
            no_search_res_frame = pds.DataFrame([no_search_res_dict])
            ols_string_search_res_frame = ols_string_search_res_frame.append(no_search_res_frame)

        ols_string_search_res_frame['query'] = orig_enum
        inner_cosine_obj = Cosine(1)

        # if vg:
        #     eprint(ols_string_search_res_frame)

        # insert meaning
        # first, check whether anny of the annotation on any of the hits have an
        # acceptable cosine string distance

        annotations_frame = pds.DataFrame(columns=['name', 'obo_id', 'scope', 'type', 'xrefs'])
        for ols_string_search_res_row in ols_string_search_res_frame.itertuples(index=False):
            # global annotations_frame
            # if vg:
            #     eprint(ols_string_search_res_row.iri)
            once = urllib.parse.quote(ols_string_search_res_row.iri, safe='')
            twice = urllib.parse.quote(once, safe='')
            # build url from base
            term_retr_base = 'http://www.ebi.ac.uk/ols/api/ontologies/'
            term_retr_assembled = term_retr_base + ols_string_search_res_row.ontology_name + '/terms/' + twice
            if vg:
                eprint(term_retr_assembled)
            term_details = requests.get(term_retr_assembled)
            term_json = term_details.json()
            has_label = 'label' in set(term_json.keys())
            if has_label:
                if vg:
                    eprint(term_json['label'])
                #     eprint(term_json.keys())
                label_frame = pds.DataFrame([[term_json['label'], 'label', 'label', '']],
                                            columns=['name', 'scope', 'type', 'xrefs'])
                label_frame['obo_id'] = term_json['obo_id']
                label_frame['pref_lab'] = term_json['label']
                annotations_frame = annotations_frame.append(label_frame, ignore_index=True)
            # also get other properties?
            has_synonyms = 'obo_synonym' in set(term_json.keys())
            if has_synonyms:
                obo_syn_json = term_json['obo_synonym']
                obo_syn_frame = pds.DataFrame(obo_syn_json)
                obo_syn_frame['obo_id'] = term_json['obo_id']
                obo_syn_frame['pref_lab'] = term_json['label']
                annotations_frame = annotations_frame.append(obo_syn_frame, ignore_index=True)

            annotations_row_count = len(annotations_frame.index)

            if annotations_row_count == 0:
                eprint('NO ANNOTATIONS')
                manual_row = pds.Series(['', '', '', '', '', ''])
                row_df = pds.DataFrame([manual_row], columns=['name', 'obo_id', 'scope', 'type', 'xrefs', 'pref_lab'])
                annotations_frame = pds.concat([row_df, annotations_frame], ignore_index=True)
            annotations_frame['enum_class'] = one_enum_param
            annotations_frame['query'] = tidied_enum
            annotations_frame['orig_enum'] = orig_enum
            # annotations_frame['cosine_dist'] = 0.5
            # eprint(tidied_enum.lower())
            # eprint(annotations_frame['name'])
            # annotations_frame = annotations_frame.replace(np.nan, '', regex=True)
            annotations_frame['name'] = annotations_frame['name'].fillna('')

            annotations_frame['cosine_dist'] = \
                annotations_frame.apply(lambda row: inner_cosine_obj.distance(tidied_enum.lower(),
                                                                              row['name'].lower()),
                                        axis=1)
            annotations_frame = annotations_frame.sort_values('cosine_dist')
            annotations_frame['dist_ok'] = annotations_frame['cosine_dist'] <= mdg

            if vg:
                eprint(annotations_frame)

            annotations_frame = annotations_frame[
                ['enum_class', 'orig_enum', 'query', 'obo_id', 'pref_lab', 'name', 'cosine_dist', 'dist_ok', 'type',
                 'scope']]
            # do something with xrefs?
        per_enum_frame = per_enum_frame.append(annotations_frame)
        # if vg:
        #     eprint(annotations_frame)
        #     eprint(per_enum_frame)
    return per_enum_frame


# add ontoprefix parameter (instead of using it as a global?
# or allow a list of ontoprefixes instead of just one?
def all_enums_to_ols(inferred_model_param, the_enums_param):
    # per_enum_class_list = []
    multi_enum_frame = pds.DataFrame(columns=['enum_class', 'orig_enum', 'query', 'obo_id', 'pref_lab',
                                              'name', 'cosine_dist', 'dist_ok', 'type', 'scope'])
    for one_enum in the_enums_param:
        inner_permitted_param = get_one_enum_class(inferred_model_param, one_enum)
        one_enum_class_list = one_enum_to_ols_frame_list(inner_permitted_param, one_enum)
        multi_enum_frame = multi_enum_frame.append(one_enum_class_list)
    return multi_enum_frame


# # add ontoprefix parameter (instead of using it as a global?
# def all_enums_to_bp(inferred_model_param, the_enums_param):
#     per_enum_class_list = []
#     for one_enum in the_enums_param:
#         inner_permitted_param = get_one_enum_class(inferred_model_param, one_enum)
#         one_enum_class_list = one_enum_to_bp_dict_list(inner_permitted_param, min_search_chars, one_enum)
#         # eprint(one_enum_class_list)
#         per_enum_class_list.extend(one_enum_class_list)
#         # eprint(per_enum_class_list)
#     return per_enum_class_list

global inferred_model, ecg, opg, rrg, qfg, mdg, omg, vg


# don't forget type field on options
@click.command()
@click.option('--modelfile', '-f',
              help='Path to a YAML linkml file containing enumerated values.',
              required=True,
              type=click.Path(exists=True),
              )
@click.option('--tabular_outputfile', '-t',
              default='mappings_log.tsv',
              help='A tsv dump of the search results will be written to this file.',
              show_default=True,
              type=click.Path()
              )
# have tried NCBITaxon,SO,ENVO,PATO,MESH,NCIT,LOINC,SNOMED,MPO,MEO,GAZ,GO,MVC,OBI,OMIT,PO,OCHV,GALEN,EFO,PMO
# but probably better to stick witha  smaller list of mostly OBO
@click.option('--ontoprefix', '-p',
              default='NCBITaxon,SO,ENVO,PATO,GO,OBI',
              help='comma-separated list of (abbreviated) ontologies to search over.',
              show_default=True
              )
# synbio: species_enum,host_organism_enum
@click.option('--enum_list', '-e',
              default='',
              help='comma-separated list of enums to search with. '' = all enums.',
              show_default=True
              )
# the choice and order of the query_fields has a big impact on what terms are returned
# overwrite the model's description with preferred term?
# OLS defaults are {label, synonym, description, short_form, obo_id, annotations, logical_description, iri}
@click.option('--query_fields', '-q',
              default='',
              help="comma-separated list of term properties to include in string similarity calculation. '" +
                   "'' = {label, synonym, description, short_form, obo_id, annotations, logical_description, iri}.",
              show_default=True
              )
# escaped_chars impacts returned fields too
# 'SARS-CoV-2' fails if the hyphens are escaped or ???
@click.option('--escaped_chars', '-c',
              default='._ ',
              help='characters to replace with whitespace.',
              show_default=True
              )
@click.option('--min_search_chars', '-n',
              default=2,
              help='queries with fewer characters will not be submitted in the search.',
              show_default=True
              )
@click.option('--row_req', '-r',
              default=10,
              help='requested number of search result.',
              show_default=True
              )
@click.option('--maxdist', '-r',
              default=0.05,
              help="maximum string distance between query and best matching term's best matching property.",
              show_default=True
              )
@click.option('--overwite_meaning', '-m',
              default=False,
              help="should existing enum meanings be overwritten?.",
              is_flag=True,
              show_default=True
              )
@click.option('--verbose', '-v',
              default=False,
              help="verbose mode. see also debug mode.",
              is_flag=True,
              show_default=True
              )
@click.option('--search_engine', '-s',
              default='OLS',
              help="OLS or BioPortal.",
              show_default=True
              )
def clickmain(modelfile, tabular_outputfile, ontoprefix, enum_list, query_fields, escaped_chars, min_search_chars,
              row_req, maxdist, overwite_meaning, verbose, search_engine):
    enum_list = enum_list.split(",")

    global inferred_model, ecg, opg, rrg, qfg, mdg, omg, vg

    inferred_model = read_yaml_model(modelfile)
    ecg = escaped_chars
    opg = ontoprefix
    rrg = row_req
    qfg = query_fields
    mdg = maxdist
    omg = overwite_meaning
    vg = verbose

    if vg:
        temp = get_enum_list(inferred_model)
        temp.sort()
        eprint(temp)
    # TODO check this
    if len(enum_list) == 0 or len(enum_list[0]) == 0:
        the_enums = get_enum_list(inferred_model)
    else:
        the_enums = enum_list
    sorted_enums = case_fold_list_sort(the_enums)

    if search_engine == 'BioPortal':
        return
        # ontoprefix = str(ontoprefix).upper()
        # op_url_part = ''
        # if len(ontoprefix) > 0 and ontoprefix != 'NONE':
        #     op_url_part = '&ontologies=' + ontoprefix
        # else:
        #     eprint('NO ONTOPREFIX PROVIDED. SEARCHING ALL OF BIOPORTAL!')
        # results_list = all_enums_to_bp(inferred_model, sorted_enums)
        # results_frame = pds.DataFrame(results_list)
        # results_frame.to_csv(tabular_outputfile, index=False, sep='\t')
    elif search_engine == 'OLS':
        all_ols_results = all_enums_to_ols(inferred_model, sorted_enums)
        if vg:
            eprint(all_ols_results)
        all_ols_results.to_csv(tabular_outputfile, sep='\t')
        # ols_results_single_frame = pds.concat(all_ols_results)
        # ols_results_single_frame = ols_results_single_frame[['enum_class', 'query', 'obo_id', 'label',
        #                                                      'description', 'ontology_prefix']]
        # ols_results_single_frame.to_csv(tabular_outputfile, index=False, sep='\t')
        # yaml.safe_dump(inferred_model, sys.stdout, default_flow_style=False)
    else:
        eprint('No valid search engine specified')


if __name__ == '__main__':
    pds.set_option('display.expand_frame_repr', False)
    clickmain(auto_envvar_prefix='ENUMENRICH')

# bpkey = os.getenv('ENUMENRICH_BPKEY')
# bpendpoint = 'http://data.bioontology.org'

# TODO write mapped terms back in as meanings
#    give option for overwriting?
# TODO all user to specify enum classes to process
# when verbose, stderr gets status and debugging info
# stdout gets the modified model as yaml and should be redirected to a file

# BP and OLS dataframe structures are not the same yet
#   different columns
#   BP shows one best
#   OLS lists up to N best
#   not filtering out small queries in OLS approach yet
#   (OLS approach?) neither handling nor optimizing for repeat values
#   not merging results back into model yet

# # bicarbonate
# # term_iri = 'https://www.ebi.ac.uk/ols/api/ontologies/chebi/terms/http%253A%252F%252Fpurl.obolibrary.org%252Fobo%252FCHEBI_32139'
# # fungus
# # term_iri = 'https://www.ebi.ac.uk/ols/api/ontologies/ncbitaxon/terms/http%253A%252F%252Fpurl.obolibrary.org%252Fobo%252FNCBITaxon_33169'
# # sars-cov-2
# # term_iri = 'https://www.ebi.ac.uk/ols/api/ontologies/ncbitaxon/terms/http%253A%252F%252Fpurl.obolibrary.org%252Fobo%252FNCBITaxon_2697049'
# # Escherichia phage T7
# # # http://purl.obolibrary.org/obo/NCBITaxon_10760
# # term_iri = 'https://www.ebi.ac.uk/ols/api/ontologies/ncbitaxon/terms/http%253A%252F%252Fpurl.obolibrary.org%252Fobo%252FNCBITaxon_10760'

# # one_enum_param = 'taxon'
# # orig_enum = 'Homo sapiens'
# # ecg = '._ '
# # opg = 'NCBItaxon'
# # qfg = 'label,annotation'
# # vg = True
# # rrg = 10
# # mdg = 0.05
# # has_meaning = False