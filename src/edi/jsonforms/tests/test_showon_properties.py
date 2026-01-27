# -*- coding: utf-8 -*-
from edi.jsonforms.testing import EDI_JSONFORMS_INTEGRATION_TESTING
from edi.jsonforms.views.showOn_properties import (
    find_scope,
    transform_scope_to_object_writing_form,
)
from edi.jsonforms.views.common import create_id
from plone import api
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID

import unittest


class ShowOnPropertiesTest(unittest.TestCase):
    """Test showOn properties functionality"""

    layer = EDI_JSONFORMS_INTEGRATION_TESTING

    def setUp(self):
        """Custom shared utility setup for tests."""
        self.portal = self.layer['portal']
        setRoles(self.portal, TEST_USER_ID, ['Manager'])
        
        # Create a form for testing
        self.form = api.content.create(
            container=self.portal,
            type='Form',
            id='test-form',
            title='Test Form',
        )

    def test_find_scope_for_field(self):
        """Test find_scope for a simple field"""
        field = api.content.create(
            container=self.form,
            type='Field',
            title='Test Field',
        )
        field.answer_type = 'text'
        
        lookup_scopes = {}
        scope = find_scope(lookup_scopes, field)
        
        # Should return a scope dictionary
        self.assertIsInstance(scope, (dict, str))

    def test_find_scope_for_option(self):
        """Test find_scope for an option"""
        selectionfield = api.content.create(
            container=self.form,
            type='SelectionField',
            title='Test Selection',
        )
        selectionfield.answer_type = 'radio'
        
        option = api.content.create(
            container=selectionfield,
            type='Option',
            title='Test Option',
        )
        
        lookup_scopes = {}
        scope = find_scope(lookup_scopes, option)
        
        # Should return a scope for the option's parent
        self.assertIsInstance(scope, (dict, str))

    def test_find_scope_caches_result(self):
        """Test that find_scope caches the result"""
        field = api.content.create(
            container=self.form,
            type='Field',
            title='Test Field',
        )
        field.answer_type = 'text'
        
        lookup_scopes = {}
        scope1 = find_scope(lookup_scopes, field)
        
        # Second call should use cache
        scope2 = find_scope(lookup_scopes, field)
        
        self.assertEqual(scope1, scope2)
        # Cache should have entry
        field_id = create_id(field)
        self.assertIn(field_id, lookup_scopes)

    def test_find_scope_for_nested_field(self):
        """Test find_scope for a nested field in complex"""
        complex_field = api.content.create(
            container=self.form,
            type='Complex',
            title='Test Complex',
        )
        
        field = api.content.create(
            container=complex_field,
            type='Field',
            title='Nested Field',
        )
        field.answer_type = 'text'
        
        lookup_scopes = {}
        scope = find_scope(lookup_scopes, field)
        
        # Should return a scope with complex in path
        if isinstance(scope, str):
            self.assertIn('properties', scope)

    def test_find_scope_for_array_field(self):
        """Test find_scope for a field in array"""
        array = api.content.create(
            container=self.form,
            type='Array',
            title='Test Array',
        )
        
        field = api.content.create(
            container=array,
            type='Field',
            title='Array Field',
        )
        field.answer_type = 'text'
        
        lookup_scopes = {}
        scope = find_scope(lookup_scopes, field)
        
        # Should return a scope with items in path for arrays
        if isinstance(scope, str):
            self.assertIn('items', scope) or self.assertIn('properties', scope)

    def test_transform_scope_to_object_writing_form(self):
        """Test transform_scope_to_object_writing_form"""
        scope = '/properties/field1/properties/field2'
        result = transform_scope_to_object_writing_form(scope)
        
        # Should transform properties/ to dots
        self.assertIsInstance(result, str)
        self.assertNotIn('properties/', result)

    def test_transform_scope_handles_items(self):
        """Test transform_scope_to_object_writing_form with items"""
        scope = '/properties/array1/items/properties/field1'
        result = transform_scope_to_object_writing_form(scope)
        
        # Should handle items correctly
        self.assertIsInstance(result, str)

    def test_transform_scope_empty(self):
        """Test transform_scope_to_object_writing_form with empty scope"""
        scope = ''
        result = transform_scope_to_object_writing_form(scope)
        
        self.assertEqual(result, '')

    def test_find_scope_returns_empty_for_non_field(self):
        """Test find_scope returns empty dict for non-field/non-option types"""
        fieldset = api.content.create(
            container=self.form,
            type='Fieldset',
            title='Test Fieldset',
        )
        
        lookup_scopes = {}
        scope = find_scope(lookup_scopes, fieldset)
        
        # Should return empty dict for Fieldset
        self.assertEqual(scope, {})

    def test_find_scope_for_deeply_nested_structure(self):
        """Test find_scope for deeply nested structure"""
        fieldset = api.content.create(
            container=self.form,
            type='Fieldset',
            title='Test Fieldset',
        )
        
        complex_field = api.content.create(
            container=fieldset,
            type='Complex',
            title='Test Complex',
        )
        
        field = api.content.create(
            container=complex_field,
            type='Field',
            title='Deeply Nested Field',
        )
        field.answer_type = 'text'
        
        lookup_scopes = {}
        scope = find_scope(lookup_scopes, field)
        
        # Should return a valid scope
        self.assertIsInstance(scope, (dict, str))
