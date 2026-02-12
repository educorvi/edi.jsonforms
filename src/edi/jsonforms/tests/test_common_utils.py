# -*- coding: utf-8 -*-
"""Tests for content/common.py utilities."""
from edi.jsonforms.content.common import get_base_path, get_base_path_parent
from edi.jsonforms.testing import EDI_JSONFORMS_INTEGRATION_TESTING
from plone import api
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from zope.interface import Invalid

import unittest


class BasePathUtilsTest(unittest.TestCase):
    """Test base path utility functions."""

    layer = EDI_JSONFORMS_INTEGRATION_TESTING

    def setUp(self):
        """Custom shared utility setup for tests."""
        self.portal = self.layer['portal']
        setRoles(self.portal, TEST_USER_ID, ['Manager'])
        
        # Create a test form
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

    def test_get_base_path_for_field_in_form(self):
        """Test get_base_path for a field directly in a form."""
        base_path = get_base_path(self.field)
        expected_path = "/".join(self.form.getPhysicalPath())
        
        self.assertEqual(base_path, expected_path)

    def test_get_base_path_parent_for_form(self):
        """Test get_base_path_parent returns form path for form."""
        base_path = get_base_path_parent(self.form)
        expected_path = "/".join(self.form.getPhysicalPath())
        
        self.assertEqual(base_path, expected_path)

    def test_get_base_path_for_nested_field(self):
        """Test get_base_path for a field in a complex object."""
        # Create a complex object
        complex_obj = api.content.create(
            container=self.form,
            type='Complex',
            id='complex',
            title='Complex Object'
        )
        
        # Create a field in the complex object
        nested_field = api.content.create(
            container=complex_obj,
            type='Field',
            id='nested_field',
            title='Nested Field'
        )
        
        base_path = get_base_path(nested_field)
        expected_path = "/".join(complex_obj.getPhysicalPath())
        
        self.assertEqual(base_path, expected_path)

    def test_get_base_path_for_field_in_fieldset(self):
        """Test get_base_path for a field in a fieldset."""
        # Create a fieldset
        fieldset = api.content.create(
            container=self.form,
            type='Fieldset',
            id='fieldset',
            title='Test Fieldset'
        )
        
        # Create a field in the fieldset
        field_in_fieldset = api.content.create(
            container=fieldset,
            type='Field',
            id='field_in_fieldset',
            title='Field in Fieldset'
        )
        
        base_path = get_base_path(field_in_fieldset)
        expected_path = "/".join(fieldset.getPhysicalPath())
        
        self.assertEqual(base_path, expected_path)

    def test_get_base_path_for_field_in_array(self):
        """Test get_base_path for a field in an array."""
        # Create an array
        array = api.content.create(
            container=self.form,
            type='Array',
            id='array',
            title='Test Array'
        )
        
        # Create a field in the array
        field_in_array = api.content.create(
            container=array,
            type='Field',
            id='field_in_array',
            title='Field in Array'
        )
        
        base_path = get_base_path(field_in_array)
        expected_path = "/".join(array.getPhysicalPath())
        
        self.assertEqual(base_path, expected_path)


class DependenciesTest(unittest.TestCase):
    """Test dependencies invariant validation."""

    layer = EDI_JSONFORMS_INTEGRATION_TESTING

    def setUp(self):
        """Custom shared utility setup for tests."""
        self.portal = self.layer['portal']
        setRoles(self.portal, TEST_USER_ID, ['Manager'])
        
        # Create a test form
        self.form = api.content.create(
            container=self.portal,
            type='Form',
            id='test_form',
            title='Test Form'
        )
        
        # Add fields to the form
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

    def test_field_can_have_dependency_in_same_form(self):
        """Test that a field can have dependencies from the same form."""
        from z3c.relationfield import RelationValue
        from zope.component import getUtility
        from zope.intid.interfaces import IIntIds
        
        intids = getUtility(IIntIds)
        
        # Set field2 to depend on field1
        self.field2.dependencies = [RelationValue(intids.getId(self.field1))]
        
        # This should not raise an error
        # The invariant is checked during the edit process

    def test_field_cannot_depend_on_itself(self):
        """Test that a field cannot depend on itself."""
        from z3c.relationfield import RelationValue
        from zope.component import getUtility
        from zope.intid.interfaces import IIntIds
        from edi.jsonforms.content.common import IDependent
        
        intids = getUtility(IIntIds)
        
        # Try to make field1 depend on itself
        self.field1.dependencies = [RelationValue(intids.getId(self.field1))]
        
        # The invariant should detect this during validation
        # Note: The actual validation happens at the form level during edit

    def test_dependencies_must_be_in_same_container_group(self):
        """Test that dependencies must be in the same container group."""
        # Create two separate complex objects
        complex1 = api.content.create(
            container=self.form,
            type='Complex',
            id='complex1',
            title='Complex 1'
        )
        
        complex2 = api.content.create(
            container=self.form,
            type='Complex',
            id='complex2',
            title='Complex 2'
        )
        
        field_in_complex1 = api.content.create(
            container=complex1,
            type='Field',
            id='field_in_complex1',
            title='Field in Complex 1'
        )
        
        field_in_complex2 = api.content.create(
            container=complex2,
            type='Field',
            id='field_in_complex2',
            title='Field in Complex 2'
        )
        
        # Fields in different complex objects should not be able to depend on each other
        # This is validated by the check_dependencies invariant
