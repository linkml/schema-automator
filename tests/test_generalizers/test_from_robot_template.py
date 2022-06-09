# -*- coding: utf-8 -*-

"""Test the module can be imported."""

import unittest
import os
from schema_automator.generalizers.csv_data_generalizer import CsvDataGeneralizer
from linkml.generators.yamlgen import YAMLGenerator
from linkml_runtime.utils.schemaview import SchemaView

from schema_automator.utils.schemautils import write_schema
from tests import INPUT_DIR, OUTPUT_DIR

BIOBANK_SPECIMENS = os.path.join(INPUT_DIR, 'biobank-specimens.tsv')
OUTSCHEMA = os.path.join(OUTPUT_DIR, 'biobank.yaml')
OUTSCHEMA_ENHANCED = os.path.join(OUTPUT_DIR, 'biobank.enhanced.yaml')

class TestRobotTemplateImport(unittest.TestCase):
    """tests import from a robot template """

    def test_from_robot_template(self):
        """Test that expando can be imported."""
        ie = CsvDataGeneralizer(robot=True)
        schema = ie.convert(BIOBANK_SPECIMENS, class_name='BiobankSpecimen', name='biobank')
        write_schema(schema, OUTSCHEMA)
        sv = SchemaView(OUTSCHEMA)
        s = YAMLGenerator(OUTSCHEMA).serialize()
        with open(OUTSCHEMA_ENHANCED, 'w') as stream:
            stream.write(s)
        for cn, c in sv.all_class().items():
            print(f'C: {cn}')
            for s in sv.class_induced_slots(cn):
                print(f'  S: {s.name} {s.identifier}')
            id_slot = sv.get_identifier_slot(cn)
            print(f'ID = {id_slot}')
            if cn == 'BiobankSpecimen':
                assert id_slot.name == 'Ontology ID'


