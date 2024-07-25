# -*- coding: utf-8 -*-

"""Test the module can be imported."""

import unittest
import os
import yaml
from schema_automator.importers.owl_import_engine import OwlImportEngine
from linkml.generators.yamlgen import YAMLGenerator

from schema_automator.utils.schemautils import write_schema
from tests import INPUT_DIR, OUTPUT_DIR

PROV = os.path.join(INPUT_DIR, 'prov.ofn')
DIR = os.path.join(OUTPUT_DIR, 'prov')
OUTSCHEMA = os.path.join(OUTPUT_DIR, 'prov-from-owl.yaml')
OUTSCHEMA_ENHANCED = os.path.join(OUTPUT_DIR, 'prov-from-owl.enhanced.yaml')

class TestOwlImporter(unittest.TestCase):
    """Tests OWL conversion """

    def test_from_owl(self):
        """Test OWL conversion on reproschema."""
        oie = OwlImportEngine()
        schema = oie.convert(PROV, name='prov')
        write_schema(schema, OUTSCHEMA)
        s = YAMLGenerator(OUTSCHEMA).serialize()
        with open(OUTSCHEMA_ENHANCED, 'w') as stream:
            stream.write(s)

    def test_anon_individuals(self):
        """
        Test that anonymous individuals are handled correctly
        """
        oie = OwlImportEngine()
        schema = oie.convert(os.path.join(INPUT_DIR, 'test-anon-individual.ofn'), name='anon_individuals')
        write_schema(schema, os.path.join(OUTPUT_DIR, 'anon-individual-from-owl.yaml'))


