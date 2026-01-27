# -*- coding: utf-8 -*-
from edi.jsonforms.testing import EDI_JSONFORMS_INTEGRATION_TESTING
from edi.jsonforms.content.common import get_base_path, get_base_path_parent
from edi.jsonforms.views.common import create_id
from plone import api
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID

import unittest


class CommonUtilitiesTest(unittest.TestCase):
    """Test common utility functions"""

    layer = EDI_JSONFORMS_INTEGRATION_TESTING

    def setUp(self):
        """Custom shared utility setup for tests."""
        self.portal = self.layer['portal']
        setRoles(self.portal, TEST_USER_ID, ['Manager'])
        
        # Create a form hierarchy
        self.form = api.content.create(
            container=self.portal,
            type='Form',
            id='test-form',
            title='Test Form',
        )

    def test_create_id_simple(self):
        """Test create_id with simple object"""
        field = api.content.create(
            container=self.form,
            type='Field',
            title='Test Field',
        )
        
        field_id = create_id(field)
        self.assertIsInstance(field_id, str)
        self.assertTrue(len(field_id) > 0)

    def test_create_id_consistent(self):
        """Test that create_id returns consistent IDs"""
        field = api.content.create(
            container=self.form,
            type='Field',
            title='Test Field',
        )
        
        id1 = create_id(field)
        id2 = create_id(field)
        self.assertEqual(id1, id2)

    def test_get_base_path_from_field(self):
        """Test get_base_path from a field"""
        field = api.content.create(
            container=self.form,
            type='Field',
            title='Test Field',
        )
        
        base_path = get_base_path(field)
        self.assertIn('test-form', base_path)

    def test_get_base_path_from_nested_field(self):
        """Test get_base_path from a nested field in fieldset"""
        fieldset = api.content.create(
            container=self.form,
            type='Fieldset',
            title='Test Fieldset',
        )
        
        field = api.content.create(
            container=fieldset,
            type='Field',
            title='Nested Field',
        )
        
        base_path = get_base_path(field)
        self.assertIn('test-fieldset', base_path)

    def test_get_base_path_from_complex(self):
        """Test get_base_path from a field in complex"""
        complex_field = api.content.create(
            container=self.form,
            type='Complex',
            title='Test Complex',
        )
        
        field = api.content.create(
            container=complex_field,
            type='Field',
            title='Complex Field',
        )
        
        base_path = get_base_path(field)
        self.assertIn('test-complex', base_path)

    def test_get_base_path_from_array(self):
        """Test get_base_path from a field in array"""
        array = api.content.create(
            container=self.form,
            type='Array',
            title='Test Array',
        )
        
        field = api.content.create(
            container=array,
            type='Field',
            title='Array Field',
        )
        
        base_path = get_base_path(field)
        self.assertIn('test-array', base_path)

    def test_get_base_path_parent_from_form(self):
        """Test get_base_path_parent from form"""
        base_path = get_base_path_parent(self.form)
        self.assertIn('test-form', base_path)

    def test_get_base_path_parent_from_fieldset(self):
        """Test get_base_path_parent from fieldset"""
        fieldset = api.content.create(
            container=self.form,
            type='Fieldset',
            title='Test Fieldset',
        )
        
        base_path = get_base_path_parent(fieldset)
        self.assertIn('test-fieldset', base_path)

    def test_get_base_path_parent_from_field(self):
        """Test get_base_path_parent from field's parent"""
        field = api.content.create(
            container=self.form,
            type='Field',
            title='Test Field',
        )
        
        base_path = get_base_path_parent(field.aq_parent)
        self.assertIn('test-form', base_path)

    def test_get_base_path_deeply_nested(self):
        """Test get_base_path from deeply nested structure"""
        fieldset = api.content.create(
            container=self.form,
            type='Fieldset',
            title='Test Fieldset',
        )
        
        complex_field = api.content.create(
            container=fieldset,
            type='Complex',
            title='Test Complex',
        )
        
        field = api.content.create(
            container=complex_field,
            type='Field',
            title='Deeply Nested Field',
        )
        
        base_path = get_base_path(field)
        self.assertIn('test-complex', base_path)
