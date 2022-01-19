import click
import pandas as pd
from linkml_runtime.utils.schemaview import SchemaView, Example
# Annotation
from linkml_runtime.dumpers import yaml_dumper

import logging
import click_log

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
@click.option('--collapse/--no-collapse', default=False)
def curated_to_enums(tsv_in, model_in, selected_enum, tsv_encoding, curated_yaml, collapse):
    from_tsv = pd.read_csv(tsv_in, sep="\t", encoding=tsv_encoding)
    # todo collapse rows with identical meanings?
    # make a new unique pipe-delimited examples column with these values for all rows:
    # text	title	match_pref_lab	match_val	curated_pref_lab	curated_val	examples
    if "pvs_per_meaning" in from_tsv.columns:
        from_tsv.drop(["pvs_per_meaning"], axis=1, inplace=True)
    pvs_per_meaning = from_tsv["meaning"].value_counts()
    pvs_per_meaning = pvs_per_meaning.rename_axis('meaning').reset_index(name='pvs_per_meaning')
    from_tsv = from_tsv.merge(pvs_per_meaning, how="left", on="meaning")
    from_tsv['pvs_per_meaning'] = from_tsv['pvs_per_meaning'].fillna(1)
    if collapse:
        from_tsv = collapse_by_meaning(from_tsv)
    from_tsv.index = from_tsv['text']
    logger.info(from_tsv)
    # check if an index appears more than once
    ft_dict = None
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
        if type(tsv_says["examples"]) == str:
            splitex = tsv_says["examples"].split("|")
            for one_ex in splitex:
                ex_ex = Example(value=one_ex)
                model_says.examples.append(ex_ex)
        model_says.annotations["pvs_per_meaning"] = int(tsv_says["pvs_per_meaning"])
        me_pvs[i] = model_says

    menum.permissible_values = me_pvs

    # todo check for inconsistent annotation structures in YAML

    mschema.enums[selected_enum] = menum
    yaml_dumper.dump(mschema, curated_yaml)


def collapse_by_meaning(pre_collapsed: pd.DataFrame) -> pd.DataFrame:
    singles = pre_collapsed.loc[pre_collapsed['pvs_per_meaning'].lt(2)]
    collapseables = pre_collapsed.loc[pre_collapsed['pvs_per_meaning'].gt(1)]
    collapseable_meanings = list(set(list(collapseables['meaning'])))
    collapseable_meanings.sort()
    collapsed_examples = []
    for i in collapseable_meanings:
        temp = collapseables.loc[
            collapseables['meaning'].eq(i), ['text', 'title', 'match_pref_lab', 'match_val', 'curated_pref_lab',
                                             'curated_val', 'examples']]
        temp = temp.fillna('')
        temp = temp.values.tolist()
        # flatten
        temp = [item for sublist in temp for item in sublist]
        # uniqify
        temp = list(set(temp))
        # drop empty strings
        temp = [item for item in temp if item]
        # todo split (examples) on | and flatten/uniqify again
        temp.sort()
        temp = "|".join(temp)
        collapsed_examples.append({"meaning": i, "examples": temp})
    collapsed_examples = pd.DataFrame(collapsed_examples)
    collapseables.drop(["examples"], axis=1, inplace=True)
    collapseables = collapseables.merge(collapsed_examples, how="left", on="meaning")
    reunited = pd.concat([singles, collapseables])
    # logger.info(reunited)
    return reunited


if __name__ == '__main__':
    curated_to_enums()
