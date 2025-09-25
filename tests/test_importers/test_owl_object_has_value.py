"""
Test case for ObjectHasValue support in OWL import engine
"""

import unittest
import tempfile
import os
from schema_automator.importers.owl_import_engine import OwlImportEngine


class TestObjectHasValue(unittest.TestCase):
    """Test ObjectHasValue constraint handling"""

    def test_object_has_value_constraint(self):
        """Test that ObjectHasValue constraints are properly converted to equals_string"""
        
        # Simple OWL functional syntax with ObjectHasValue constraint
        owl_content = '''
Prefix(:=<http://example.org/test#>)
Prefix(owl:=<http://www.w3.org/2002/07/owl#>)
Prefix(rdf:=<http://www.w3.org/1999/02/22-rdf-syntax-ns#>)
Prefix(rdfs:=<http://www.w3.org/2000/01/rdf-schema#>)

Ontology(<http://example.org/test>

Declaration(Class(:TestClass))
Declaration(ObjectProperty(:hasState))
Declaration(NamedIndividual(:SolidState))

SubClassOf(:TestClass ObjectHasValue(:hasState :SolidState))

)'''
        
        # Write to temporary file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.ofn', delete=False) as f:
            f.write(owl_content)
            temp_file = f.name
        
        try:
            # Convert using our engine
            engine = OwlImportEngine()
            schema = engine.convert(temp_file, name='test')
            
            # Check that the constraint was properly converted
            self.assertIn('TestClass', schema.classes)
            test_class = schema.classes['TestClass']
            
            # Should have slot_usage with equals_string constraint
            self.assertIn('slot_usage', test_class)
            self.assertIn('hasState', test_class['slot_usage'])
            self.assertIn('equals_string', test_class['slot_usage']['hasState'])
            self.assertEqual(test_class['slot_usage']['hasState']['equals_string'], 'SolidState')
            
        finally:
            # Clean up
            os.unlink(temp_file)


if __name__ == '__main__':
    unittest.main()
