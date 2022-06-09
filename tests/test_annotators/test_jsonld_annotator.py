# -*- coding: utf-8 -*-

"""Test the module can be imported."""

import unittest
import os
import json
import yaml
from linkml_runtime.utils.compile_python import compile_python
from linkml_runtime.loaders import json_loader
from linkml_runtime.loaders import yaml_loader
from linkml_runtime.utils.schema_as_dict import schema_as_dict

from schema_automator.annotators.jsonld_annotator import JsonLdAnnotator
from schema_automator.importers.jsonschema_import_engine import JsonSchemaImportEngine
from linkml_runtime.dumpers import yaml_dumper
from linkml.generators.jsonschemagen import JsonSchemaGenerator
from linkml.generators.pythongen import PythonGenerator

from schema_automator.utils.schemautils import minify_schema
from tests import INPUT_DIR, OUTPUT_DIR

JSONSCHEMA = os.path.join(INPUT_DIR, 'obo_registry.schema.json')
CONTEXT = os.path.join(INPUT_DIR, 'obo_registry.context.jsonld')
OUTSCHEMA = os.path.join(OUTPUT_DIR, 'obo_registry.yaml')

class TestJsonLdAnnotator(unittest.TestCase):

    def test_annotate(self):
        ie = JsonSchemaImportEngine()
        schema = ie.load(JSONSCHEMA)
        ann = JsonLdAnnotator()
        ann.annotate(schema, CONTEXT)
        assert 'foaf' in schema.prefixes
        assert schema.prefixes['foaf'].prefix_reference == 'http://xmlns.com/foaf/0.1/'
        assert schema.slots['title'].slot_uri == 'dce:title'
        sd = schema_as_dict(schema)
        with open(OUTSCHEMA, 'w') as stream:
            yaml.safe_dump(sd, stream, sort_keys=False)


