# -*- coding: utf-8 -*-
"""Tests for handlers module."""
from edi.jsonforms.handlers.schema_handler import schema_handler
from edi.jsonforms.testing import EDI_JSONFORMS_INTEGRATION_TESTING
from plone import api
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from unittest.mock import Mock, patch
from zope.lifecycleevent import ObjectModifiedEvent

import unittest


class SchemaHandlerTest(unittest.TestCase):
    """Test schema_handler event handler."""

    layer = EDI_JSONFORMS_INTEGRATION_TESTING

    def setUp(self):
        """Custom shared utility setup for tests."""
        self.portal = self.layer['portal']
        setRoles(self.portal, TEST_USER_ID, ['Manager'])
        self.form = api.content.create(
            container=self.portal,
            type='Form',
            id='test_form',
            title='Test Form'
        )

    def test_schema_handler_without_change_note(self):
        """Test that schema_handler does not set schema revisions without change note."""
        # Create event
        event = ObjectModifiedEvent(self.form)
        
        # Call handler
        schema_handler(self.form, event)
        
        # Without a change note, revisions should not be set
        self.assertFalse(hasattr(self.form, 'json_schema_rev'))
        self.assertFalse(hasattr(self.form, 'ui_schema_rev'))

    def test_schema_handler_with_change_note(self):
        """Test that schema_handler sets schema revisions when change note is present."""
        # Mock REQUEST with change note
        mock_request = Mock()
        mock_request.form = {'cmf.change_note': 'Test change'}
        self.form.REQUEST = mock_request
        
        # Create event
        event = ObjectModifiedEvent(self.form)
        
        # Call handler
        schema_handler(self.form, event)
        
        # With a change note, revisions should be set
        self.assertTrue(hasattr(self.form, 'json_schema_rev'))
        self.assertTrue(hasattr(self.form, 'ui_schema_rev'))
        self.assertIsNotNone(self.form.json_schema_rev)
        self.assertIsNotNone(self.form.ui_schema_rev)

    def test_schema_handler_stores_valid_schemas(self):
        """Test that schema_handler stores valid JSON schemas."""
        # Mock REQUEST with change note
        mock_request = Mock()
        mock_request.form = {'cmf.change_note': 'Test change'}
        self.form.REQUEST = mock_request
        
        # Create event
        event = ObjectModifiedEvent(self.form)
        
        # Call handler
        schema_handler(self.form, event)
        
        # Check that stored schemas are dictionaries (valid JSON structures)
        self.assertIsInstance(self.form.json_schema_rev, dict)
        self.assertIsInstance(self.form.ui_schema_rev, dict)
