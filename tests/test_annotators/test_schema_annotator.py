# -*- coding: utf-8 -*-

"""Test the module can be imported."""
import logging
import unittest
import os
import yaml
from schema_automator.annotators.schema_annotator import SchemaAnnotator
from linkml.generators.yamlgen import YAMLGenerator
from tests import INPUT_DIR, OUTPUT_DIR


KEYPATH = os.path.join('../conf', 'bioportal_apikey.txt')

class testAnnotator(unittest.TestCase):
    """NCBO """

    def test_ann(self):
        if os.path.exists(KEYPATH):
            logging.basicConfig(level=logging.DEBUG)
            annr = SchemaAnnotator()
            annr.load_bioportal_api_key(KEYPATH)
            #resultset = annr.annotate_text("Northwest_Latitude_Coordinate", include=None, require_exact_match=True)
            resultset = annr.annotate_text("melanoma", include=None, require_exact_match=True)
            for r in resultset.results:
                print(yaml.dump(r))
                print(f'COMPLETE = {r.complete()}')
                for a in r.annotations:
                    print(f'  C={a.complete()} // {a}')
        else:
            print('No API key: skipping test')


