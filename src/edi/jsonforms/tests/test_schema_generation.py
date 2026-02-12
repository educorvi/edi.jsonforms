# -*- coding: utf-8 -*-
"""Tests for schema generation with various field types."""
from edi.jsonforms.testing import EDI_JSONFORMS_INTEGRATION_TESTING
from plone import api
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID

import json
import unittest


class FieldTypeSchemaTest(unittest.TestCase):
    """Test schema generation for different field types."""

    layer = EDI_JSONFORMS_INTEGRATION_TESTING

    def setUp(self):
        """Custom shared utility setup for tests."""
        self.portal = self.layer['portal']
        self.request = self.layer['request']
        setRoles(self.portal, TEST_USER_ID, ['Manager'])
        
        # Create a test form
        self.form = api.content.create(
            container=self.portal,
            type='Form',
            id='schema_test_form',
            title='Schema Test Form'
        )

    def test_text_field_schema(self):
        """Test that text field generates correct schema."""
        field = api.content.create(
            container=self.form,
            type='Field',
            id='text_field',
            title='Text Field'
        )
        field.answer_type = 'text'
        
        view = api.content.get_view(
            name='json-schema-view',
            context=self.form,
            request=self.request
        )
        
        schema = view.get_schema()
        
        # Check that the field is in the schema
        self.assertIn('text_field', schema['properties'])
        # Check that it has string type
        self.assertEqual(schema['properties']['text_field']['type'], 'string')

    def test_email_field_schema(self):
        """Test that email field generates correct schema with format."""
        field = api.content.create(
            container=self.form,
            type='Field',
            id='email_field',
            title='Email Field'
        )
        field.answer_type = 'email'
        
        view = api.content.get_view(
            name='json-schema-view',
            context=self.form,
            request=self.request
        )
        
        schema = view.get_schema()
        
        # Check that the field has email format
        self.assertIn('email_field', schema['properties'])
        self.assertEqual(schema['properties']['email_field']['type'], 'string')
        self.assertEqual(schema['properties']['email_field'].get('format'), 'email')

    def test_url_field_schema(self):
        """Test that URL field generates correct schema with format."""
        field = api.content.create(
            container=self.form,
            type='Field',
            id='url_field',
            title='URL Field'
        )
        field.answer_type = 'url'
        
        view = api.content.get_view(
            name='json-schema-view',
            context=self.form,
            request=self.request
        )
        
        schema = view.get_schema()
        
        # Check that the field has hostname format
        self.assertIn('url_field', schema['properties'])
        self.assertEqual(schema['properties']['url_field']['type'], 'string')
        self.assertIn('format', schema['properties']['url_field'])

    def test_date_field_schema(self):
        """Test that date field generates correct schema with format."""
        field = api.content.create(
            container=self.form,
            type='Field',
            id='date_field',
            title='Date Field'
        )
        field.answer_type = 'date'
        
        view = api.content.get_view(
            name='json-schema-view',
            context=self.form,
            request=self.request
        )
        
        schema = view.get_schema()
        
        # Check that the field has date format
        self.assertIn('date_field', schema['properties'])
        self.assertEqual(schema['properties']['date_field']['type'], 'string')
        self.assertEqual(schema['properties']['date_field'].get('format'), 'date')

    def test_number_field_schema(self):
        """Test that number field generates correct schema."""
        field = api.content.create(
            container=self.form,
            type='Field',
            id='number_field',
            title='Number Field'
        )
        field.answer_type = 'number'
        field.minimum = 0
        field.maximum = 100
        
        view = api.content.get_view(
            name='json-schema-view',
            context=self.form,
            request=self.request
        )
        
        schema = view.get_schema()
        
        # Check that the field has number type with min/max
        self.assertIn('number_field', schema['properties'])
        field_schema = schema['properties']['number_field']
        self.assertIn(field_schema['type'], ['number', 'integer'])

    def test_required_field_in_schema(self):
        """Test that required fields appear in schema required array."""
        field = api.content.create(
            container=self.form,
            type='Field',
            id='required_field',
            title='Required Field'
        )
        field.required_choice = 'required'
        
        view = api.content.get_view(
            name='json-schema-view',
            context=self.form,
            request=self.request
        )
        
        schema = view.get_schema()
        
        # Check that the field is marked as required
        if 'required' in schema:
            self.assertIn('required_field', schema.get('required', []))

    def test_optional_field_not_required_in_schema(self):
        """Test that optional fields don't appear in required array."""
        field = api.content.create(
            container=self.form,
            type='Field',
            id='optional_field',
            title='Optional Field'
        )
        field.required_choice = 'optional'
        
        view = api.content.get_view(
            name='json-schema-view',
            context=self.form,
            request=self.request
        )
        
        schema = view.get_schema()
        
        # Check that the field is not in required array
        required = schema.get('required', [])
        self.assertNotIn('optional_field', required)

    def test_field_with_min_max_length(self):
        """Test that field with min/max length generates correct constraints."""
        field = api.content.create(
            container=self.form,
            type='Field',
            id='length_field',
            title='Length Constrained Field'
        )
        field.answer_type = 'text'
        field.minimum = 5
        field.maximum = 50
        
        view = api.content.get_view(
            name='json-schema-view',
            context=self.form,
            request=self.request
        )
        
        schema = view.get_schema()
        
        # Check that the field has length constraints
        self.assertIn('length_field', schema['properties'])
        field_schema = schema['properties']['length_field']
        # minLength and maxLength should be set
        if 'minLength' in field_schema:
            self.assertEqual(field_schema['minLength'], 5)
        if 'maxLength' in field_schema:
            self.assertEqual(field_schema['maxLength'], 50)


class SelectionFieldSchemaTest(unittest.TestCase):
    """Test schema generation for selection fields."""

    layer = EDI_JSONFORMS_INTEGRATION_TESTING

    def setUp(self):
        """Custom shared utility setup for tests."""
        self.portal = self.layer['portal']
        self.request = self.layer['request']
        setRoles(self.portal, TEST_USER_ID, ['Manager'])
        
        # Create a test form
        self.form = api.content.create(
            container=self.portal,
            type='Form',
            id='selection_test_form',
            title='Selection Test Form'
        )

    def test_selection_field_with_options(self):
        """Test that selection field generates correct enum schema."""
        selection = api.content.create(
            container=self.form,
            type='SelectionField',
            id='selection',
            title='Selection Field'
        )
        
        # Create option list
        option_list = api.content.create(
            container=selection,
            type='OptionList',
            id='options',
            title='Options'
        )
        option_list.options = ['option1', 'option2', 'option3']
        
        view = api.content.get_view(
            name='json-schema-view',
            context=self.form,
            request=self.request
        )
        
        schema = view.get_schema()
        
        # Check that selection field has enum
        self.assertIn('selection', schema['properties'])
        # Selection fields should have enum or oneOf
        field_schema = schema['properties']['selection']
        self.assertTrue('enum' in field_schema or 'oneOf' in field_schema)

    def test_selection_field_with_id_value_pairs(self):
        """Test that selection field handles id:value pairs correctly."""
        selection = api.content.create(
            container=self.form,
            type='SelectionField',
            id='selection_with_ids',
            title='Selection with IDs'
        )
        
        # Create option list with id:value pairs
        option_list = api.content.create(
            container=selection,
            type='OptionList',
            id='options',
            title='Options'
        )
        option_list.options = ['id1:Value 1', 'id2:Value 2', 'id3:Value 3']
        
        view = api.content.get_view(
            name='json-schema-view',
            context=self.form,
            request=self.request
        )
        
        schema = view.get_schema()
        
        # Check that selection field is in schema
        self.assertIn('selection_with_ids', schema['properties'])


class ComplexObjectSchemaTest(unittest.TestCase):
    """Test schema generation for complex objects."""

    layer = EDI_JSONFORMS_INTEGRATION_TESTING

    def setUp(self):
        """Custom shared utility setup for tests."""
        self.portal = self.layer['portal']
        self.request = self.layer['request']
        setRoles(self.portal, TEST_USER_ID, ['Manager'])
        
        # Create a test form
        self.form = api.content.create(
            container=self.portal,
            type='Form',
            id='complex_test_form',
            title='Complex Test Form'
        )

    def test_complex_object_schema(self):
        """Test that complex object generates nested properties."""
        complex_obj = api.content.create(
            container=self.form,
            type='Complex',
            id='complex',
            title='Complex Object'
        )
        
        # Add fields to complex object
        field1 = api.content.create(
            container=complex_obj,
            type='Field',
            id='nested1',
            title='Nested Field 1'
        )
        
        field2 = api.content.create(
            container=complex_obj,
            type='Field',
            id='nested2',
            title='Nested Field 2'
        )
        
        view = api.content.get_view(
            name='json-schema-view',
            context=self.form,
            request=self.request
        )
        
        schema = view.get_schema()
        
        # Check that complex object is in schema
        self.assertIn('complex', schema['properties'])
        complex_schema = schema['properties']['complex']
        
        # Complex object should have type 'object' and properties
        self.assertEqual(complex_schema.get('type'), 'object')
        self.assertIn('properties', complex_schema)
        
        # Nested fields should be in complex object properties
        self.assertIn('nested1', complex_schema['properties'])
        self.assertIn('nested2', complex_schema['properties'])

    def test_array_schema(self):
        """Test that array generates correct schema."""
        array = api.content.create(
            container=self.form,
            type='Array',
            id='array',
            title='Array'
        )
        
        # Add a field to the array
        field = api.content.create(
            container=array,
            type='Field',
            id='item',
            title='Array Item'
        )
        
        view = api.content.get_view(
            name='json-schema-view',
            context=self.form,
            request=self.request
        )
        
        schema = view.get_schema()
        
        # Check that array is in schema
        self.assertIn('array', schema['properties'])
        array_schema = schema['properties']['array']
        
        # Array should have type 'array' and items
        self.assertEqual(array_schema.get('type'), 'array')
        self.assertIn('items', array_schema)
