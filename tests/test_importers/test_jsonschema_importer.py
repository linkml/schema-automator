# -*- coding: utf-8 -*-

"""Test the module can be imported."""

import unittest
import os
from pathlib import Path

from linkml_runtime import SchemaView
from linkml_runtime.utils.compile_python import compile_python

from schema_automator.importers.jsonschema_import_engine import JsonSchemaImportEngine
from linkml_runtime.dumpers import yaml_dumper
from linkml.generators.jsonschemagen import JsonSchemaGenerator
from linkml.generators.pythongen import PythonGenerator

from schema_automator.utils.schemautils import minify_schema, write_schema
from tests import INPUT_DIR, OUTPUT_DIR

#PP = os.path.join(INPUT_DIR, 'phenopackets/phenopackets.schema.json')
#OUTSCHEMA = os.path.join(OUTPUT_DIR, 'phenopackets.yaml')


class TestJsonSchemaImporter(unittest.TestCase):
    """JSONSchema """

    def _convert(self, fn, suffix='json', path='jsonschema', name=None,
                 root_class_name=None, data_files=[], target_class=None):
        """
        Tests conversion of json-schema to linkml, and tests downstream
        products can be generated

        :param fn:
        :param suffix:
        :param path:
        :param name:
        :param root_class_name:
        :param data_files: note uses yet
        :param target_class:
        :return:
        """
        ie = JsonSchemaImportEngine()
        d = os.path.join(INPUT_DIR, path)
        schema = ie.load(os.path.join(d, f'{fn}.{suffix}'), name=name, format=suffix, root_class_name=root_class_name)
        model_path = os.path.join(OUTPUT_DIR, f'{fn}.yaml')
        write_schema(schema, model_path)
        roundtrip_path = os.path.join(OUTPUT_DIR, f'{fn}.roundtrip.json')
        with open(roundtrip_path, 'w') as stream:
            stream.write(JsonSchemaGenerator(model_path).serialize())
        python_path = os.path.join(OUTPUT_DIR, f'{fn}.py')
        with open(python_path, 'w') as stream:
            stream.write(PythonGenerator(model_path).serialize())
            compile_python(python_path)
        # TODO: test data_files
        return schema

    def test_convert_dosdp(self):
        """Tests conversion of DOSDP JSON Schema.
        Note there is a separate importer for DOSDPs themselves
        """
        schema = self._convert('dosdp_schema', 'yaml',
                               name='dosdp',
                               root_class_name='Pattern',
                               data_files=['OMIM_disease_series_by_gene.yaml'],
                               target_class='')
        #print(yaml_dumper.dumps(schema))
        axiom_type_options = schema.enums['axiom_type_options']
        self.assertIn('equivalentTo', axiom_type_options.permissible_values)
        self.assertIn('axiom_type', schema.slots)
        self.assertIn('PrintfClause', schema.classes)

    def test_convert_vrs(self):
        """Test JSONSchema conversion."""
        schema = self._convert('vrs.schema', 'json')
        #print(yaml_dumper.dumps(schema))
        self.assertIn('SimpleInterval', schema.enums['type_options'].permissible_values)
        self.assertIn('location', schema.slots)
        self.assertEqual('SequenceLocation', schema.slots['location'].range)

    def test_phenopackets(self):
        schema = self._convert('phenopackets.schema', 'json',
                               name='phenopackets',
                               path='phenopackets')
        self.assertIn('VCF', schema.enums['hts_format_options'].permissible_values)
        self.assertIn('age', schema.slots)
        self.assertEqual('Evidence', schema.slots['evidence'].range)
        self.assertTrue(schema.slots['evidence'].multivalued)
        self.assertIn('Age', schema.classes)

    def test_obo_registry(self):
        schema = self._convert('obo_registry.schema', 'json',
                               name='obo_registry',
                               path='.')
        #print(yaml_dumper.dumps(schema))
        self.assertIn('active', schema.enums['activity_status_options'].permissible_values)
        self.assertIn('activity_status', schema.slots)
        self.assertEqual('activity_status_options', schema.slots['activity_status'].range)

    def test_import_hca_project(self):
        """This also tests the ability to import a whole project.

        Note that the following modifications were made:

        - changed 10x to S10x
        - modified links to remove name clashes with classes

            - renamed protocol to protocol_reference
            - renamed supplementary_file to supplementary_file_reference

        """
        ie = JsonSchemaImportEngine(use_attributes=True)
        import_path = Path(INPUT_DIR) / "hca"
        export_path = Path(OUTPUT_DIR) / "hca"
        root_path = ie.import_project(import_path, export_path, name="hca")
        sv = SchemaView(root_path)
        c = sv.get_class("OrganPartOntology")
        ont_slot = c.attributes["ontology"]
        rng = ont_slot.range
        edef = sv.get_enum(rng)
        self.assertEqual(2, len(edef.include))
        self.assertIsNotNone(ont_slot.title)
        jsonschema_str = JsonSchemaGenerator(root_path).serialize()


