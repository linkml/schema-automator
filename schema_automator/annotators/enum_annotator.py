# import linkml
import logging
import random
import re
# urllib? urllib3? pure requests?
import urllib

import click
import click_log
import linkml.utils.rawloader as rl
import linkml_runtime
import pandas as pd
import requests
import yaml
from linkml_runtime.dumpers import yaml_dumper
# cosine? SIFT4?
from strsimpy.cosine import Cosine

# # for querying and changing?
# import linkml_runtime_api

# # PROGRESS
# # took out globals
# # reusing requests sessions
# # saving annotations
# # logging


# # TODO
# # add caching of already searched terms
# # add default values for functions

# todo this silences
#   SettingWithCopyWarning: A value is trying to be set on a copy of a slice from a DataFrame
#   but I should really be dealing with it
pd.options.mode.chained_assignment = None  # default='warn'

logger = logging.getLogger(__name__)
click_log.basic_config(logger)


# make classes out of DataFrames that would be appealing as globals
# TODO try dataclasses
class DataFrameClass:
    def __init__(self):
        self.mapping_frame = pd.DataFrame()

    def add(self, miniframe):
        self.mapping_frame = self.mapping_frame.append(miniframe)

    def get(self):
        return self.mapping_frame


def parse_yaml_file(yaml_file_name):
    with open(yaml_file_name, 'r') as stream:
        try:
            parse_res = yaml.safe_load(stream)
            return parse_res
        except yaml.YAMLError as exc:
            # log or print?
            logger.error(exc)


def dict_to_schema(dict_param):
    converted_schema = rl.load_raw_schema(dict_param)
    return converted_schema


def request_an_enum(schema_param, enum_name_param):
    enum_requested = schema_param.enums[enum_name_param]
    return enum_requested


def request_pvs(enum_param):
    pvs_requested = enum_param.permissible_values
    return pvs_requested


# make sorting optional?
def get_pv_names(pv_param):
    pv_names = [k for k, v in pv_param.items()]
    pv_names.sort()
    return pv_names


def make_cosine_obj(shingle_size_param):
    made_cosine_obj = Cosine(shingle_size_param)
    return made_cosine_obj


def ols_term_search(term, chars_to_whiteout, ontology_param, qf_param, rowcount_param, blank_row_param,
                    global_frame_param, session_param, ols_search_base_url, do_trunc):
    woed = do_whiteout(term, chars_to_whiteout, do_trunc)

    request_string = ols_search_base_url + \
                     '?q=' + \
                     urllib.parse.quote(woed) + '&' + \
                     'type=class' + '&' + \
                     'exact=false' + '&' + \
                     ontology_param + "&" + \
                     'rows=' + str(rowcount_param) + '&' + \
                     qf_param

    logger.debug(request_string)

    # this gets matching terms but doesn't show why they matched
    response_param = session_param.get(request_string)

    ols_string_search_res_j = response_param.json()
    ols_string_search_res_frame = pd.DataFrame(ols_string_search_res_j['response']['docs'])
    ols_string_search_res_frame.insert(0, "raw_query", term)
    ols_string_search_res_frame.insert(0, "tidied_query", woed)

    # did the string search get any result rows?
    r, c = ols_string_search_res_frame.shape
    if r == 0:
        no_search_res_dict = blank_row_param.copy()
        # no_search_res_dict['id'] = term
        no_search_res_dict['raw_query'] = term
        no_search_res_dict['tidied_query'] = woed
        no_search_res_frame = pd.DataFrame([no_search_res_dict])
        ols_string_search_res_frame = ols_string_search_res_frame.append(no_search_res_frame)
        # failures.append(orig_enum)

    global_frame_param.add(ols_string_search_res_frame)
    # return ols_string_search_res_frame?
    return True


# TODO refactor
def make_ontolgy_phrase(ontology_param):
    ontologies_phrase = ''
    if ontology_param is not None and ontology_param != "":
        ontologies_phrase = 'ontology=' + ontology_param.lower()
    return ontologies_phrase


# TODO refactor
def make_qf_phrase(qf_param):
    qf_phrase = ''
    if qf_param is not None and qf_param != "":
        qf_phrase = 'queryFields=' + qf_param.lower()
    return qf_phrase


def do_whiteout(raw_string, chars_to_whiteout, do_trunc):
    if chars_to_whiteout is not None and chars_to_whiteout != "":
        tidied_string = re.sub(r'[' + chars_to_whiteout + ']+', ' ', raw_string)
    else:
        tidied_string = raw_string
    if do_trunc:
        tidied_string = re.sub(r' \(.*$', '', tidied_string)
    return tidied_string


def get_ols_term_annotations(iri_param, ontology_param, session_param, ols_terms_based_url, term_annotations):
    logger.info(iri_param)
    once = urllib.parse.quote(iri_param, safe='')
    twice = urllib.parse.quote(once, safe='')
    # build url from base
    term_retr_assembled = ols_terms_based_url + ontology_param + '/terms/' + twice
    term_details = session_param.get(term_retr_assembled)
    term_json = term_details.json()

    if 'label' in set(term_json.keys()):
        # logger.debug(term_retr_assembled)
        # term_label = term_json['label']
        # logger.debug(term_label)
        label_frame = pd.DataFrame([[term_json['label'], 'label', 'label', '']],
                                   columns=['name', 'scope', 'type', 'xrefs'])
        label_frame['obo_id'] = term_json['obo_id']
        label_frame['pref_lab'] = term_json['label']

        label_frame.insert(0, "iri", iri_param)

        term_annotations.add(label_frame)

    if 'obo_synonym' in set(term_json.keys()):
        obo_syn_json = term_json['obo_synonym']
        obo_syn_frame = pd.DataFrame(obo_syn_json)
        obo_syn_frame['obo_id'] = term_json['obo_id']
        obo_syn_frame['pref_lab'] = term_json['label']
        obo_syn_frame.insert(0, "iri", iri_param)
        term_annotations.add(obo_syn_frame)

    return True


@click.command()
@click_log.simple_verbosity_option(logger)
@click.option('--modelfile', help="path to LinkML input", type=click.Path(exists=True), show_default=True,
              required=True)
# parametrize this so this script can be written many times an not overwrite the all mappings file
@click.option('--all_mappings_fn', default="target/all_mappings_frame.tsv",
              help="where do you want to write a table of all mappings?",
              type=click.Path(), show_default=True)
# binomial_name_enum
@click.option('--requested_enum_name', help="name of the enumeration that contains the terms you want to map",
              required=True)
@click.option('--overwrite_meaning/--no_overwrite', help="do you want to overwrite meanings that are already present?",
              default=True, show_default=True)
@click.option('--whiteout_chars', help="characters in terms that should be replaced with whitespace before mapping",
              default='._-', show_default=True)
# ontology_string = "NCBItaxon,PATO"
@click.option('--ontology_string', help="comma separated list of ontologies to use in the mapping", default='NCBItaxon',
              show_default=True)
@click.option('--ols_search_base_url', help="", default='http://www.ebi.ac.uk/ols/api/search', show_default=True)
@click.option('--ols_terms_based_url', help="", default='http://www.ebi.ac.uk/ols/api/ontologies/',
              show_default=True)
@click.option('--desired_row_count', help="how many rows of mappings do you want to retrieve for each term?", default=5,
              show_default=True)
@click.option('--shingle_size', help="what shingle/n-gram size do you want for cosine similarity calculations?",
              default=2, show_default=True)
@click.option('--max_cosine',
              help="""how much of a cosine distance will you tolerate 
              when comparing an enum name to a term label or synonym?""",
              default=0.05, show_default=True)
@click.option('--query_field_string',
              help="""do you want to define a custom list of fields to search in? 
              The default settings work well in most cases.""",
              default='', show_default=True)
@click.option('--test_sample_size',
              help="""if greater than 0, the enum name list will be samples at this size before mapping.""",
              default=0, show_default=True)
@click.option('--trim_parentheticals/--keep_parentheticals', default=False)
def enum_annotator(modelfile, all_mappings_fn, requested_enum_name, whiteout_chars, ontology_string,
                   ols_search_base_url, ols_terms_based_url, desired_row_count, shingle_size, max_cosine,
                   overwrite_meaning, query_field_string, test_sample_size, trim_parentheticals):
    # show entire width of data frames
    pd.set_option('display.expand_frame_repr', False)

    # GLOBALS within this method
    blank_row = {'title': '', 'id': '', 'iri': '', 'is_defining_ontology': '',
                 'label': '', 'obo_id': '', 'ontology_name': '', 'ontology_prefix': '',
                 'short_form': '', 'type': ''}

    # ols_annotations_cols = ['name', 'obo_id', 'scope', 'type', 'xrefs']

    parsed_yaml = parse_yaml_file(modelfile)

    current_schema = dict_to_schema(parsed_yaml)

    requested_enum_obj = request_an_enum(current_schema, requested_enum_name)

    requested_pvs_obj = request_pvs(requested_enum_obj)

    requested_pvs_names = get_pv_names(requested_pvs_obj)
    requested_pvs_names.sort()
    logger.debug(requested_pvs_names)

    ontologies_phrased = make_ontolgy_phrase(ontology_string)
    logger.debug(ontologies_phrased)

    qf_phrased = make_qf_phrase(query_field_string)
    logger.debug(qf_phrased)

    cosine_obj = make_cosine_obj(shingle_size)
    # logger.debug(cosine_obj)

    # initialize
    enum_name_mappings = DataFrameClass()
    # logger.debug(enum_name_mappings.get())
    term_annotations = DataFrameClass()
    # logger.debug(term_annotations.get())

    reusable_session = requests.Session()
    # logger.debug(reusable_session)

    # # load with schemaview and extract SchemaDefinition?
    # # or open directly into a SchemaDefinition?  HOW?
    # # https://fedingo.com/how-to-read-yaml-file-to-dict-in-python/

    if test_sample_size > 0:
        requested_pvs_names = random.sample(requested_pvs_names, test_sample_size)
        requested_pvs_names.sort()

    for pv_name in requested_pvs_names:
        logger.info(pv_name)
        # current_pv = requested_pvs_obj[pv_name]
        # logger.debug(current_pv)
        ols_term_search(pv_name, whiteout_chars, ontologies_phrased, qf_phrased, desired_row_count,
                        blank_row, enum_name_mappings, reusable_session, ols_search_base_url, trim_parentheticals)
        # # returns true
        # # could look at growth in enum_name_mappings

        enum_name_mapping_frame = enum_name_mappings.get()
        # logger.debug(enum_name_mapping_frame)

        term_and_source = enum_name_mapping_frame.loc[enum_name_mapping_frame['raw_query'].eq(pv_name)]

        term_and_source = term_and_source[["iri", "ontology_name"]]
        term_and_source.drop_duplicates(inplace=True)
        term_and_source = term_and_source.loc[~term_and_source['iri'].eq("")]
        term_and_source.sort_values(["iri", "ontology_name"], inplace=True)
        logger.debug(term_and_source)

        term_and_source = term_and_source.to_dict(orient="records")

        for i in term_and_source:
            # returns true and saves to a dataframe class
            get_ols_term_annotations(i["iri"], i["ontology_name"], reusable_session,
                                     ols_terms_based_url, term_annotations)

        annotations_from_terms = term_annotations.get()

        # logger.warning(enum_name_mapping_frame)
        # # warning:    tidied_query     raw_query title id iri is_defining_ontology label obo_id ontology_name ontology_prefix short_form type
        # # warning: 0  metabolomics  metabolomics
        # logger.warning(annotations_from_terms)
        # # warning: Empty DataFrame
        # # warning: Columns: []
        # # warning: Index: []

        if len(enum_name_mapping_frame.index) > 0 and len(annotations_from_terms.index) > 0:
            raw_through_annotations = enum_name_mapping_frame.merge(annotations_from_terms, how='left', on="iri",
                                                                    suffixes=('_term', '_ano'))

            for_str_dist = raw_through_annotations[["tidied_query", "name"]]
            # 20211215 0912
            # A value is trying to be set on a copy of a slice from a DataFrame.
            for_str_dist["tidied_query_lc"] = for_str_dist["tidied_query"].str.lower()
            for_str_dist["name_lc"] = for_str_dist["name"].str.lower()

            # favoring simplicity over efficiency
            # ie may be string-comparing some duplicates
            # easier to merge back in
            # for_str_dist = for_str_dist.loc[
            #     ~for_str_dist["tidied_query"].eq("") and ~for_str_dist["label"].eq("") and ~for_str_dist[
            #         "tidied_query"].isnull() and ~for_str_dist["label"].isnull()]
            # for_str_dist.drop_duplicates(inplace=True)
            # for_str_dist.sort_values(["tidied_query", "label"], inplace=True)

            for_str_dist_dict = for_str_dist.to_dict(orient="records")

            # dist_list = []
            new_pair_list = []

            for pair in for_str_dist_dict:
                # used to get_profile
                name_type = type(pair["name"])
                if name_type is str:
                    the_dist = cosine_obj.distance(pair["tidied_query_lc"], pair["name_lc"])
                    pair['cosine'] = the_dist
                else:
                    pair['cosine'] = None
                new_pair_list.append(pair)

            for_str_dist = pd.DataFrame(new_pair_list)
            for_str_dist.drop(labels=["tidied_query_lc", "name_lc"], axis=1, inplace=True)

            # was debug
            logger.debug(for_str_dist)
            raw_through_dist = raw_through_annotations.merge(for_str_dist, how="left", on=["tidied_query", "name"])
            all_mappings_frame = []

            new_enum = linkml_runtime.linkml_model.EnumDefinition(name=requested_enum_name)
            # logger.info(new_enum)

            # looping inside the same loop ?!
            for i in requested_pvs_names:
                # todo unnest loop?
                logger.debug(i)
                ce = requested_pvs_obj[i]
                cr = raw_through_dist.loc[raw_through_dist["raw_query"].eq(i)]
                all_mappings_frame.append(cr)
                cr_row_count = len(cr.index)
                if cr_row_count > 0:
                    min_cosine = cr["cosine"].min()
                    with_min = cr.loc[cr["cosine"] == min_cosine]
                    with_min_row_count = len(with_min.index)
                    if with_min_row_count > 0:
                        with_min = with_min.drop(labels=['xrefs'], axis=1)
                        if 'description' in with_min.columns:
                            with_min['description'] = str(with_min['description'])
                        with_min.drop_duplicates(inplace=True)
                        deduped_row_count = len(with_min.index)
                        # # I'm surprised that there aren't any 2+ equally good mappings here
                        # will have to deal with that at some point
                        # may still need to do some row filtering/prioritizing by source or annotation type
                        # prefer label over synonym
                        # Prefer ontologies in the order they appear in XXX parameter?
                        if deduped_row_count > 1:
                            pass
                        first_row_as_dict = (with_min.to_dict(orient="records"))[0]
                        # print(first_row_as_dict)
                        ce.annotations["match_val"] = first_row_as_dict['name']
                        ce.annotations["match_type"] = first_row_as_dict['scope']
                        ce.annotations["match_id"] = first_row_as_dict['obo_id_term']
                        ce.annotations["match_pref_lab"] = first_row_as_dict['pref_lab']
                        ce.annotations["cosine"] = first_row_as_dict['cosine']
                        if overwrite_meaning:
                            if first_row_as_dict['cosine'] <= max_cosine:
                                ce.meaning = first_row_as_dict['obo_id_term']
                                ce.title = first_row_as_dict['label']
                            else:
                                ce.meaning = None
                                ce.title = None
                        new_enum.permissible_values[i] = ce

    all_mappings_frame = pd.concat(all_mappings_frame)

    all_mappings_frame.to_csv(all_mappings_fn, sep="\t", index=False)

    if 'description' in all_mappings_frame.columns:
        all_mappings_frame['description'] = str(all_mappings_frame['description'])
    if 'xrefs' in all_mappings_frame.columns:
        all_mappings_frame['xrefs'] = str(all_mappings_frame['xrefs'])

    all_mappings_frame.drop_duplicates(inplace=True)

    all_mappings_frame.to_csv(all_mappings_fn, sep="\t", index=False)

    gs_tq_vc = all_mappings_frame["raw_query"].value_counts()
    logger.info("Number of hits for each term, regardless of quality. Doesn't show terms with 0 hits.")
    logger.info(gs_tq_vc)

    current_schema.enums[requested_enum_name] = new_enum

    string_dumped_schema = yaml_dumper.dumps(current_schema)

    # todo send to STDOUT or output file?
    print(string_dumped_schema)
    # # with open(xxx, 'w') as file:
    # #     documents = yaml.safe_dump(string_dumped_schema, file)


if __name__ == '__main__':
    enum_annotator()
