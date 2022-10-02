# -*- coding: utf-8 -*-

"""Test the module can be imported."""

import unittest
import os
import yaml
import glob
from linkml_runtime.loaders import yaml_loader

from schema_automator.metamodels.dosdp.model import Pattern
from linkml.generators.owlgen import OwlSchemaGenerator

from schema_automator.utils.schemautils import minify_schema
from schema_automator.importers.dosdp_import_engine import DOSDPImportEngine
from tests import INPUT_DIR, OUTPUT_DIR

DOSDP_DIR = os.path.join(INPUT_DIR, 'dosdp')
META_OWL_OUTPUT = os.path.join(OUTPUT_DIR, 'mondo_dps.owl')

def load_dp(path) -> Pattern:
    with open(path) as stream:
        obj = yaml.safe_load(stream)
    if 'def' in obj:
        obj['definition'] = obj['def']
        del obj['def']
    return yaml_loader.load(obj, target_class=Pattern)

class TestDOSDPImporter(unittest.TestCase):
    """Tests import from DOSDP yaml templates """

    def test_dosdp_import(self):
        """
        Test importing a folder
        """
        ie = DOSDPImportEngine()
        files = glob.glob(os.path.join(DOSDP_DIR, '*.yaml'))
        print(f'LOADING: {files}')
        schema = ie.convert(files,
                            id='https://example.org/mondo/',
                            name='mondo', range_as_enums=False)
        #print(schema)
        sd = minify_schema(schema)
        model_path = os.path.join(OUTPUT_DIR, 'mondo_dps.yaml')
        with open(model_path, 'w') as stream:
            yaml.safe_dump(sd, stream, sort_keys=False)
        with open(META_OWL_OUTPUT, 'w') as stream:
            stream.write(OwlSchemaGenerator(model_path, type_objects=False, metaclasses=False).serialize())



