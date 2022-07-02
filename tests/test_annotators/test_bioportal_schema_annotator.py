# -*- coding: utf-8 -*-

import logging
import unittest
import os
import yaml
from linkml.utils.schema_builder import SchemaBuilder
from linkml_runtime.dumpers import yaml_dumper
from linkml_runtime.linkml_model import SchemaDefinition, EnumDefinition, PermissibleValue
from oaklib.implementations import BioportalImplementation
from oaklib.selector import get_implementation_from_shorthand

from schema_automator.annotators.schema_annotator import SchemaAnnotator
from linkml.generators.yamlgen import YAMLGenerator
from tests import INPUT_DIR, OUTPUT_DIR


class BioPortalSchemaAnnotatorTestCase(unittest.TestCase):
    """
    Tests schema annotator using bioportal.

    Note that currently this test will be skipped on github actions.

    To run this test locally follow the OAK instructions for setting the Bioportal API key
    """

    def setUp(self) -> None:
        impl = BioportalImplementation()
        try:
            impl.load_bioportal_api_key()
        except ValueError:
            self.skipTest("Skipping bioportal tests, no API key set")
        self.annotator = SchemaAnnotator(impl)

    def test_ann(self):
        s = SchemaDefinition(id='test', name='test')
        sb = SchemaBuilder(s)
        sb.add_class('Gene').add_slot('symbol')
        # TODO: use add_enum
        e = EnumDefinition('GeneType')
        s.enums[e.name] = e
        # Test case involves use of CamelCase
        pv1 = PermissibleValue('ProteinCodingGene')
        pv2 = PermissibleValue('RNAGene')
        e.permissible_values[pv1.text] = pv1
        e.permissible_values[pv2.text] = pv2
        self.annotator.annotate_schema(s, curie_only=True)
        print(yaml_dumper.dumps(s))
        gene = list(s.classes.values())[0]
        self.assertIn('SO:0000704', gene.exact_mappings)
        gene_type = list(s.enums.values())[0]
        self.assertIn('NCIT:C25284', gene_type.exact_mappings)
        for pv in gene_type.permissible_values.values():
            self.assertIsNotNone(pv.meaning)
            self.assertGreater(len(pv.exact_mappings), 1)


