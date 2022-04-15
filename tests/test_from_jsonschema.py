# -*- coding: utf-8 -*-

"""Test the module can be imported."""

import unittest
import os
import json
import yaml
from linkml_runtime.utils.compile_python import compile_python
from linkml_runtime.loaders import json_loader
from linkml_runtime.loaders import yaml_loader

from schema_automator.importers.jsonschema_import_engine import JsonSchemaImportEngine
from linkml_runtime.dumpers import yaml_dumper
from linkml.generators.jsonschemagen import JsonSchemaGenerator
from linkml.generators.pythongen import PythonGenerator

from schema_automator.utils.schemautils import minify_schema
from tests import INPUT_DIR, OUTPUT_DIR

PP = os.path.join(INPUT_DIR, 'phenopackets/phenopackets.schema.json')
OUTSCHEMA = os.path.join(OUTPUT_DIR, 'phenopackets.yaml')

class TestJsonSchemaImport(unittest.TestCase):
    """JSONSchema """

    def _convert(self, fn, suffix='json', path='jsonschema', name=None, root_class_name=None, data_files=[], target_class=None):
        ie = JsonSchemaImportEngine()
        d = os.path.join(INPUT_DIR, path)
        schema = ie.load(os.path.join(d, f'{fn}.{suffix}'), name=name, format=suffix, root_class_name=root_class_name)
        sd = minify_schema(schema)
        model_path = os.path.join(OUTPUT_DIR, f'{fn}.yaml')
        with open(model_path, 'w') as stream:
            yaml.safe_dump(sd, stream, sort_keys=False)
        roundtrip_path = os.path.join(OUTPUT_DIR, f'{fn}.roundtrip.json')
        with open(roundtrip_path, 'w') as stream:
            stream.write(JsonSchemaGenerator(model_path).serialize())
        python_path = os.path.join(OUTPUT_DIR, f'{fn}.py')
        with open(python_path, 'w') as stream:
            stream.write(PythonGenerator(model_path).serialize())
            mod = compile_python(python_path)
        for f in data_files:
            obj = None
            #obj = yaml_loader.load(f, target_class=target_class)
            #print(obj)
        return sd

    def test_convert_dosdp(self):
        """Test JSONSchema conversion."""
        schema = self._convert('dosdp_schema', 'yaml',
                               name='dosdp',
                               root_class_name='Pattern',
                               data_files=['OMIM_disease_series_by_gene.yaml'],
                               target_class='')

    def test_convert_vrs(self):
        """Test JSONSchema conversion."""
        schema = self._convert('vrs.schema', 'json')

    def test_phenopackets(self):
        schema = self._convert('phenopackets.schema', 'json',
                               name='phenopackets',
                               path='phenopackets')

    def test_obo_registry(self):
        schema = self._convert('obo_registry.schema', 'json',
                               name='obo_registry',
                               path='.')

