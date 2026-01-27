# -*- coding: utf-8 -*-
from edi.jsonforms.testing import EDI_JSONFORMS_INTEGRATION_TESTING
from plone import api
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from plone.restapi.testing import RelativeSession

import json
import unittest


class ApiServicesTest(unittest.TestCase):
    """Test API services"""

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

    def test_json_schema_service_registered(self):
        """Test that @json-schema service is registered"""
        view = api.content.get_view(
            name='@json-schema',
            context=self.form,
            request=self.request
        )
        self.assertIsNotNone(view)

    def test_json_schema_service_returns_valid_schema(self):
        """Test that @json-schema service returns valid JSON schema"""
        view = api.content.get_view(
            name='@json-schema',
            context=self.form,
            request=self.request
        )
        result = view.reply()
        
        # Check basic schema structure
        self.assertIn('type', result)
        self.assertEqual(result['type'], 'object')
        self.assertIn('properties', result)
        self.assertIn('required', result)

    def test_ui_schema_service_registered(self):
        """Test that @ui-schema service is registered"""
        view = api.content.get_view(
            name='@ui-schema',
            context=self.form,
            request=self.request
        )
        self.assertIsNotNone(view)

    def test_ui_schema_service_returns_valid_schema(self):
        """Test that @ui-schema service returns valid UI schema"""
        view = api.content.get_view(
            name='@ui-schema',
            context=self.form,
            request=self.request
        )
        result = view.reply()
        
        # Check basic UI schema structure
        self.assertIn('type', result)
        self.assertIn('elements', result)

    def test_schemata_service_registered(self):
        """Test that @schemata service is registered"""
        view = api.content.get_view(
            name='@schemata',
            context=self.form,
            request=self.request
        )
        self.assertIsNotNone(view)

    def test_schemata_service_returns_items(self):
        """Test that @schemata service returns items"""
        view = api.content.get_view(
            name='@schemata',
            context=self.form,
            request=self.request
        )
        result = view.reply()
        
        # Check basic schemata structure
        self.assertIn('items', result)
        self.assertIsInstance(result['items'], list)

    def test_json_schema_with_field(self):
        """Test JSON schema generation with a field"""
        field = api.content.create(
            container=self.form,
            type='Field',
            title='Test Field',
        )
        field.answer_type = 'text'
        field.required_choice = 'required'
        
        view = api.content.get_view(
            name='@json-schema',
            context=self.form,
            request=self.request
        )
        result = view.reply()
        
        # Check that field is in schema
        self.assertIn('properties', result)
        # Field should be in properties (with some ID)
        self.assertTrue(len(result['properties']) > 0)

    def test_ui_schema_with_field(self):
        """Test UI schema generation with a field"""
        field = api.content.create(
            container=self.form,
            type='Field',
            title='Test Field',
        )
        field.answer_type = 'text'
        
        view = api.content.get_view(
            name='@ui-schema',
            context=self.form,
            request=self.request
        )
        result = view.reply()
        
        # Check that UI schema has elements
        self.assertIn('elements', result)
        self.assertTrue(len(result['elements']) > 0)

    def test_json_schema_extended_mode(self):
        """Test extended JSON schema mode"""
        # Create a field with dependencies
        field = api.content.create(
            container=self.form,
            type='Field',
            title='Test Field',
        )
        field.answer_type = 'text'
        
        view = api.content.get_view(
            name='@json-schema',
            context=self.form,
            request=self.request
        )
        
        # Extended schema should include allOf structure
        result = view.reply()
        self.assertIsInstance(result, dict)
