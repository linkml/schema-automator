# -*- coding: utf-8 -*-

"""Test the module can be imported."""

import unittest
import os
from linkml_runtime.utils.schemaview import SchemaView

from schema_automator.generalizers.json_instance_generalizer import JsonDataGeneralizer
from linkml.generators.yamlgen import YAMLGenerator

from schema_automator.utils.schemautils import write_schema
from tests import INPUT_DIR, OUTPUT_DIR

IN = os.path.join(INPUT_DIR, 'synonymizer.yaml')
IN_GOLD = os.path.join(INPUT_DIR, 'neon-in-gold.json.gz')
OUTSCHEMA = os.path.join(OUTPUT_DIR, 'syn-schema.yaml')
OUTSCHEMA_ENHANCED = os.path.join(OUTPUT_DIR, 'syn-schema2.yaml')
OUTSCHEMA_GOLD = os.path.join(OUTPUT_DIR, 'neon-in-gold-inf.yaml')


class TestJsonDataGeneralizer(unittest.TestCase):
    """Tests ability to generalize from JSON instance data to a LinkML schema """

    def test_from_json(self):
        """Test inference of a schema from JSON instance data (small example)."""
        ie = JsonDataGeneralizer()
        schema = ie.convert(IN, format='yaml')
        write_schema(schema, OUTSCHEMA)
        s = YAMLGenerator(OUTSCHEMA).serialize()
        with open(OUTSCHEMA_ENHANCED, 'w') as stream:
            stream.write(s)
        sv = SchemaView(OUTSCHEMA)
        assert 'NewSynonym' in sv.get_enum(sv.induced_slot('type', 'Rules').range).permissible_values


    def test_gold_neon(self):
        """Test inference of a schema from JSON instance data (GOLD API example)."""
        ie = JsonDataGeneralizer()
        ie.omit_null = True
        BIOSAMPLE = 'Biosample'
        schema = ie.convert(IN_GOLD, format='json.gz', container_class_name=BIOSAMPLE)
        write_schema(schema, OUTSCHEMA_GOLD)
        sv = SchemaView(OUTSCHEMA_GOLD)
        assert BIOSAMPLE in sv.all_classes()
        habitat_slot = sv.induced_slot('habitat', BIOSAMPLE)
        assert 'Mixed forest soil' in sv.get_enum(habitat_slot.range).permissible_values
        assert 'latitude' in sv.get_class(BIOSAMPLE).slots
        # omit null
        assert 'hostGender' not in sv.get_class(BIOSAMPLE).slots


