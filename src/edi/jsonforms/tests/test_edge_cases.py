# -*- coding: utf-8 -*-
from edi.jsonforms.testing import EDI_JSONFORMS_INTEGRATION_TESTING
from plone import api
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID

import json
import unittest

# Test constants
MAX_TITLE_LENGTH = 1000
PERFORMANCE_TEST_FIELD_COUNT = 50
MAX_NESTING_DEPTH = 5


class EdgeCasesTest(unittest.TestCase):
    """Test edge cases and boundary conditions"""

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

    def test_empty_form_json_schema(self):
        """Test JSON schema for empty form"""
        view = api.content.get_view(
            name='json-schema-view',
            context=self.form,
            request=self.request
        )
        schema = json.loads(view())
        
        # Empty form should have basic structure
        self.assertEqual(schema['type'], 'object')
        self.assertEqual(schema['properties'], {})
        self.assertEqual(schema['required'], [])

    def test_empty_form_ui_schema(self):
        """Test UI schema for empty form"""
        view = api.content.get_view(
            name='ui-schema-view',
            context=self.form,
            request=self.request
        )
        schema = json.loads(view())
        
        # Empty form should have basic structure
        self.assertIn('type', schema)
        self.assertIn('elements', schema)

    def test_field_with_empty_title(self):
        """Test field with empty title"""
        field = api.content.create(
            container=self.form,
            type='Field',
            title='',
        )
        field.answer_type = 'text'
        
        view = api.content.get_view(
            name='json-schema-view',
            context=self.form,
            request=self.request
        )
        schema = json.loads(view())
        
        # Should still generate schema
        self.assertIn('properties', schema)

    def test_field_with_very_long_title(self):
        """Test field with very long title"""
        long_title = 'A' * MAX_TITLE_LENGTH
        field = api.content.create(
            container=self.form,
            type='Field',
            title=long_title,
        )
        field.answer_type = 'text'
        
        view = api.content.get_view(
            name='json-schema-view',
            context=self.form,
            request=self.request
        )
        schema = json.loads(view())
        
        # Should still generate schema
        self.assertIn('properties', schema)

    def test_field_with_special_characters_in_title(self):
        """Test field with special characters in title"""
        field = api.content.create(
            container=self.form,
            type='Field',
            title='Test & Field <script>alert("xss")</script>',
        )
        field.answer_type = 'text'
        
        view = api.content.get_view(
            name='json-schema-view',
            context=self.form,
            request=self.request
        )
        schema = json.loads(view())
        
        # Should still generate schema
        self.assertIn('properties', schema)

    def test_field_with_unicode_characters(self):
        """Test field with unicode characters"""
        field = api.content.create(
            container=self.form,
            type='Field',
            title='Tëst Fiëld 你好 مرحبا',
        )
        field.answer_type = 'text'
        
        view = api.content.get_view(
            name='json-schema-view',
            context=self.form,
            request=self.request
        )
        schema = json.loads(view())
        
        # Should still generate schema
        self.assertIn('properties', schema)

    def test_selection_field_with_no_options(self):
        """Test selection field with no options"""
        selectionfield = api.content.create(
            container=self.form,
            type='SelectionField',
            title='Empty Selection',
        )
        selectionfield.answer_type = 'radio'
        
        view = api.content.get_view(
            name='json-schema-view',
            context=self.form,
            request=self.request
        )
        schema = json.loads(view())
        
        # Should generate schema with empty enum
        self.assertIn('properties', schema)

    def test_field_with_minimum_equal_to_maximum(self):
        """Test field with minimum equal to maximum"""
        field = api.content.create(
            container=self.form,
            type='Field',
            title='Test Field',
        )
        field.answer_type = 'number'
        field.minimum = 5
        field.maximum = 5
        
        view = api.content.get_view(
            name='json-schema-view',
            context=self.form,
            request=self.request
        )
        schema = json.loads(view())
        
        # Should have both minimum and maximum set to 5
        from edi.jsonforms.views.common import create_id
        field_id = create_id(field)
        self.assertEqual(schema['properties'][field_id]['minimum'], 5)
        self.assertEqual(schema['properties'][field_id]['maximum'], 5)

    def test_field_with_minimum_greater_than_maximum(self):
        """Test field with minimum greater than maximum (edge case)"""
        field = api.content.create(
            container=self.form,
            type='Field',
            title='Test Field',
        )
        field.answer_type = 'number'
        field.minimum = 10
        field.maximum = 5
        
        view = api.content.get_view(
            name='json-schema-view',
            context=self.form,
            request=self.request
        )
        schema = json.loads(view())
        
        # Should still generate schema (validation may happen elsewhere)
        from edi.jsonforms.views.common import create_id
        field_id = create_id(field)
        self.assertIn(field_id, schema['properties'])

    def test_nested_empty_structures(self):
        """Test nested empty structures"""
        fieldset = api.content.create(
            container=self.form,
            type='Fieldset',
            title='Empty Fieldset',
        )
        
        complex_obj = api.content.create(
            container=fieldset,
            type='Complex',
            title='Empty Complex',
        )
        
        view = api.content.get_view(
            name='json-schema-view',
            context=self.form,
            request=self.request
        )
        schema = json.loads(view())
        
        # Should generate schema even for empty nested structures
        self.assertIn('properties', schema)

    def test_array_with_no_items(self):
        """Test array with no items"""
        array = api.content.create(
            container=self.form,
            type='Array',
            title='Empty Array',
        )
        
        view = api.content.get_view(
            name='json-schema-view',
            context=self.form,
            request=self.request
        )
        schema = json.loads(view())
        
        # Should generate schema for empty array
        self.assertIn('properties', schema)

    def test_many_fields_performance(self):
        """Test form with many fields (50+)"""
        # Create multiple fields to test performance
        for i in range(PERFORMANCE_TEST_FIELD_COUNT):
            field = api.content.create(
                container=self.form,
                type='Field',
                title=f'Field {i}',
            )
            field.answer_type = 'text'
        
        # Should be able to generate schema
        view = api.content.get_view(
            name='json-schema-view',
            context=self.form,
            request=self.request
        )
        schema = json.loads(view())
        
        # Should have all fields
        self.assertEqual(len(schema['properties']), PERFORMANCE_TEST_FIELD_COUNT)

    def test_deeply_nested_structure_limit(self):
        """Test very deeply nested structure"""
        # Create deeply nested structure
        parent = self.form
        for i in range(MAX_NESTING_DEPTH):
            if i % 2 == 0:
                parent = api.content.create(
                    container=parent,
                    type='Complex',
                    title=f'Level {i}',
                )
            else:
                parent = api.content.create(
                    container=parent,
                    type='Fieldset',
                    title=f'Level {i}',
                )
        
        # Add a field at the deepest level
        field = api.content.create(
            container=parent,
            type='Field',
            title='Deep Field',
        )
        field.answer_type = 'text'
        
        # Should still generate schema
        view = api.content.get_view(
            name='json-schema-view',
            context=self.form,
            request=self.request
        )
        schema = json.loads(view())
        
        # Should have properties
        self.assertIn('properties', schema)

    def test_option_with_empty_title(self):
        """Test option with empty title"""
        selectionfield = api.content.create(
            container=self.form,
            type='SelectionField',
            title='Selection',
        )
        selectionfield.answer_type = 'radio'
        
        option = api.content.create(
            container=selectionfield,
            type='Option',
            title='',
        )
        
        view = api.content.get_view(
            name='json-schema-view',
            context=self.form,
            request=self.request
        )
        schema = json.loads(view())
        
        # Should still generate schema with empty option
        self.assertIn('properties', schema)

    def test_form_with_only_helptext(self):
        """Test form with only helptext (no actual fields)"""
        helptext = api.content.create(
            container=self.form,
            type='Helptext',
            title='Help',
        )
        
        view = api.content.get_view(
            name='json-schema-view',
            context=self.form,
            request=self.request
        )
        schema = json.loads(view())
        
        # Should generate basic schema (helptext doesn't add to schema)
        self.assertEqual(schema['properties'], {})
