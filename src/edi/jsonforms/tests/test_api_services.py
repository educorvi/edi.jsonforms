# -*- coding: utf-8 -*-
"""Tests for API services."""
from edi.jsonforms.testing import EDI_JSONFORMS_FUNCTIONAL_TESTING
from edi.jsonforms.testing import EDI_JSONFORMS_INTEGRATION_TESTING
from plone import api
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from plone.restapi.testing import RelativeSession

import json
import unittest


class SchemataServiceIntegrationTest(unittest.TestCase):
    """Test Schemata expandable element."""

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
            id='test_form',
            title='Test Form'
        )

    def test_schemata_expandable_element_exists(self):
        """Test that Schemata expandable element can be retrieved."""
        from edi.jsonforms.api.services.schemata.get import Schemata
        
        schemata = Schemata(self.form, self.request)
        result = schemata(expand=False)
        
        self.assertIn('schemata', result)
        self.assertIn('@id', result['schemata'])

    def test_schemata_expandable_element_expanded(self):
        """Test that Schemata expandable element can be expanded."""
        from edi.jsonforms.api.services.schemata.get import Schemata
        
        schemata = Schemata(self.form, self.request)
        result = schemata(expand=True)
        
        self.assertIn('schemata', result)
        self.assertIn('items', result['schemata'])


class JsonSchemaServiceIntegrationTest(unittest.TestCase):
    """Test JsonSchemaGet REST API service."""

    layer = EDI_JSONFORMS_INTEGRATION_TESTING

    def setUp(self):
        """Custom shared utility setup for tests."""
        self.portal = self.layer['portal']
        self.request = self.layer['request']
        setRoles(self.portal, TEST_USER_ID, ['Manager'])
        
        # Create a test form with fields
        self.form = api.content.create(
            container=self.portal,
            type='Form',
            id='test_form',
            title='Test Form'
        )
        
        # Add a field to the form
        self.field = api.content.create(
            container=self.form,
            type='Field',
            id='test_field',
            title='Test Field'
        )

    def test_json_schema_service_returns_dict(self):
        """Test that JsonSchemaGet service returns a dictionary."""
        from edi.jsonforms.api.services.schemata.get import JsonSchemaGet
        
        service = JsonSchemaGet(self.form, self.request)
        result = service.reply()
        
        self.assertIsInstance(result, dict)

    def test_json_schema_service_has_required_properties(self):
        """Test that JsonSchemaGet service returns schema with required properties."""
        from edi.jsonforms.api.services.schemata.get import JsonSchemaGet
        
        service = JsonSchemaGet(self.form, self.request)
        result = service.reply()
        
        # Check for basic JSON Schema properties
        self.assertIn('type', result)
        self.assertIn('properties', result)


class UiSchemaServiceIntegrationTest(unittest.TestCase):
    """Test UiSchemaGet REST API service."""

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
            id='test_form',
            title='Test Form'
        )

    def test_ui_schema_service_returns_dict(self):
        """Test that UiSchemaGet service returns a dictionary."""
        from edi.jsonforms.api.services.schemata.get import UiSchemaGet
        
        service = UiSchemaGet(self.form, self.request)
        result = service.reply()
        
        self.assertIsInstance(result, dict)

    def test_ui_schema_service_has_type(self):
        """Test that UiSchemaGet service returns schema with type."""
        from edi.jsonforms.api.services.schemata.get import UiSchemaGet
        
        service = UiSchemaGet(self.form, self.request)
        result = service.reply()
        
        # UI schemas should have a type property
        self.assertIn('type', result)


class RestAPIFunctionalTest(unittest.TestCase):
    """Test REST API endpoints."""

    layer = EDI_JSONFORMS_FUNCTIONAL_TESTING

    def setUp(self):
        """Custom shared utility setup for tests."""
        self.portal = self.layer['portal']
        self.request = self.layer['request']
        setRoles(self.portal, TEST_USER_ID, ['Manager'])
        
        # Create a test form
        self.form = api.content.create(
            container=self.portal,
            type='Form',
            id='test_form',
            title='Test Form'
        )
        
        # Setup API session
        self.api_session = RelativeSession(self.portal.absolute_url())
        self.api_session.headers.update({'Accept': 'application/json'})
        self.api_session.auth = (TEST_USER_ID, 'secret')

    def test_json_schema_endpoint_accessible(self):
        """Test that /@json-schema endpoint is accessible."""
        response = self.api_session.get(
            '/test_form/@json-schema'
        )
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIsInstance(data, dict)

    def test_ui_schema_endpoint_accessible(self):
        """Test that /@ui-schema endpoint is accessible."""
        response = self.api_session.get(
            '/test_form/@ui-schema'
        )
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIsInstance(data, dict)
