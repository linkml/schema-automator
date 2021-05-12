
def one_enum_to_ols_frame_list(permitteds, one_enum_param):
    global failures
    global success_frame

    per_enum_frame = pds.DataFrame(columns=cols2display)

    for orig_enum in permitteds:

        temp = one_enum_param + ": " + orig_enum
        logger.info(temp)

        # tidied_enum = re.sub(r'[_,.\-;@#?!&$ ]+', ' ', orig_enum)
        tidied_enum = re.sub(r'[' + ecg + ']+', ' ', orig_enum)

        ontologies_phrase = ''
        if len(opg) > 1:
            ontologies_phrase = 'ontology=' + opg.lower()

        qf_phrase = ''
        if len(qfg) > 1:
            qf_phrase = 'queryFields=' + qfg.lower()

        # requiring local loses EROs annotations of SV40
        # 'local=true' + '&' + \
        request_string = 'http://www.ebi.ac.uk/ols/api/search?q=' + \
                         urllib.parse.quote(tidied_enum) + '&' + \
                         'type=class' + '&' + \
                         'exact=false' + '&' + \
                         ontologies_phrase + "&" + \
                         'rows=' + str(rrg) + '&' + \
                         qf_phrase

        logger.debug(request_string)

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
            failures.append(orig_enum)

        ols_string_search_res_frame['query'] = orig_enum
        inner_cosine_obj = Cosine(1)

        annotations_frame = pds.DataFrame(columns=['name', 'obo_id', 'scope', 'type', 'xrefs'])

        for ols_string_search_res_row in ols_string_search_res_frame.itertuples(index=False):
            once = urllib.parse.quote(ols_string_search_res_row.iri, safe='')
            twice = urllib.parse.quote(once, safe='')
            # build url from base
            term_retr_base = 'http://www.ebi.ac.uk/ols/api/ontologies/'
            term_retr_assembled = term_retr_base + ols_string_search_res_row.ontology_name + '/terms/' + twice
            term_details = requests.get(term_retr_assembled)
            term_json = term_details.json()
            has_label = 'label' in set(term_json.keys())
            if has_label:
                logger.debug(term_retr_assembled)
                temp = term_json['label']
                logger.debug(temp)
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

            # # don't process every kind of annotation, like genetic code
            # has_annotations = 'annotation' in set(term_json.keys())
            # if has_annotations:
            #     obo_ano_json = term_json['annotation']
            #     for anokey in obo_ano_json.keys():
            #         for keyval in obo_ano_json[anokey]:
            #             new_row = {'name': keyval,
            #                        'obo_id': term_json['obo_id'],
            #                        'scope': anokey,
            #                        'type': 'annotation',
            #                        'xrefs': '',
            #                        'pref_lab': term_json['label']}
            #             annotations_frame = annotations_frame.append(new_row, ignore_index=True)

            annotations_row_count = len(annotations_frame.index)

            if annotations_row_count == 0:
                logger.warning('NO ANNOTATIONS')
                manual_row = pds.Series(['', '', '', '', '', ''])
                row_df = pds.DataFrame([manual_row], columns=['name', 'obo_id', 'scope', 'type', 'xrefs', 'pref_lab'])
                annotations_frame = pds.concat([row_df, annotations_frame], ignore_index=True)
                failures.append(orig_enum)
            annotations_frame['enum_class'] = one_enum_param
            annotations_frame['query'] = tidied_enum
            annotations_frame['orig_enum'] = orig_enum
            # check whether anny of the annotation on any of the hits have an
            #   acceptable cosine string distance
            annotations_frame['name'] = annotations_frame['name'].fillna('')
            annotations_frame['cosine_dist'] = \
                annotations_frame.apply(lambda row: inner_cosine_obj.distance(tidied_enum.strip().lower(),
                                                                              row['name'].strip().lower()),
                                        axis=1)
            annotations_frame = annotations_frame.sort_values('cosine_dist')
            annotations_frame['dist_ok'] = annotations_frame['cosine_dist'] <= mdg
            annotations_frame['rank'] = list(range(1, len(annotations_frame.index)+1))

            # annotations_frame = annotations_frame[
            #     ['enum_class', 'orig_enum', 'query', 'name', 'cosine_dist', 'dist_ok',
            #      'obo_id', 'pref_lab', 'type', 'scope']]

            annotations_frame = annotations_frame[cols2display]

            # do something with xrefs?
        logger.debug(annotations_frame)

        # get best acceptable row
        acceptable_cosine = annotations_frame[annotations_frame['cosine_dist'] <= mdg]
        acceptable_row_count = len(acceptable_cosine.index)
        if acceptable_row_count > 0:
            best_acceptable = acceptable_cosine.iloc[0]
            success_frame = success_frame.append(best_acceptable)
            # check if permitted value already has a meaning
            meaning_search = list(inferred_model['enums'][one_enum_param]['permissible_values'][orig_enum].keys())
            if 'meaning' in meaning_search:
                has_meaning = True
            else:
                has_meaning = False
            meaningless = not has_meaning
            if meaningless or omg:
                # insert meaning
                inferred_model['enums'][one_enum_param]['permissible_values'][orig_enum]['meaning'] = best_acceptable[
                    'obo_id']
                inferred_model['enums'][one_enum_param]['permissible_values'][orig_enum]['description'] = \
                    best_acceptable['pref_lab']
        else:
            temp = 'NO ACCEPTABLE MAPPINGS FOR ' + one_enum_param + " " + orig_enum
            logger.warning(temp)
            # sort and make unique
            failures.append(orig_enum)
        per_enum_frame = per_enum_frame.append(annotations_frame)
    # I think there will be one success frame for each enum
    success_frame = success_frame[cols2display]
    success_frame = success_frame[list(annotations_frame.columns)]
    logger.info(success_frame)
    return per_enum_frame
