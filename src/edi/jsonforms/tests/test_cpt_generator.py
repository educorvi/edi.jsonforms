# -*- coding: utf-8 -*-
"""Tests for the Chameleon Page Template Generator view."""

import unittest
import json
from unittest.mock import Mock, patch

from zope.interface import implementer
from zope.publisher.interfaces.browser import IDefaultBrowserLayer
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID

from edi.jsonforms.testing import EDI_JSONFORMS_INTEGRATION_TESTING
from edi.jsonforms.views.cpt_generator import ChameleonPageTemplateGenerator
from edi.jsonforms.content.form import IForm


class TestChameleonPageTemplateGenerator(unittest.TestCase):
    """Test the ChameleonPageTemplateGenerator view."""

    layer = EDI_JSONFORMS_INTEGRATION_TESTING

    def setUp(self):
        """Set up test fixtures."""
        self.app = self.layer['app']
        self.portal = self.layer['portal']
        self.request = self.layer['request']
        setRoles(self.portal, TEST_USER_ID, ['Manager'])
        
        # Create a mock form context
        self.mock_form = Mock()
        self.mock_form.title = "Test Form"
        self.mock_form.description = "Test form description"
        
        # Mock getFolderContents to return empty list by default
        self.mock_form.getFolderContents.return_value = []
        
    def _create_mock_field(self, field_id, portal_type='Field'):
        """Helper to create a mock field object."""
        mock_brain = Mock()
        mock_object = Mock()
        mock_object.portal_type = portal_type
        mock_object.show_condition = ""
        mock_object.negate_condition = False
        mock_object.getId.return_value = field_id
        mock_brain.getObject.return_value = mock_object
        return mock_brain

    @patch('edi.jsonforms.views.cpt_generator.create_id')
    @patch('edi.jsonforms.views.cpt_generator.check_show_condition_in_request')
    @patch('edi.jsonforms.views.json_schema_view.JsonSchemaView')
    @patch('edi.jsonforms.views.simple_ui_schema_view.SimpleUiSchemaView')
    def test_basic_template_generation(self, mock_ui_view, mock_json_view, mock_check_condition, mock_create_id):
        """Test basic template generation with simple fields."""
        # Setup mocks
        mock_check_condition.return_value = True  # Always show fields
        mock_create_id.side_effect = lambda obj: obj.getId()  # Return field ID
        
        # Create mock form children
        name_field = self._create_mock_field('name')
        email_field = self._create_mock_field('email')
        self.mock_form.getFolderContents.return_value = [name_field, email_field]
        
        # Mock JSON schema
        json_schema_data = json.dumps({
            "type": "object",
            "properties": {
                "name": {
                    "type": "string",
                    "title": "Full Name"
                },
                "email": {
                    "type": "string",
                    "title": "Email Address"
                }
            },
            "required": ["name"]
        })
        mock_json_instance = Mock()
        mock_json_instance.return_value = json_schema_data
        mock_json_view.return_value = mock_json_instance
        
        # Mock UI schema
        ui_schema_data = json.dumps({
            "name": {
                "ui:title": "Full Name",
                "ui:description": "Enter your complete name"
            },
            "email": {
                "ui:title": "Email Address",
                "ui:widget": "email"
            }
        })
        mock_ui_instance = Mock()
        mock_ui_instance.return_value = ui_schema_data
        mock_ui_view.return_value = mock_ui_instance
        
        # Create view instance
        view = ChameleonPageTemplateGenerator(self.mock_form, self.request)
        
        # Generate template
        template = view.generate_chameleon_template()
        
        # Assertions
        self.assertIn('<div class="container">', template)
        self.assertIn('tal:content="view.title"', template)
        self.assertIn('tal:content="view.description"', template)
        self.assertIn('<form', template)
        self.assertIn('method="POST"', template)
        self.assertIn('enctype="multipart/form-data"', template)
        self.assertIn('<div class="row">', template)
        self.assertIn('col-12', template)
        self.assertIn("tal:replace=\"structure form['name'].render_template", template)
        self.assertIn("tal:replace=\"structure form['email'].render_template", template)

    @patch('edi.jsonforms.views.cpt_generator.create_id')
    @patch('edi.jsonforms.views.cpt_generator.check_show_condition_in_request')
    @patch('edi.jsonforms.views.json_schema_view.JsonSchemaView')
    @patch('edi.jsonforms.views.simple_ui_schema_view.SimpleUiSchemaView')
    def test_conditional_fields(self, mock_ui_view, mock_json_view, mock_check_condition, mock_create_id):
        """Test template generation with conditional fields."""
        # Setup mocks
        mock_check_condition.return_value = True  # Always show fields
        mock_create_id.side_effect = lambda obj: obj.getId()  # Return field ID
        
        # Create mock form children
        checkbox_field = self._create_mock_field('hasSpecialNeeds')
        description_field = self._create_mock_field('specialNeedsDescription')
        self.mock_form.getFolderContents.return_value = [checkbox_field, description_field]
        
        # Mock JSON schema
        json_schema_data = json.dumps({
            "type": "object",
            "properties": {
                "hasSpecialNeeds": {
                    "type": "boolean",
                    "title": "I have special needs"
                },
                "specialNeedsDescription": {
                    "type": "string",
                    "title": "Special Needs Description"
                }
            }
        })
        mock_json_instance = Mock()
        mock_json_instance.return_value = json_schema_data
        mock_json_view.return_value = mock_json_instance
        
        # Mock UI schema with conditions in ui:attributes format
        ui_schema_data = json.dumps({
            "hasSpecialNeeds": {
                "ui:title": "I have special needs",
                "ui:widget": "checkbox",
                "ui:attributes": {
                    "data-condition-target": "specialNeedsDescription"
                }
            },
            "specialNeedsDescription": {
                "ui:title": "Special Needs Description",
                "ui:widget": "textarea",
                "ui:attributes": {
                    "data-conditions": "{'field': 'hasSpecialNeeds', 'operator': 'equals', 'value': true}",
                    "data-condition-logic": "and"
                }
            }
        })
        mock_ui_instance = Mock()
        mock_ui_instance.return_value = ui_schema_data
        mock_ui_view.return_value = mock_ui_instance
        
        # Create view instance
        view = ChameleonPageTemplateGenerator(self.mock_form, self.request)
        
        # Generate template
        template = view.generate_chameleon_template()
        
        # Assertions for conditional fields - conditions now in ui:attributes
        self.assertIn('data-condition-target="specialNeedsDescription"', template)
        self.assertIn('data-conditions=', template)
        self.assertIn('data-condition-logic=', template)
        self.assertIn("'field': 'hasSpecialNeeds'", template)
        self.assertIn("'operator': 'equals'", template)
        self.assertIn("'value': true", template)

    @patch('edi.jsonforms.views.cpt_generator.create_id')
    @patch('edi.jsonforms.views.cpt_generator.check_show_condition_in_request')
    @patch('edi.jsonforms.views.json_schema_view.JsonSchemaView')
    @patch('edi.jsonforms.views.simple_ui_schema_view.SimpleUiSchemaView')
    def test_column_layout_grouping(self, mock_ui_view, mock_json_view, mock_check_condition, mock_create_id):
        """Test that fields are grouped correctly by Bootstrap columns."""
        # Setup mocks
        mock_check_condition.return_value = True  # Always show fields
        mock_create_id.side_effect = lambda obj: obj.getId()  # Return field ID
        
        # Create mock form children
        field1 = self._create_mock_field('field1')
        field2 = self._create_mock_field('field2')
        field3 = self._create_mock_field('field3')
        field4 = self._create_mock_field('field4')
        self.mock_form.getFolderContents.return_value = [field1, field2, field3, field4]
        
        # Mock JSON schema with multiple fields
        json_schema_data = json.dumps({
            "type": "object",
            "properties": {
                "field1": {"type": "string", "title": "Field 1"},
                "field2": {"type": "string", "title": "Field 2"},
                "field3": {"type": "string", "title": "Field 3"},
                "field4": {"type": "string", "title": "Field 4"}
            }
        })
        mock_json_instance = Mock()
        mock_json_instance.return_value = json_schema_data
        mock_json_view.return_value = mock_json_instance
        
        # Mock UI schema without ui:column (static col-12 implementation)
        ui_schema_data = json.dumps({
            "field1": {"ui:title": "Field 1"},
            "field2": {"ui:title": "Field 2"},
            "field3": {"ui:title": "Field 3"},
            "field4": {"ui:title": "Field 4"}
        })
        mock_ui_instance = Mock()
        mock_ui_instance.return_value = ui_schema_data
        mock_ui_view.return_value = mock_ui_instance
        
        # Create view instance
        view = ChameleonPageTemplateGenerator(self.mock_form, self.request)
        
        # Generate template
        template = view.generate_chameleon_template()
        
        # Count rows - should have 4 rows since all fields use static col-12 (full width)
        # Row 1: field1 (12)
        # Row 2: field2 (12) 
        # Row 3: field3 (12)
        # Row 4: field4 (12)
        row_count = template.count('<div class="row">')
        self.assertEqual(row_count, 4)
        
        # Check that all fields use static col-12
        self.assertIn('col-12', template)
        # Should have 4 instances of col-12
        self.assertEqual(template.count('col-12'), 4)


    @patch('edi.jsonforms.views.json_schema_view.JsonSchemaView')
    @patch('edi.jsonforms.views.simple_ui_schema_view.SimpleUiSchemaView')
    def test_view_call_returns_string(self, mock_ui_view, mock_json_view):
        """Test that the view __call__ method returns a string."""
        # Mock minimal schemas
        json_schema_data = '{"type": "object", "properties": {}}'
        mock_json_instance = Mock()
        mock_json_instance.return_value = json_schema_data
        mock_json_view.return_value = mock_json_instance
        
        ui_schema_data = '{}'
        mock_ui_instance = Mock()
        mock_ui_instance.return_value = ui_schema_data
        mock_ui_view.return_value = mock_ui_instance
        
        # Create view instance
        view = ChameleonPageTemplateGenerator(self.mock_form, self.request)
        
        # Call the view
        result = view()
        
        # Assertions
        self.assertIsInstance(result, str)
        self.assertIn('<div class="container">', result)
        self.assertEqual(self.request.response.getHeader('Content-Type'), 'text/plain; charset=utf-8')

    def test_prepare_conditions_data(self):
        """Test conditions data preparation with single quotes."""
        view = ChameleonPageTemplateGenerator(self.mock_form, self.request)
        
        ui_config = {
            "ui:conditions": [
                {
                    "field": "testField",
                    "operator": "equals",
                    "value": "testValue"
                }
            ],
            "ui:condition_logic": "and"
        }
        
        result = view._prepare_conditions_data(ui_config)
        
        # Should use single quotes instead of escaped double quotes
        self.assertIn("'conditions'", result["data-conditions"])
        self.assertIn("'field': 'testField'", result["data-conditions"])
        self.assertNotIn('&quot;', result["data-conditions"])
        self.assertEqual(result["data-condition-logic"], "and")


if __name__ == '__main__':
    unittest.main()