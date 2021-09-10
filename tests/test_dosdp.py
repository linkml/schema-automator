# -*- coding: utf-8 -*-

"""Test the module can be imported."""

import unittest
import os
import json
import yaml
import glob
from linkml_runtime.utils.compile_python import compile_python
from linkml_runtime.loaders import json_loader
from linkml_runtime.loaders import yaml_loader

from linkml_model_enrichment.dosdp.model import Pattern
from linkml_runtime.dumpers import yaml_dumper
from linkml.generators.jsonschemagen import JsonSchemaGenerator
from linkml.generators.pythongen import PythonGenerator

from linkml_model_enrichment.utils.schemautils import minify_schema
from linkml_model_enrichment.importers.dosdp_import_engine import DOSDPImportEngine
from tests import INPUT_DIR, OUTPUT_DIR

DOSDP_DIR = os.path.join(INPUT_DIR, 'dosdp')
DP = os.path.join(INPUT_DIR, 'dosdp/OMIM_disease_series_by_gene.yaml')

def load_dp(path) -> Pattern:
    with open(path) as stream:
        obj = yaml.safe_load(stream)
    if 'def' in obj:
        obj['definition'] = obj['def']
        del obj['def']
    #print(obj)
    return yaml_loader.load(obj, target_class=Pattern)

class TestDOSDP(unittest.TestCase):
    """DOSDP """

    def test_dosdp_import(self):
        ie = DOSDPImportEngine()
        files = glob.glob(os.path.join(DOSDP_DIR, '*.yaml'))
        print(f'LOADING: {files}')
        schema = ie.convert(files, id='mondo', name='mondo')
        #print(schema)
        sd = minify_schema(schema)
        model_path = os.path.join(OUTPUT_DIR, 'mondo_dps.yaml')
        with open(model_path, 'w') as stream:
            yaml.safe_dump(sd, stream, sort_keys=False)



