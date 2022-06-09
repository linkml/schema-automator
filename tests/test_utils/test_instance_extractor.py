# -*- coding: utf-8 -*-

"""Test the module can be imported."""

import unittest
import os
from linkml_runtime.linkml_model import SchemaDefinition, ClassDefinition
from linkml_runtime.loaders import yaml_loader
from linkml_runtime.utils.introspection import package_schemaview
from linkml_runtime.dumpers import yaml_dumper
from schema_automator.utils.instance_extractor import InstanceView
from tests import INPUT_DIR, OUTPUT_DIR

SCHEMA = os.path.join(INPUT_DIR, 'kitchen_sink.yaml')

class TestInstanceExtractor(unittest.TestCase):
    """
    Tests instance extraction
    """

    def setUp(self) -> None:
        root: SchemaDefinition
        self.root = yaml_loader.loads(SCHEMA, SchemaDefinition)
        meta_sv = package_schemaview('linkml_runtime.linkml_model.meta')
        self.iv = InstanceView(root=self.root, schemaview=meta_sv)
        self.iv.create_index()

    def test_index(self):
        iv = self.iv
        id_to_path = iv.id_to_path
        #for k, v in id_to_path.items():
        #    print(f'{k} = {v}')
        self.assertEqual(['slots', 'has employment history'], id_to_path['has employment history'])
        #self.assertEqual(['slots', 'id'], id_to_path['id'])
        self.assertNotIn('id', id_to_path)  ## imports not resolved by default
        self.assertEqual(['enums', 'EmploymentEventType'], id_to_path['EmploymentEventType'])
        obj = iv.fetch_object('Person')
        #print(obj)
        self.assertEqual(type(obj), ClassDefinition)
        self.assertEqual(obj.id_prefixes, ['P'])
        #for s, o in iv.references:
        #    if s is not None:
        #        print(f'T={s.name} -- {o}')

    def test_extract(self):
        ie = self.iv
        #refs = ie.get_object_references(root.classes['Concept'], 'class_definition')
        #print(refs)
        #self.assertCountEqual(['id', 'name', 'in code system', 'Concept'], refs)
        c = ie.fetch_object('DiagnosisConcept')
        print(c)
        refs = ie.get_object_references(c)
        print(refs)
        self.assertCountEqual(['in code system', 'DiagnosisConcept', 'Concept', 'CodeSystem', 'name', 'id'], refs)
        subschema = ie.extract(['MedicalEvent'])
        #print(yaml_dumper.dumps(subschema))
        self.assertIn('Concept', subschema.classes)
        self.assertIn('Event', subschema.classes)
        self.assertIn('diagnosis', subschema.slots)
        self.assertNotIn('Person', subschema.classes)
        subschema = ie.extract(['FamilialRelationship'])
        self.assertIn('Event', subschema.classes)
        self.assertIn('FamilialRelationshipType', subschema.enums)
        self.assertIn('diagnosis', subschema.slots)
        subschema = ie.extract(['employed at'])
        print(yaml_dumper.dumps(subschema))
        self.assertIn('Event', subschema.classes)
        self.assertIn('FamilialRelationshipType', subschema.enums)
        self.assertIn('diagnosis', subschema.slots)



