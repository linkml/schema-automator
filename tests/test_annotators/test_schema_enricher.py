# -*- coding: utf-8 -*-

import logging
import os
import unittest
from linkml.utils.schema_builder import SchemaBuilder
from linkml_runtime.dumpers import yaml_dumper
from linkml_runtime.linkml_model import SchemaDefinition, EnumDefinition, PermissibleValue
from oaklib.implementations import BioPortalImplementation
from oaklib.selector import get_implementation_from_shorthand

from schema_automator.annotators.schema_annotator import SchemaAnnotator
from linkml.generators.yamlgen import YAMLGenerator
from tests import INPUT_DIR, OUTPUT_DIR


class SchemaEnricherTestCase(unittest.TestCase):
    """
    Tests :ref:`SchemaAnnotator`
    """

    def setUp(self) -> None:
        """
        Use a fragment of the Sequence Ontology as a test case
        """
        impl = get_implementation_from_shorthand(os.path.join(INPUT_DIR, "so-mini.obo"))
        self.annotator = SchemaAnnotator(impl)

    def test_enrich(self):
        sb = SchemaBuilder('test')
        schema = sb.schema
        sb.add_class('Gene', class_uri="SO:0000704").add_slot('part_of')
        schema.slots['part_of'].exact_mappings.append("BFO:0000050")
        sb.add_enum('GeneType', permissible_values=['ncRNA_gene', 'scRNA_gene'])
        gt = schema.enums['GeneType']
        gt.permissible_values['ncRNA_gene'].meaning = 'SO:0001263'
        gt.permissible_values['scRNA_gene'].meaning = 'SO:0001266'
        s = self.annotator.enrich(schema)
        #print(yaml_dumper.dumps(s))
        assert s.classes['Gene'].description.startswith("A region")
        assert s.slots['part_of'].description.startswith("this is")
        self.assertEqual("A gene that encodes a non-coding RNA.",
                         gt.permissible_values['ncRNA_gene'].description)
        self.assertEqual("A gene encoding a small noncoding RNA that is generally found only in the cytoplasm.",
                         gt.permissible_values['scRNA_gene'].description)



