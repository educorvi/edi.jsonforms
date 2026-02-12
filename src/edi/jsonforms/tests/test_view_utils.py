# -*- coding: utf-8 -*-
"""Tests for views/optionlist_view.py and views/common.py."""
from edi.jsonforms.testing import EDI_JSONFORMS_INTEGRATION_TESTING
from plone import api
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID

import unittest


class OptionListViewTest(unittest.TestCase):
    """Test OptionList view."""

    layer = EDI_JSONFORMS_INTEGRATION_TESTING

    def setUp(self):
        """Custom shared utility setup for tests."""
        self.portal = self.layer['portal']
        self.request = self.layer['request']
        setRoles(self.portal, TEST_USER_ID, ['Manager'])
        
        # Create a test form with selection field
        self.form = api.content.create(
            container=self.portal,
            type='Form',
            id='test_form',
            title='Test Form'
        )
        
        self.selection_field = api.content.create(
            container=self.form,
            type='SelectionField',
            id='selection',
            title='Selection Field'
        )
        
        # Create an option list
        self.option_list = api.content.create(
            container=self.selection_field,
            type='OptionList',
            id='options',
            title='Options'
        )
        self.option_list.options = ['key1:value1', 'key2:value2', 'key3:value3']

    def test_optionlist_view_accessible(self):
        """Test that optionlist view is accessible."""
        view = api.content.get_view(
            name='optionlist-view',
            context=self.option_list,
            request=self.request
        )
        
        # View should exist
        self.assertIsNotNone(view)

    def test_optionlist_view_returns_options(self):
        """Test that optionlist view returns options."""
        view = api.content.get_view(
            name='optionlist-view',
            context=self.option_list,
            request=self.request
        )
        
        # Should have options available
        self.assertTrue(hasattr(self.option_list, 'get_options'))
        options = self.option_list.get_options()
        self.assertEqual(len(options), 3)


class CommonViewUtilitiesTest(unittest.TestCase):
    """Test common view utilities."""

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

    def test_form_has_views(self):
        """Test that form has necessary views registered."""
        # Check that json-schema-view is available
        view = api.content.get_view(
            name='json-schema-view',
            context=self.form,
            request=self.request
        )
        self.assertIsNotNone(view)
        
        # Check that ui-schema-view is available
        view = api.content.get_view(
            name='ui-schema-view',
            context=self.form,
            request=self.request
        )
        self.assertIsNotNone(view)

    def test_form_view_is_accessible(self):
        """Test that form-view is accessible."""
        view = api.content.get_view(
            name='form-view',
            context=self.form,
            request=self.request
        )
        
        # View should exist and be callable
        self.assertIsNotNone(view)
        result = view()
        self.assertIsNotNone(result)
