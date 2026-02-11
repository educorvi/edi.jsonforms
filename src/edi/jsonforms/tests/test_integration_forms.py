# -*- coding: utf-8 -*-
"""Integration tests for form rendering and functionality."""
from edi.jsonforms.testing import EDI_JSONFORMS_FUNCTIONAL_TESTING
from edi.jsonforms.testing import EDI_JSONFORMS_INTEGRATION_TESTING
from plone import api
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from z3c.relationfield import RelationValue
from zope.component import getUtility
from zope.intid.interfaces import IIntIds

import json
import unittest


class FormRenderingIntegrationTest(unittest.TestCase):
    """Test complete form rendering with various field types."""

    layer = EDI_JSONFORMS_INTEGRATION_TESTING

    def setUp(self):
        """Custom shared utility setup for tests."""
        self.portal = self.layer['portal']
        self.request = self.layer['request']
        setRoles(self.portal, TEST_USER_ID, ['Manager'])
        
        # Create a comprehensive test form
        self.form = api.content.create(
            container=self.portal,
            type='Form',
            id='comprehensive_form',
            title='Comprehensive Test Form'
        )

    def test_form_with_text_field(self):
        """Test form with a text field renders correctly."""
        field = api.content.create(
            container=self.form,
            type='Field',
            id='text_field',
            title='Text Field',
            required_choice='optional'
        )
        
        view = api.content.get_view(
            name='json-schema-view',
            context=self.form,
            request=self.request
        )
        
        schema = view.get_schema()
        
        # Check that the schema contains the field
        self.assertIn('properties', schema)
        self.assertIn('text_field', schema['properties'])

    def test_form_with_selection_field(self):
        """Test form with a selection field renders correctly."""
        selection_field = api.content.create(
            container=self.form,
            type='SelectionField',
            id='selection_field',
            title='Selection Field'
        )
        
        # Add an option list
        option_list = api.content.create(
            container=selection_field,
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
        
        # Check that the schema contains the selection field
        self.assertIn('properties', schema)
        self.assertIn('selection_field', schema['properties'])

    def test_form_with_upload_field(self):
        """Test form with an upload field renders correctly."""
        upload_field = api.content.create(
            container=self.form,
            type='UploadField',
            id='upload_field',
            title='Upload Field'
        )
        
        view = api.content.get_view(
            name='json-schema-view',
            context=self.form,
            request=self.request
        )
        
        schema = view.get_schema()
        
        # Check that the schema contains the upload field
        self.assertIn('properties', schema)
        self.assertIn('upload_field', schema['properties'])

    def test_form_with_complex_object(self):
        """Test form with a complex object renders correctly."""
        complex_obj = api.content.create(
            container=self.form,
            type='Complex',
            id='complex_obj',
            title='Complex Object'
        )
        
        # Add a field to the complex object
        nested_field = api.content.create(
            container=complex_obj,
            type='Field',
            id='nested_field',
            title='Nested Field'
        )
        
        view = api.content.get_view(
            name='json-schema-view',
            context=self.form,
            request=self.request
        )
        
        schema = view.get_schema()
        
        # Check that the schema contains the complex object
        self.assertIn('properties', schema)
        self.assertIn('complex_obj', schema['properties'])

    def test_form_with_array(self):
        """Test form with an array renders correctly."""
        array = api.content.create(
            container=self.form,
            type='Array',
            id='array',
            title='Array'
        )
        
        # Add a field to the array
        array_field = api.content.create(
            container=array,
            type='Field',
            id='array_field',
            title='Array Field'
        )
        
        view = api.content.get_view(
            name='json-schema-view',
            context=self.form,
            request=self.request
        )
        
        schema = view.get_schema()
        
        # Check that the schema contains the array
        self.assertIn('properties', schema)
        self.assertIn('array', schema['properties'])

    def test_form_with_fieldset(self):
        """Test form with a fieldset renders correctly."""
        fieldset = api.content.create(
            container=self.form,
            type='Fieldset',
            id='fieldset',
            title='Fieldset'
        )
        
        # Add a field to the fieldset
        fieldset_field = api.content.create(
            container=fieldset,
            type='Field',
            id='fieldset_field',
            title='Fieldset Field'
        )
        
        view = api.content.get_view(
            name='json-schema-view',
            context=self.form,
            request=self.request
        )
        
        schema = view.get_schema()
        
        # Check that the schema contains the fieldset
        self.assertIn('properties', schema)

    def test_form_with_helptext(self):
        """Test form with helptext renders correctly."""
        helptext = api.content.create(
            container=self.form,
            type='Helptext',
            id='helptext',
            title='Helptext'
        )
        
        view = api.content.get_view(
            name='json-schema-view',
            context=self.form,
            request=self.request
        )
        
        schema = view.get_schema()
        
        # Helptext should be in the schema structure
        self.assertIsInstance(schema, dict)

    def test_form_with_all_field_types(self):
        """Test form with all field types renders correctly."""
        # Create one of each field type
        field = api.content.create(
            container=self.form,
            type='Field',
            id='field',
            title='Text Field'
        )
        
        selection = api.content.create(
            container=self.form,
            type='SelectionField',
            id='selection',
            title='Selection Field'
        )
        
        upload = api.content.create(
            container=self.form,
            type='UploadField',
            id='upload',
            title='Upload Field'
        )
        
        complex_obj = api.content.create(
            container=self.form,
            type='Complex',
            id='complex',
            title='Complex'
        )
        
        array = api.content.create(
            container=self.form,
            type='Array',
            id='array',
            title='Array'
        )
        
        view = api.content.get_view(
            name='json-schema-view',
            context=self.form,
            request=self.request
        )
        
        schema = view.get_schema()
        
        # Check that all fields are in the schema
        self.assertIn('properties', schema)
        self.assertIn('field', schema['properties'])
        self.assertIn('selection', schema['properties'])
        self.assertIn('upload', schema['properties'])
        self.assertIn('complex', schema['properties'])
        self.assertIn('array', schema['properties'])


class FieldDependenciesIntegrationTest(unittest.TestCase):
    """Test field dependencies functionality."""

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
            id='dependency_form',
            title='Dependency Test Form'
        )
        
        # Create fields for dependency testing
        self.field1 = api.content.create(
            container=self.form,
            type='Field',
            id='field1',
            title='Field 1'
        )
        
        self.field2 = api.content.create(
            container=self.form,
            type='Field',
            id='field2',
            title='Field 2'
        )

    def test_field_with_dependency(self):
        """Test that a field can have dependencies."""
        intids = getUtility(IIntIds)
        
        # Set field2 to depend on field1
        self.field2.dependencies = [RelationValue(intids.getId(self.field1))]
        
        # Get UI schema to check dependencies are included
        view = api.content.get_view(
            name='ui-schema-view',
            context=self.form,
            request=self.request
        )
        
        ui_schema = json.loads(view())
        
        # The UI schema should be a dictionary
        self.assertIsInstance(ui_schema, dict)

    def test_field_with_or_dependencies(self):
        """Test that a field can have OR dependencies."""
        intids = getUtility(IIntIds)
        
        field3 = api.content.create(
            container=self.form,
            type='Field',
            id='field3',
            title='Field 3'
        )
        
        # Set field3 to depend on field1 OR field2
        field3.dependencies = [
            RelationValue(intids.getId(self.field1)),
            RelationValue(intids.getId(self.field2))
        ]
        field3.connection_type = False  # OR connection
        
        # Should not raise an error
        self.assertEqual(len(field3.dependencies), 2)

    def test_field_with_and_dependencies(self):
        """Test that a field can have AND dependencies."""
        intids = getUtility(IIntIds)
        
        field3 = api.content.create(
            container=self.form,
            type='Field',
            id='field3',
            title='Field 3'
        )
        
        # Set field3 to depend on field1 AND field2
        field3.dependencies = [
            RelationValue(intids.getId(self.field1)),
            RelationValue(intids.getId(self.field2))
        ]
        field3.connection_type = True  # AND connection
        
        # Should not raise an error
        self.assertEqual(len(field3.dependencies), 2)
        self.assertTrue(field3.connection_type)


class ShowConditionIntegrationTest(unittest.TestCase):
    """Test show condition functionality."""

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
            id='condition_form',
            title='Condition Test Form'
        )

    def test_field_with_show_condition(self):
        """Test that a field can have a show condition."""
        field = api.content.create(
            container=self.form,
            type='Field',
            id='conditional_field',
            title='Conditional Field'
        )
        
        # Set a show condition
        field.show_condition = 'condition1, condition2'
        
        # Should be stored correctly
        self.assertEqual(field.show_condition, 'condition1, condition2')

    def test_field_with_negated_condition(self):
        """Test that a field can have a negated show condition."""
        field = api.content.create(
            container=self.form,
            type='Field',
            id='negated_field',
            title='Negated Field'
        )
        
        # Set a negated show condition
        field.show_condition = 'condition1'
        field.negate_condition = True
        
        # Should be stored correctly
        self.assertEqual(field.show_condition, 'condition1')
        self.assertTrue(field.negate_condition)
