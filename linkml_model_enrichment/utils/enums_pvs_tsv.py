import logging
import click
import click_log
import pandas as pd
from linkml_runtime.utils.schemaview import SchemaView

logger = logging.getLogger(__name__)
click_log.basic_config(logger)


@click.command()
@click_log.simple_verbosity_option(logger)
@click.option('--modelfile', help="path to LinkML input", type=click.Path(exists=True), show_default=True,
              required=True)
@click.option('--output_file', help="path to TSV output", type=click.Path(), required=True)
def enums_pvs_tsv(modelfile, output_file):
    """
    Writes a TSV report of the enums and permissible values in modelfile (a LinkML YAML file) to output_file (a TSV file).
    """
    row_list = []
    view = SchemaView(modelfile)
    enums = view.all_enums()
    for ek, ev in enums.items():
        pvs = ev.permissible_values
        for pk, pv in pvs.items():
            logger.debug(f"{ek}: {pk}")
            row_list.append({"enum": ek, "pv": pk})
    row_frame = pd.DataFrame(row_list)
    row_frame.to_csv(output_file, sep="\t", index=False)


if __name__ == '__main__':
    enums_pvs_tsv()
