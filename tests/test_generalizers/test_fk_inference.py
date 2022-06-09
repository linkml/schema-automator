# -*- coding: utf-8 -*-

"""Test the module can be imported."""
import logging
import unittest
import os
from linkml_runtime.utils.schemaview import SchemaView

from schema_automator.generalizers.csv_data_generalizer import CsvDataGeneralizer

from schema_automator.utils.schemautils import write_schema
from tests import INPUT_DIR, OUTPUT_DIR

SAMPLES = os.path.join(INPUT_DIR, 'sample.tsv')
ENVO = os.path.join(INPUT_DIR, 'envo.tsv')
SAMPLES_OUTSCHEMA = os.path.join(OUTPUT_DIR, 'sample-schema.yaml')

class TestForeignKeyInference(unittest.TestCase):
    """TSV """

    def test_fk_inference(self):
        """Test ability to infer foreign key linkages using
        sample data and ENVO."""
        ie = CsvDataGeneralizer(downcase_header=True)
        fks = ie.infer_linkages([ENVO, SAMPLES])
        #fks = ie.infer_linkages([SAMPLES, ENVO])
        self.assertEqual(len(fks), 3)
        logging.info('FKS:')
        expected = ['envo_biome_id', 'envo_feature_id', 'envo_material_id']
        for fk in fks:
            logging.info(fk)
            if fk.source_table == 'sample' and fk.target_column == 'envo_id' and fk.num_distinct_values > 0:
                if fk.source_column in expected:
                    expected.remove(fk.source_column)
                else:
                    raise Exception(f'Unexpected FK: {fk}')
        assert expected == []



    def test_schema_with_fk_inference(self):
        """Tests foreign key inference."""
        ie = CsvDataGeneralizer(downcase_header=True, infer_foreign_keys=True)
        schema = ie.convert_multiple([ENVO, SAMPLES])
        write_schema(schema, SAMPLES_OUTSCHEMA)
        #ys = yaml.dump(schema_dict, default_flow_style=False, sort_keys=False)
        #with open(SAMPLES_OUTSCHEMA, 'w') as stream:
        #    stream.write(ys)
        sv = SchemaView(schema)
        expected = ['envo_biome_id', 'envo_feature_id', 'envo_material_id']
        for sn in expected:
            s = sv.induced_slot(sn, 'sample')
            assert s.range == 'envo'
            c = sv.get_class(s.range)
            assert c.name == 'envo'
