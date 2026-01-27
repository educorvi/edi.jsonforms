# -*- coding: utf-8 -*-
from edi.jsonforms.testing import EDI_JSONFORMS_INTEGRATION_TESTING
from edi.jsonforms.handlers.schema_handler import schema_handler
from plone import api
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from zope.lifecycleevent import ObjectModifiedEvent

import unittest


class SchemaHandlerTest(unittest.TestCase):
    """Test schema handler"""

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

    def test_schema_handler_without_change_note(self):
        """Test schema handler without change note"""
        # Create a modified event
        event = ObjectModifiedEvent(self.form)
        
        # Call handler - should not raise an error
        schema_handler(self.form, event)
        
        # Check that revision attributes are not set without change note
        self.assertFalse(hasattr(self.form, 'json_schema_rev'))
        self.assertFalse(hasattr(self.form, 'ui_schema_rev'))

    def test_schema_handler_with_change_note(self):
        """Test schema handler with change note"""
        # Set up REQUEST with change note
        from zope.globalrequest import setRequest
        from ZPublisher.HTTPRequest import HTTPRequest
        from ZPublisher.HTTPResponse import HTTPResponse
        
        # Create a proper request with change note
        environ = {'SERVER_NAME': 'test', 'SERVER_PORT': '80'}
        response = HTTPResponse()
        request = HTTPRequest(None, environ, response)
        request.form['cmfeditions_version_comment'] = 'Test change note'
        
        # Set the request
        self.form.REQUEST = request
        setRequest(request)
        
        # Create a modified event
        event = ObjectModifiedEvent(self.form)
        
        # Call handler
        schema_handler(self.form, event)
        
        # Check that revision attributes are set
        self.assertTrue(hasattr(self.form, 'json_schema_rev'))
        self.assertTrue(hasattr(self.form, 'ui_schema_rev'))
        
        # Check that schemas are stored as strings
        self.assertIsInstance(self.form.json_schema_rev, str)
        self.assertIsInstance(self.form.ui_schema_rev, str)

    def test_schema_handler_preserves_schema_content(self):
        """Test that schema handler preserves schema content"""
        # Add a field to the form
        field = api.content.create(
            container=self.form,
            type='Field',
            title='Test Field',
        )
        field.answer_type = 'text'
        
        # Set up REQUEST with change note
        from zope.globalrequest import setRequest
        from ZPublisher.HTTPRequest import HTTPRequest
        from ZPublisher.HTTPResponse import HTTPResponse
        
        environ = {'SERVER_NAME': 'test', 'SERVER_PORT': '80'}
        response = HTTPResponse()
        request = HTTPRequest(None, environ, response)
        request.form['cmfeditions_version_comment'] = 'Added field'
        
        self.form.REQUEST = request
        setRequest(request)
        
        # Create a modified event
        event = ObjectModifiedEvent(self.form)
        
        # Call handler
        schema_handler(self.form, event)
        
        # Check that schemas contain field information
        import json
        json_schema = json.loads(self.form.json_schema_rev)
        
        # Should have properties
        self.assertIn('properties', json_schema)
        self.assertTrue(len(json_schema['properties']) > 0)
