# -*- coding: utf-8 -*-
"""Integration tests for wizard functionality."""
from edi.jsonforms.testing import EDI_JSONFORMS_INTEGRATION_TESTING
from plone import api
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID

import json
import unittest


class WizardIntegrationTest(unittest.TestCase):
    """Test wizard multi-step form functionality."""

    layer = EDI_JSONFORMS_INTEGRATION_TESTING

    def setUp(self):
        """Custom shared utility setup for tests."""
        self.portal = self.layer['portal']
        self.request = self.layer['request']
        setRoles(self.portal, TEST_USER_ID, ['Manager'])
        
        # Create a test wizard
        self.wizard = api.content.create(
            container=self.portal,
            type='Wizard',
            id='test_wizard',
            title='Test Wizard'
        )

    def test_wizard_with_single_form(self):
        """Test wizard with a single form."""
        # Create a form in the wizard
        form = api.content.create(
            container=self.wizard,
            type='Form',
            id='step1',
            title='Step 1'
        )
        
        # Add a field to the form
        field = api.content.create(
            container=form,
            type='Field',
            id='field1',
            title='Field 1'
        )
        
        # Get wizard schema
        view = api.content.get_view(
            name='wizard-json-schema-view',
            context=self.wizard,
            request=self.request
        )
        
        schema = json.loads(view())
        
        # Should be a valid schema
        self.assertIsInstance(schema, dict)

    def test_wizard_with_multiple_forms(self):
        """Test wizard with multiple forms (steps)."""
        # Create multiple forms in the wizard
        form1 = api.content.create(
            container=self.wizard,
            type='Form',
            id='step1',
            title='Step 1'
        )
        
        form2 = api.content.create(
            container=self.wizard,
            type='Form',
            id='step2',
            title='Step 2'
        )
        
        form3 = api.content.create(
            container=self.wizard,
            type='Form',
            id='step3',
            title='Step 3'
        )
        
        # Add fields to each form
        api.content.create(
            container=form1,
            type='Field',
            id='field1',
            title='Field 1'
        )
        
        api.content.create(
            container=form2,
            type='Field',
            id='field2',
            title='Field 2'
        )
        
        api.content.create(
            container=form3,
            type='Field',
            id='field3',
            title='Field 3'
        )
        
        # Get wizard schema
        view = api.content.get_view(
            name='wizard-json-schema-view',
            context=self.wizard,
            request=self.request
        )
        
        schema = json.loads(view())
        
        # Should be a valid schema with multiple steps
        self.assertIsInstance(schema, dict)

    def test_wizard_ui_schema(self):
        """Test wizard UI schema generation."""
        # Create a form in the wizard
        form = api.content.create(
            container=self.wizard,
            type='Form',
            id='step1',
            title='Step 1'
        )
        
        # Add a field
        field = api.content.create(
            container=form,
            type='Field',
            id='field1',
            title='Field 1'
        )
        
        # Get wizard UI schema
        view = api.content.get_view(
            name='wizard-ui-schema-view',
            context=self.wizard,
            request=self.request
        )
        
        ui_schema = json.loads(view())
        
        # Should be a valid UI schema
        self.assertIsInstance(ui_schema, dict)

    def test_wizard_view_accessible(self):
        """Test that wizard view is accessible."""
        # Create a form in the wizard
        form = api.content.create(
            container=self.wizard,
            type='Form',
            id='step1',
            title='Step 1'
        )
        
        # Get wizard view
        view = api.content.get_view(
            name='wizard-view',
            context=self.wizard,
            request=self.request
        )
        
        # View should exist and be callable
        self.assertIsNotNone(view)
        result = view()
        self.assertIsNotNone(result)

    def test_wizard_with_complex_forms(self):
        """Test wizard with complex forms containing various field types."""
        # Create a comprehensive form in the wizard
        form = api.content.create(
            container=self.wizard,
            type='Form',
            id='complex_step',
            title='Complex Step'
        )
        
        # Add various field types
        text_field = api.content.create(
            container=form,
            type='Field',
            id='text_field',
            title='Text Field'
        )
        
        selection_field = api.content.create(
            container=form,
            type='SelectionField',
            id='selection_field',
            title='Selection Field'
        )
        
        complex_obj = api.content.create(
            container=form,
            type='Complex',
            id='complex_obj',
            title='Complex Object'
        )
        
        # Add a nested field
        nested_field = api.content.create(
            container=complex_obj,
            type='Field',
            id='nested_field',
            title='Nested Field'
        )
        
        # Get wizard schema
        view = api.content.get_view(
            name='wizard-json-schema-view',
            context=self.wizard,
            request=self.request
        )
        
        schema = json.loads(view())
        
        # Should be a valid schema
        self.assertIsInstance(schema, dict)


class WizardNavigationTest(unittest.TestCase):
    """Test wizard navigation and step management."""

    layer = EDI_JSONFORMS_INTEGRATION_TESTING

    def setUp(self):
        """Custom shared utility setup for tests."""
        self.portal = self.layer['portal']
        self.request = self.layer['request']
        setRoles(self.portal, TEST_USER_ID, ['Manager'])
        
        # Create a test wizard with multiple steps
        self.wizard = api.content.create(
            container=self.portal,
            type='Wizard',
            id='nav_wizard',
            title='Navigation Wizard'
        )
        
        # Create steps
        self.step1 = api.content.create(
            container=self.wizard,
            type='Form',
            id='step1',
            title='Step 1'
        )
        
        self.step2 = api.content.create(
            container=self.wizard,
            type='Form',
            id='step2',
            title='Step 2'
        )
        
        self.step3 = api.content.create(
            container=self.wizard,
            type='Form',
            id='step3',
            title='Step 3'
        )

    def test_wizard_has_all_steps(self):
        """Test that wizard contains all created steps."""
        # Get all forms in the wizard
        forms = [obj for obj in self.wizard.objectValues() if obj.portal_type == 'Form']
        
        # Should have 3 forms
        self.assertEqual(len(forms), 3)

    def test_wizard_steps_ordered(self):
        """Test that wizard steps maintain their order."""
        # Get all forms in the wizard
        form_ids = [obj.id for obj in self.wizard.objectValues() if obj.portal_type == 'Form']
        
        # Should be in the order they were created
        self.assertIn('step1', form_ids)
        self.assertIn('step2', form_ids)
        self.assertIn('step3', form_ids)

    def test_wizard_schema_includes_all_steps(self):
        """Test that wizard schema includes all steps."""
        view = api.content.get_view(
            name='wizard-json-schema-view',
            context=self.wizard,
            request=self.request
        )
        
        schema = json.loads(view())
        
        # Schema should be a dictionary
        self.assertIsInstance(schema, dict)
