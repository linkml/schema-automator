# -*- coding: utf-8 -*-

"""Test the module can be imported."""

import unittest
import os
import yaml
from linkml.generators.pythongen import PythonGenerator
from linkml.utils import sqlutils
from linkml.utils.schema_builder import SchemaBuilder
from linkml.utils.sqlutils import SQLStore
from linkml_runtime import SchemaView
from linkml_runtime.dumpers import yaml_dumper
from linkml_runtime.linkml_model import SlotDefinition
from sqlalchemy.orm import sessionmaker

from schema_automator.importers.owl_import_engine import OwlImportEngine
from linkml.generators.yamlgen import YAMLGenerator

from schema_automator.importers.sql_import_engine import SqlImportEngine
from schema_automator.utils.schemautils import write_schema
from tests import INPUT_DIR, OUTPUT_DIR

DB = os.path.join(OUTPUT_DIR, 'tmp.db')


class TestSqlmporter(unittest.TestCase):
    """Imports SQL """

    def setUp(self) -> None:
        """
        Creates a SQL Lite database
        :return:
        """
        sb = SchemaBuilder()
        sb.add_class('Person',
                     ['id', 'name', 'email', 'age', 'knows'])
        sb.add_slot(SlotDefinition('id', identifier=True), replace_if_present=True)
        sb.add_slot(SlotDefinition('age', range='integer'), replace_if_present=True)
        sb.add_slot(SlotDefinition('knows', range='Person', multivalued=True), replace_if_present=True)
        sb.add_defaults()
        schema = sb.schema
        #print(yaml_dumper.dumps(schema))
        # TODO: add to SchemaBuilder
        for c in schema.classes.values():
            c.from_schema = 'http://x.org/'
        python_module = PythonGenerator(schema).compile_module()
        sql_store = SQLStore(schema, database_path=DB)
        sql_store.native_module = python_module
        sql_store.db_exists(force=True)
        sql_store.compile()
        self.schema = schema
        self.schemaview = SchemaView(schema)

    def test_from_sql(self):
        """
        Test SQL conversion

        The strategy is to first build up a schema dynamically,
        use existing linkml to convert, then reverse engineer it
        """
        ie = SqlImportEngine()
        schema_rt = ie.convert(DB)
        schemaview_rt = SchemaView(schema_rt)
        print(yaml_dumper.dumps(schema_rt))
        schemaview = self.schemaview
        for c in schemaview.all_classes().values():
            self.assertIn(c.name, schemaview_rt.all_classes())
            for s in schemaview.class_induced_slots(c.name):
                if s.name == "knows":
                    # these slots are moved to join tables
                    self.assertNotIn(s.name, schemaview_rt.all_slots().keys())
                else:
                    self.assertIn(s.name, schemaview_rt.all_slots().keys())
        person = schemaview_rt.get_class('Person')
        person_knows_join = schemaview_rt.get_class('Person_knows')
        id_slot = person.attributes['id']
        age_slot = person.attributes['age']
        self.assertTrue(id_slot.identifier)
        self.assertEqual('integer', age_slot.range)
        self.assertEqual('Person', person_knows_join.attributes['Person_id'].range)
        self.assertEqual('Person', person_knows_join.attributes['knows_id'].range)







