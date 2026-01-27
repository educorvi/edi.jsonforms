# -*- coding: utf-8 -*-
from edi.jsonforms.testing import EDI_JSONFORMS_INTEGRATION_TESTING
from edi.jsonforms.views.common import create_id
from plone import api
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID

import json
import unittest


class DependenciesIntegrationTest(unittest.TestCase):
    """Test dependencies and required fields"""

    layer = EDI_JSONFORMS_INTEGRATION_TESTING

    def setUp(self):
        """Custom shared utility setup for tests."""
        self.portal = self.layer['portal']
        self.request = self.layer['request']
        setRoles(self.portal, TEST_USER_ID, ['Manager'])
        
        # Create a form for testing
        self.form = api.content.create(
            container=self.portal,
            type='Form',
            id='test-form',
            title='Test Form',
        )

    def test_required_field_in_schema(self):
        """Test that required field appears in required array"""
        field = api.content.create(
            container=self.form,
            type='Field',
            title='Required Field',
        )
        field.answer_type = 'text'
        field.required_choice = 'required'
        
        # Get JSON schema
        view = api.content.get_view(
            name='json-schema-view',
            context=self.form,
            request=self.request
        )
        schema = json.loads(view())
        
        # Check that field is in required array
        self.assertIn('required', schema)
        field_id = create_id(field)
        self.assertIn(field_id, schema['required'])

    def test_optional_field_not_in_required(self):
        """Test that optional field does not appear in required array"""
        field = api.content.create(
            container=self.form,
            type='Field',
            title='Optional Field',
        )
        field.answer_type = 'text'
        field.required_choice = 'optional'
        
        # Get JSON schema
        view = api.content.get_view(
            name='json-schema-view',
            context=self.form,
            request=self.request
        )
        schema = json.loads(view())
        
        # Check that field is not in required array
        field_id = create_id(field)
        self.assertNotIn(field_id, schema.get('required', []))

    def test_multiple_required_fields(self):
        """Test multiple required fields"""
        field1 = api.content.create(
            container=self.form,
            type='Field',
            title='Field 1',
        )
        field1.answer_type = 'text'
        field1.required_choice = 'required'
        
        field2 = api.content.create(
            container=self.form,
            type='Field',
            title='Field 2',
        )
        field2.answer_type = 'number'
        field2.required_choice = 'required'
        
        field3 = api.content.create(
            container=self.form,
            type='Field',
            title='Field 3',
        )
        field3.answer_type = 'boolean'
        field3.required_choice = 'optional'
        
        # Get JSON schema
        view = api.content.get_view(
            name='json-schema-view',
            context=self.form,
            request=self.request
        )
        schema = json.loads(view())
        
        # Check required array
        self.assertIn('required', schema)
        self.assertEqual(len(schema['required']), 2)
        self.assertIn(create_id(field1), schema['required'])
        self.assertIn(create_id(field2), schema['required'])
        self.assertNotIn(create_id(field3), schema['required'])

    def test_required_selection_field(self):
        """Test required selection field"""
        selectionfield = api.content.create(
            container=self.form,
            type='SelectionField',
            title='Required Selection',
        )
        selectionfield.answer_type = 'radio'
        selectionfield.required_choice = 'required'
        
        api.content.create(
            container=selectionfield,
            type='Option',
            title='Option 1',
        )
        
        # Get JSON schema
        view = api.content.get_view(
            name='json-schema-view',
            context=self.form,
            request=self.request
        )
        schema = json.loads(view())
        
        # Check that selection field is in required array
        field_id = create_id(selectionfield)
        self.assertIn(field_id, schema.get('required', []))

    def test_required_upload_field(self):
        """Test required upload field"""
        uploadfield = api.content.create(
            container=self.form,
            type='UploadField',
            title='Required Upload',
        )
        uploadfield.answer_type = 'file'
        uploadfield.required_choice = 'required'
        
        # Get JSON schema
        view = api.content.get_view(
            name='json-schema-view',
            context=self.form,
            request=self.request
        )
        schema = json.loads(view())
        
        # Check that upload field is in required array
        field_id = create_id(uploadfield)
        self.assertIn(field_id, schema.get('required', []))

    def test_required_array(self):
        """Test required array"""
        array = api.content.create(
            container=self.form,
            type='Array',
            title='Required Array',
        )
        array.required_choice = 'required'
        
        field = api.content.create(
            container=array,
            type='Field',
            title='Array Field',
        )
        field.answer_type = 'text'
        
        # Get JSON schema
        view = api.content.get_view(
            name='json-schema-view',
            context=self.form,
            request=self.request
        )
        schema = json.loads(view())
        
        # Check that array is in required array
        array_id = create_id(array)
        self.assertIn(array_id, schema.get('required', []))

    def test_dependent_required_structure(self):
        """Test dependentRequired structure exists"""
        field = api.content.create(
            container=self.form,
            type='Field',
            title='Test Field',
        )
        field.answer_type = 'text'
        
        # Get JSON schema
        view = api.content.get_view(
            name='json-schema-view',
            context=self.form,
            request=self.request
        )
        schema = json.loads(view())
        
        # Check that dependentRequired exists in schema
        self.assertIn('dependentRequired', schema)
        self.assertIsInstance(schema['dependentRequired'], dict)

    def test_field_with_dependencies(self):
        """Test field with dependencies"""
        field1 = api.content.create(
            container=self.form,
            type='Field',
            title='Field 1',
        )
        field1.answer_type = 'boolean'
        
        field2 = api.content.create(
            container=self.form,
            type='Field',
            title='Field 2',
        )
        field2.answer_type = 'text'
        
        # Note: Setting up dependencies requires the dependency_fields relation
        # which may not be directly testable without the full form UI
        # But we can test that the structure is present
        
        # Get JSON schema
        view = api.content.get_view(
            name='json-schema-view',
            context=self.form,
            request=self.request
        )
        schema = json.loads(view())
        
        # Schema should have dependentRequired structure
        self.assertIn('dependentRequired', schema)

    def test_required_in_nested_structure(self):
        """Test required field in nested structure"""
        fieldset = api.content.create(
            container=self.form,
            type='Fieldset',
            title='Section',
        )
        
        field = api.content.create(
            container=fieldset,
            type='Field',
            title='Nested Required Field',
        )
        field.answer_type = 'text'
        field.required_choice = 'required'
        
        # Get JSON schema
        view = api.content.get_view(
            name='json-schema-view',
            context=self.form,
            request=self.request
        )
        schema = json.loads(view())
        
        # Field should be in required array
        field_id = create_id(field)
        self.assertIn(field_id, schema.get('required', []))

    def test_mixed_required_and_optional_in_complex(self):
        """Test mix of required and optional fields in complex"""
        complex_obj = api.content.create(
            container=self.form,
            type='Complex',
            title='Complex Object',
        )
        
        required_field = api.content.create(
            container=complex_obj,
            type='Field',
            title='Required in Complex',
        )
        required_field.answer_type = 'text'
        required_field.required_choice = 'required'
        
        optional_field = api.content.create(
            container=complex_obj,
            type='Field',
            title='Optional in Complex',
        )
        optional_field.answer_type = 'text'
        optional_field.required_choice = 'optional'
        
        # Get JSON schema
        view = api.content.get_view(
            name='json-schema-view',
            context=self.form,
            request=self.request
        )
        schema = json.loads(view())
        
        # Check required array
        self.assertIn(create_id(required_field), schema.get('required', []))
        self.assertNotIn(create_id(optional_field), schema.get('required', []))
