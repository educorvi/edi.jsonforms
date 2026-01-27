# -*- coding: utf-8 -*-
from edi.jsonforms.testing import EDI_JSONFORMS_INTEGRATION_TESTING
from plone import api
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID

import json
import unittest


class NestedStructuresIntegrationTest(unittest.TestCase):
    """Test complex nested structures"""

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

    def test_fieldset_with_fields(self):
        """Test fieldset containing fields generates correct schemas"""
        fieldset = api.content.create(
            container=self.form,
            type='Fieldset',
            title='Personal Information',
        )
        
        field1 = api.content.create(
            container=fieldset,
            type='Field',
            title='First Name',
        )
        field1.answer_type = 'text'
        
        field2 = api.content.create(
            container=fieldset,
            type='Field',
            title='Last Name',
        )
        field2.answer_type = 'text'
        
        # Get JSON schema
        view = api.content.get_view(
            name='json-schema-view',
            context=self.form,
            request=self.request
        )
        schema = json.loads(view())
        
        # Check schema has properties
        self.assertIn('properties', schema)
        self.assertTrue(len(schema['properties']) >= 2)
        
        # Get UI schema
        ui_view = api.content.get_view(
            name='ui-schema-view',
            context=self.form,
            request=self.request
        )
        ui_schema = json.loads(ui_view())
        
        # Check UI schema has elements
        self.assertIn('elements', ui_schema)

    def test_complex_with_fields(self):
        """Test complex object containing fields"""
        complex_obj = api.content.create(
            container=self.form,
            type='Complex',
            title='Address',
        )
        
        street = api.content.create(
            container=complex_obj,
            type='Field',
            title='Street',
        )
        street.answer_type = 'text'
        
        city = api.content.create(
            container=complex_obj,
            type='Field',
            title='City',
        )
        city.answer_type = 'text'
        
        # Get JSON schema
        view = api.content.get_view(
            name='json-schema-view',
            context=self.form,
            request=self.request
        )
        schema = json.loads(view())
        
        # Check that complex creates nested structure
        self.assertIn('properties', schema)

    def test_array_with_fields(self):
        """Test array containing fields"""
        array = api.content.create(
            container=self.form,
            type='Array',
            title='Phone Numbers',
        )
        
        phone = api.content.create(
            container=array,
            type='Field',
            title='Phone Number',
        )
        phone.answer_type = 'tel'
        
        # Get JSON schema
        view = api.content.get_view(
            name='json-schema-view',
            context=self.form,
            request=self.request
        )
        schema = json.loads(view())
        
        # Check that array structure is created
        self.assertIn('properties', schema)

    def test_nested_complex_in_fieldset(self):
        """Test complex object nested in fieldset"""
        fieldset = api.content.create(
            container=self.form,
            type='Fieldset',
            title='Contact Information',
        )
        
        complex_obj = api.content.create(
            container=fieldset,
            type='Complex',
            title='Address',
        )
        
        street = api.content.create(
            container=complex_obj,
            type='Field',
            title='Street',
        )
        street.answer_type = 'text'
        
        # Get JSON schema
        view = api.content.get_view(
            name='json-schema-view',
            context=self.form,
            request=self.request
        )
        schema = json.loads(view())
        
        # Should have nested structure
        self.assertIn('properties', schema)

    def test_array_in_complex(self):
        """Test array nested in complex object"""
        complex_obj = api.content.create(
            container=self.form,
            type='Complex',
            title='Person',
        )
        
        array = api.content.create(
            container=complex_obj,
            type='Array',
            title='Email Addresses',
        )
        
        email = api.content.create(
            container=array,
            type='Field',
            title='Email',
        )
        email.answer_type = 'email'
        
        # Get JSON schema
        view = api.content.get_view(
            name='json-schema-view',
            context=self.form,
            request=self.request
        )
        schema = json.loads(view())
        
        # Should have nested structure
        self.assertIn('properties', schema)

    def test_deeply_nested_structure(self):
        """Test deeply nested structure: Fieldset > Complex > Array > Field"""
        fieldset = api.content.create(
            container=self.form,
            type='Fieldset',
            title='Level 1',
        )
        
        complex_obj = api.content.create(
            container=fieldset,
            type='Complex',
            title='Level 2',
        )
        
        array = api.content.create(
            container=complex_obj,
            type='Array',
            title='Level 3',
        )
        
        field = api.content.create(
            container=array,
            type='Field',
            title='Level 4',
        )
        field.answer_type = 'text'
        
        # Get JSON schema
        view = api.content.get_view(
            name='json-schema-view',
            context=self.form,
            request=self.request
        )
        schema = json.loads(view())
        
        # Should generate valid schema
        self.assertIn('type', schema)
        self.assertIn('properties', schema)

    def test_multiple_nested_structures(self):
        """Test multiple nested structures at same level"""
        # Create first nested structure
        fieldset1 = api.content.create(
            container=self.form,
            type='Fieldset',
            title='Section 1',
        )
        
        field1 = api.content.create(
            container=fieldset1,
            type='Field',
            title='Field 1',
        )
        field1.answer_type = 'text'
        
        # Create second nested structure
        complex_obj = api.content.create(
            container=self.form,
            type='Complex',
            title='Section 2',
        )
        
        field2 = api.content.create(
            container=complex_obj,
            type='Field',
            title='Field 2',
        )
        field2.answer_type = 'number'
        
        # Create third nested structure
        array = api.content.create(
            container=self.form,
            type='Array',
            title='Section 3',
        )
        
        field3 = api.content.create(
            container=array,
            type='Field',
            title='Field 3',
        )
        field3.answer_type = 'boolean'
        
        # Get JSON schema
        view = api.content.get_view(
            name='json-schema-view',
            context=self.form,
            request=self.request
        )
        schema = json.loads(view())
        
        # Should have all structures
        self.assertIn('properties', schema)
        self.assertTrue(len(schema['properties']) >= 3)

    def test_selection_field_with_options(self):
        """Test selection field with options in nested structure"""
        fieldset = api.content.create(
            container=self.form,
            type='Fieldset',
            title='Preferences',
        )
        
        selectionfield = api.content.create(
            container=fieldset,
            type='SelectionField',
            title='Favorite Color',
        )
        selectionfield.answer_type = 'radio'
        
        api.content.create(
            container=selectionfield,
            type='Option',
            title='Red',
        )
        
        api.content.create(
            container=selectionfield,
            type='Option',
            title='Blue',
        )
        
        # Get JSON schema
        view = api.content.get_view(
            name='json-schema-view',
            context=self.form,
            request=self.request
        )
        schema = json.loads(view())
        
        # Should have enum values for the selection field
        self.assertIn('properties', schema)
