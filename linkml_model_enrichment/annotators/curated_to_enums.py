import click
import pandas as pd
from linkml_runtime.utils.schemaview import SchemaView, Annotation
from linkml_runtime.dumpers import yaml_dumper

import logging
import click_log

# todo add logger
logger = logging.getLogger(__name__)
click_log.basic_config(logger)


# overwrites by default?
@click.command()
@click_log.simple_verbosity_option(logger)
@click.option('--tsv_in', type=click.Path(exists=True), required=True)
@click.option('--tsv_encoding', default="utf_16", show_default=True)
@click.option('--model_in', type=click.Path(exists=True), required=True)
@click.option('--curated_yaml', type=click.Path(), default="curated.yaml", show_default=True)
@click.option('--selected_enum', required=True)
def curated_to_enums(tsv_in, model_in, selected_enum, tsv_encoding, curated_yaml):
    from_tsv = pd.read_csv(tsv_in, sep="\t", encoding=tsv_encoding)
    from_tsv.index = from_tsv['text']
    logger.info(from_tsv)
    # check if an index appears more than once
    if from_tsv.index.is_unique:
        ft_dict = from_tsv.to_dict(orient="index")
    else:
        logger.error("index is not unique")
        exit()

    from_model = SchemaView(model_in)
    mschema = from_model.schema

    menum = from_model.get_enum(selected_enum)
    me_pvs = menum.permissible_values
    mep_keys = list(me_pvs.keys())
    mep_keys.sort()

    ft_keys = [i for i in list(ft_dict.keys()) if i == str(i)]
    ft_keys.sort()

    comparables = list(set(mep_keys).intersection(set(ft_keys)))
    comparables.sort()

    for i in comparables:
        logger.info(i)
        model_says = me_pvs[i]
        tsv_says = ft_dict[i]
        if not pd.isna(tsv_says['curated_id']) and not pd.isna(tsv_says['curated_pref_lab']) and not pd.isna(
                tsv_says['curated_type']) and not pd.isna(tsv_says['curated_val']):
            model_says.meaning = tsv_says['curated_id']
            model_says.title = tsv_says['curated_pref_lab']
            # todo delete them, don't set to empty strings
            model_says.annotations["match_id"] = tsv_says["curated_id"]
            model_says.annotations["match_pref_lab"] = tsv_says["curated_pref_lab"]
            model_says.annotations["match_type"] = tsv_says["curated_type"]
            model_says.annotations["match_val"] = tsv_says["curated_val"]
            model_says.annotations["curation_notes"] = tsv_says["curation_notes"]
            model_says.annotations["cosine"] = None
            model_says.annotations["curated"] = True
            me_pvs[i] = model_says

    menum.permissible_values = me_pvs

    meanings_tally = []
    for i in mep_keys:
        i_m = menum.permissible_values[i].meaning
        meanings_tally.append(i_m)

    # todo for collapsing pvs to get one with each meaning, the texts could be aliases or something like that?
    #   don't see an applicable slot at https://linkml.io/linkml-model/docs/PermissibleValue/#class-permissible_value

    pvs_per_meaning = pd.Series(meanings_tally).value_counts(dropna=False)

    for i in mep_keys:
        i_a = menum.permissible_values[i].annotations
        i_m = menum.permissible_values[i].meaning
        if i_m in pvs_per_meaning:
            # todo inconsistent annotation structure
            i_a["pvs_per_meaning"] = Annotation(tag="pvs_per_meaning", value=pvs_per_meaning[i_m])
            menum.permissible_values[i].annotations = i_a

    mschema.enums[selected_enum] = menum
    yaml_dumper.dump(mschema, curated_yaml)


if __name__ == '__main__':
    curated_to_enums()
