# -*- coding: utf-8 -*-

import logging
import os
import unittest
from linkml.utils.schema_builder import SchemaBuilder
from linkml_runtime.dumpers import yaml_dumper
from linkml_runtime.linkml_model import SchemaDefinition, EnumDefinition, PermissibleValue
from oaklib.implementations import BioportalImplementation
from oaklib.selector import get_implementation_from_shorthand

from schema_automator.annotators.schema_annotator import SchemaAnnotator
from linkml.generators.yamlgen import YAMLGenerator
from tests import INPUT_DIR, OUTPUT_DIR


class SchemaEnricherTestCase(unittest.TestCase):

    def setUp(self) -> None:
        impl = get_implementation_from_shorthand(os.path.join(INPUT_DIR, "so-mini.obo"))
        self.annotator = SchemaAnnotator(impl)

    def test_enrich(self):
        sb = SchemaBuilder('test')
        sb.add_class('Gene', class_uri="SO:0000704").add_slot('part_of')
        s = self.annotator.enrich(sb.schema)
        #print(yaml_dumper.dumps(s))
        assert s.classes['Gene'].description.startswith("A region")



