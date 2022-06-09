# -*- coding: utf-8 -*-

"""Test the module can be imported."""

import unittest
import os
from schema_automator.generalizers.rdf_data_generalizer import RdfDataGeneralizer
from linkml.generators.yamlgen import YAMLGenerator

from schema_automator.utils.schemautils import write_schema
from tests import INPUT_DIR, OUTPUT_DIR

PROV = os.path.join(INPUT_DIR, 'prov.ttl')
DIR = os.path.join(OUTPUT_DIR, 'prov')
OUTSCHEMA = os.path.join(OUTPUT_DIR, 'rdfs-from-prov.yaml')
OUTSCHEMA_ENHANCED = os.path.join(OUTPUT_DIR, 'rdfs-from-prov.enhanced.yaml')

class TestRdfDataGeneralizer(unittest.TestCase):
    """Tests generalization from RDF triples """

    def test_from_rdf(self):
        sie = RdfDataGeneralizer()
        if not os.path.exists(DIR):
            os.makedirs(DIR)
        schema = sie.convert(PROV, dir=DIR, format='ttl')
        write_schema(schema, OUTSCHEMA)
        s = YAMLGenerator(OUTSCHEMA).serialize()
        with open(OUTSCHEMA_ENHANCED, 'w') as stream:
            stream.write(s)

