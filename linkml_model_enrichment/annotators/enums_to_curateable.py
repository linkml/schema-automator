import click
import pandas as pd
from linkml_runtime.utils.schemaview import SchemaView

# specify normalized_dist and dist type?
blank_row = {"text": "", "title": "", "meaning": "", "match_id": "", "match_pref_lab": "", "match_type": "",
             "match_val": "", "cosine": "", "curated_id": "", "curated_pref_lab": "", "curated_type": "",
             "curated_val": "", "curation_notes": "", }
br_keys = list(blank_row.keys())
br_keys.sort()


@click.command()
@click.option('--modelfile', type=click.Path(exists=True), required=True)
@click.option('--tsv_out', type=click.Path(), default="enums_to_curateable.tsv", show_default=True)
@click.option('--enum', required=True)
def enums_to_curateable(modelfile, enum, tsv_out):
    row_list = []
    mschema = SchemaView(modelfile)
    menum = mschema.get_enum(enum)
    mpvs = menum.permissible_values
    for apvt, apvd in mpvs.items():
        current_blank = blank_row.copy()
        apvd_annotations = apvd.annotations
        apvd_anno_keys = list(apvd_annotations.keys())
        for i in br_keys:
            if i in apvd_anno_keys:
                current_blank[i] = apvd_annotations[i].value
            elif i in apvd:
                current_blank[i] = apvd[i]
        row_list.append(current_blank)
        row_frame = pd.DataFrame(row_list)
    print(row_frame)
    row_frame.to_csv(tsv_out, sep="\t", index=False)


if __name__ == '__main__':
    enums_to_curateable()
