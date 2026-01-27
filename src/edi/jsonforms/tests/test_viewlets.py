# -*- coding: utf-8 -*-
from edi.jsonforms.testing import EDI_JSONFORMS_INTEGRATION_TESTING
from edi.jsonforms.viewlets.developer_viewlet import DeveloperViewlet
from plone import api
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID

import unittest


class DeveloperViewletTest(unittest.TestCase):
    """Test developer viewlet"""

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

    def test_viewlet_render_empty_without_tools_url(self):
        """Test that viewlet renders empty without tools URL"""
        viewlet = DeveloperViewlet(self.form, self.request, None, None)
        result = viewlet.render()
        
        # Should return empty string if not on tools view
        self.assertEqual(result, "")

    def test_viewlet_render_with_form_tools_url(self):
        """Test that viewlet renders with form-tools-view URL"""
        self.request['URL'] = self.form.absolute_url() + '/form-tools-view'
        viewlet = DeveloperViewlet(self.form, self.request, None, None)
        result = viewlet.render()
        
        # Should render viewlet template
        self.assertIsNotNone(result)

    def test_viewlet_render_with_wizard_tools_url(self):
        """Test that viewlet renders with wizard-tools-view URL"""
        # Create wizard instead
        wizard = api.content.create(
            container=self.portal,
            type='Wizard',
            id='test-wizard',
            title='Test Wizard',
        )
        
        self.request['URL'] = wizard.absolute_url() + '/wizard-tools-view'
        viewlet = DeveloperViewlet(wizard, self.request, None, None)
        result = viewlet.render()
        
        # Should render viewlet template
        self.assertIsNotNone(result)

    def test_get_json_schema_for_form(self):
        """Test get_json_schema for Form"""
        viewlet = DeveloperViewlet(self.form, self.request, None, None)
        schema = viewlet.get_json_schema()
        
        # Should return JSON schema
        self.assertIsInstance(schema, str)
        # Should be valid JSON
        import json
        parsed = json.loads(schema)
        self.assertIn('type', parsed)

    def test_get_ui_schema_for_form(self):
        """Test get_ui_schema for Form"""
        viewlet = DeveloperViewlet(self.form, self.request, None, None)
        schema = viewlet.get_ui_schema()
        
        # Should return UI schema
        self.assertIsInstance(schema, str)
        # Should be valid JSON
        import json
        parsed = json.loads(schema)
        self.assertIn('type', parsed)

    def test_get_json_schema_for_wizard(self):
        """Test get_json_schema for Wizard"""
        wizard = api.content.create(
            container=self.portal,
            type='Wizard',
            id='test-wizard',
            title='Test Wizard',
        )
        
        viewlet = DeveloperViewlet(wizard, self.request, None, None)
        schema = viewlet.get_json_schema()
        
        # Should return JSON schema
        self.assertIsInstance(schema, str)

    def test_get_ui_schema_for_wizard(self):
        """Test get_ui_schema for Wizard"""
        wizard = api.content.create(
            container=self.portal,
            type='Wizard',
            id='test-wizard',
            title='Test Wizard',
        )
        
        viewlet = DeveloperViewlet(wizard, self.request, None, None)
        schema = viewlet.get_ui_schema()
        
        # Should return UI schema
        self.assertIsInstance(schema, str)

    def test_get_json_schema_for_non_form(self):
        """Test get_json_schema for non-Form/Wizard type"""
        # Use portal itself
        viewlet = DeveloperViewlet(self.portal, self.request, None, None)
        schema = viewlet.get_json_schema()
        
        # Should return empty string
        self.assertEqual(schema, "")

    def test_get_ui_schema_for_non_form(self):
        """Test get_ui_schema for non-Form/Wizard type"""
        # Use portal itself
        viewlet = DeveloperViewlet(self.portal, self.request, None, None)
        schema = viewlet.get_ui_schema()
        
        # Should return empty string
        self.assertEqual(schema, "")

    def test_get_versions_without_history(self):
        """Test get_versions without version history"""
        viewlet = DeveloperViewlet(self.form, self.request, None, None)
        versions = viewlet.get_versions()
        
        # Should return empty list if no versions
        self.assertIsInstance(versions, list)

    def test_get_versions_returns_list(self):
        """Test that get_versions returns a list"""
        viewlet = DeveloperViewlet(self.form, self.request, None, None)
        versions = viewlet.get_versions()
        
        # Should always return a list
        self.assertIsInstance(versions, list)

    def test_viewlet_with_field_in_form(self):
        """Test viewlet with field in form"""
        field = api.content.create(
            container=self.form,
            type='Field',
            title='Test Field',
        )
        field.answer_type = 'text'
        
        viewlet = DeveloperViewlet(self.form, self.request, None, None)
        
        # Get schemas
        json_schema = viewlet.get_json_schema()
        ui_schema = viewlet.get_ui_schema()
        
        # Both should contain data
        self.assertTrue(len(json_schema) > 0)
        self.assertTrue(len(ui_schema) > 0)
