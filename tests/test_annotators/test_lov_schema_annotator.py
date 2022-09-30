# -*- coding: utf-8 -*-

import logging
import unittest
import os
import yaml
from linkml.utils.schema_builder import SchemaBuilder
from linkml_runtime.dumpers import yaml_dumper
from linkml_runtime.linkml_model import SchemaDefinition, EnumDefinition, PermissibleValue
from oaklib import OntologyResource
from oaklib.implementations import BioPortalImplementation
from oaklib.implementations.sparql.lov_implementation import LovImplementation
from oaklib.selector import get_implementation_from_shorthand

from schema_automator.annotators.schema_annotator import SchemaAnnotator
from linkml.generators.yamlgen import YAMLGenerator
from tests import INPUT_DIR, OUTPUT_DIR


class LovSchemaAnnotatorTestCase(unittest.TestCase):
    """
    Tests schema annotator using LOV.
    """

    def setUp(self) -> None:
        impl = LovImplementation(OntologyResource())
        self.annotator = SchemaAnnotator(impl)

    @unittest.skip("Currently incomplete")
    def test_ann(self):
        s = SchemaDefinition(id='test', name='test')
        sb = SchemaBuilder(s)
        sb.add_class('Person').add_slot('full_name').add_slot('phone_number')
        # TODO: use add_enum
        e = EnumDefinition('VitalStatus')
        s.enums[e.name] = e
        pv1 = PermissibleValue('LIVING')
        pv2 = PermissibleValue('DEAD')
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


