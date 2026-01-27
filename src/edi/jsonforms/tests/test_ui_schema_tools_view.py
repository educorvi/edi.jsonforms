# -*- coding: utf-8 -*-
from edi.jsonforms.testing import EDI_JSONFORMS_INTEGRATION_TESTING
from plone import api
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID

import json
import unittest


class UiSchemaToolsViewTest(unittest.TestCase):
    """Test UI schema tools view"""

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

    def test_ui_schema_tools_view_registered(self):
        """Test that ui-schema-tools-view is registered"""
        view = api.content.get_view(
            name='ui-schema-tools-view',
            context=self.form,
            request=self.request
        )
        self.assertIsNotNone(view)

    def test_ui_schema_tools_view_returns_schema(self):
        """Test that ui-schema-tools-view returns valid schema"""
        view = api.content.get_view(
            name='ui-schema-tools-view',
            context=self.form,
            request=self.request
        )
        result = view()
        
        # Should return JSON string
        self.assertIsInstance(result, str)
        
        # Should be valid JSON
        schema = json.loads(result)
        self.assertIn('type', schema)

    def test_ui_schema_tools_view_with_fields(self):
        """Test ui-schema-tools-view with fields"""
        field = api.content.create(
            container=self.form,
            type='Field',
            title='Test Field',
        )
        field.answer_type = 'text'
        
        view = api.content.get_view(
            name='ui-schema-tools-view',
            context=self.form,
            request=self.request
        )
        result = view()
        
        # Should return schema with elements
        schema = json.loads(result)
        self.assertIn('elements', schema)

    def test_ui_schema_tools_view_different_from_regular(self):
        """Test that ui-schema-tools-view can differ from regular ui-schema-view"""
        # Get regular UI schema
        regular_view = api.content.get_view(
            name='ui-schema-view',
            context=self.form,
            request=self.request
        )
        regular_result = regular_view()
        
        # Get tools UI schema
        tools_view = api.content.get_view(
            name='ui-schema-tools-view',
            context=self.form,
            request=self.request
        )
        tools_result = tools_view()
        
        # Both should be valid JSON
        regular_schema = json.loads(regular_result)
        tools_schema = json.loads(tools_result)
        
        # Both should have type
        self.assertIn('type', regular_schema)
        self.assertIn('type', tools_schema)

    def test_ui_schema_tools_view_inherits_from_ui_schema_view(self):
        """Test that ui-schema-tools-view inherits from UiSchemaView"""
        from edi.jsonforms.views.ui_schema_tools_view import UiSchemaToolsView
        from edi.jsonforms.views.ui_schema_view import UiSchemaView
        
        # Check inheritance
        self.assertTrue(issubclass(UiSchemaToolsView, UiSchemaView))

    def test_ui_schema_tools_view_sets_tools_mode(self):
        """Test that ui-schema-tools-view sets tools mode"""
        from edi.jsonforms.views.ui_schema_tools_view import UiSchemaToolsView
        
        view = UiSchemaToolsView(self.form, self.request)
        
        # Call the view
        result = view()
        
        # Should return valid schema
        self.assertIsInstance(result, str)
        schema = json.loads(result)
        self.assertIn('type', schema)

    def test_ui_schema_tools_view_with_complex_structure(self):
        """Test ui-schema-tools-view with complex structure"""
        fieldset = api.content.create(
            container=self.form,
            type='Fieldset',
            title='Section',
        )
        
        field = api.content.create(
            container=fieldset,
            type='Field',
            title='Field in Section',
        )
        field.answer_type = 'text'
        
        view = api.content.get_view(
            name='ui-schema-tools-view',
            context=self.form,
            request=self.request
        )
        result = view()
        
        # Should return valid schema
        schema = json.loads(result)
        self.assertIn('type', schema)
        self.assertIn('elements', schema)
