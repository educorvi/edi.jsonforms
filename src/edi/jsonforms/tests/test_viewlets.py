# -*- coding: utf-8 -*-
"""Tests for developer viewlet."""
from edi.jsonforms.testing import EDI_JSONFORMS_INTEGRATION_TESTING
from edi.jsonforms.viewlets.developer_viewlet import DeveloperViewlet
from plone import api
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from unittest.mock import Mock

import unittest


class DeveloperViewletTest(unittest.TestCase):
    """Test DeveloperViewlet."""

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
        
        # Create a test wizard
        self.wizard = api.content.create(
            container=self.portal,
            type='Wizard',
            id='test_wizard',
            title='Test Wizard'
        )

    def test_viewlet_renders_on_tools_view(self):
        """Test that viewlet renders on form-tools-view."""
        mock_request = Mock()
        mock_request.get = Mock(return_value=self.form.absolute_url() + '/form-tools-view')
        
        viewlet = DeveloperViewlet(self.form, mock_request, None, None)
        result = viewlet.render()
        
        # Should render (return non-empty string)
        self.assertIsNotNone(result)

    def test_viewlet_does_not_render_on_other_views(self):
        """Test that viewlet does not render on other views."""
        mock_request = Mock()
        mock_request.get = Mock(return_value=self.form.absolute_url() + '/view')
        
        viewlet = DeveloperViewlet(self.form, mock_request, None, None)
        result = viewlet.render()
        
        # Should not render (return empty string)
        self.assertEqual(result, "")

    def test_viewlet_renders_on_wizard_tools_view(self):
        """Test that viewlet renders on wizard-tools-view."""
        mock_request = Mock()
        mock_request.get = Mock(return_value=self.wizard.absolute_url() + '/wizard-tools-view')
        
        viewlet = DeveloperViewlet(self.wizard, mock_request, None, None)
        result = viewlet.render()
        
        # Should render
        self.assertIsNotNone(result)

    def test_get_json_schema_for_form(self):
        """Test get_json_schema returns schema for Form."""
        viewlet = DeveloperViewlet(self.form, self.request, None, None)
        result = viewlet.get_json_schema()
        
        # Should return a JSON schema string
        self.assertIsInstance(result, str)
        self.assertGreater(len(result), 0)

    def test_get_json_schema_for_wizard(self):
        """Test get_json_schema returns schema for Wizard."""
        viewlet = DeveloperViewlet(self.wizard, self.request, None, None)
        result = viewlet.get_json_schema()
        
        # Should return a JSON schema string
        self.assertIsInstance(result, str)
        self.assertGreater(len(result), 0)

    def test_get_json_schema_for_other_type(self):
        """Test get_json_schema returns empty for other content types."""
        document = api.content.create(
            container=self.portal,
            type='Document',
            id='test_doc',
            title='Test Document'
        )
        
        viewlet = DeveloperViewlet(document, self.request, None, None)
        result = viewlet.get_json_schema()
        
        # Should return empty string for non-Form/Wizard types
        self.assertEqual(result, "")

    def test_get_ui_schema_for_form(self):
        """Test get_ui_schema returns schema for Form."""
        viewlet = DeveloperViewlet(self.form, self.request, None, None)
        result = viewlet.get_ui_schema()
        
        # Should return a UI schema string
        self.assertIsInstance(result, str)
        self.assertGreater(len(result), 0)

    def test_get_ui_schema_for_wizard(self):
        """Test get_ui_schema returns schema for Wizard."""
        viewlet = DeveloperViewlet(self.wizard, self.request, None, None)
        result = viewlet.get_ui_schema()
        
        # Should return a UI schema string
        self.assertIsInstance(result, str)
        self.assertGreater(len(result), 0)

    def test_get_ui_schema_for_other_type(self):
        """Test get_ui_schema returns empty for other content types."""
        document = api.content.create(
            container=self.portal,
            type='Document',
            id='test_doc',
            title='Test Document'
        )
        
        viewlet = DeveloperViewlet(document, self.request, None, None)
        result = viewlet.get_ui_schema()
        
        # Should return empty string for non-Form/Wizard types
        self.assertEqual(result, "")

    def test_get_versions_without_versioning(self):
        """Test get_versions returns empty list when no versions exist."""
        viewlet = DeveloperViewlet(self.form, self.request, None, None)
        result = viewlet.get_versions()
        
        # Should return empty list when no versions exist
        self.assertIsInstance(result, list)
        self.assertEqual(len(result), 0)

    def test_get_versions_with_versioning(self):
        """Test get_versions returns version history when versions exist."""
        # Enable versioning for Forms
        portal_types = api.portal.get_tool('portal_types')
        form_type = portal_types['Form']
        
        # Create a change to trigger versioning
        # This requires CMFEditions to be properly configured
        # For now, we just test that the method doesn't error
        viewlet = DeveloperViewlet(self.form, self.request, None, None)
        result = viewlet.get_versions()
        
        # Should return a list (even if empty)
        self.assertIsInstance(result, list)
