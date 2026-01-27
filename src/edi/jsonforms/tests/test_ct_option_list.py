# -*- coding: utf-8 -*-
from edi.jsonforms.content.option_list import IOptionList, get_keys_and_values_for_options_list  # NOQA E501
from edi.jsonforms.testing import EDI_JSONFORMS_INTEGRATION_TESTING  # noqa
from plone import api
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from plone.dexterity.interfaces import IDexterityFTI
from zope.component import createObject
from zope.component import queryUtility

import unittest


class OptionListIntegrationTest(unittest.TestCase):

    layer = EDI_JSONFORMS_INTEGRATION_TESTING

    def setUp(self):
        """Custom shared utility setup for tests."""
        self.portal = self.layer['portal']
        setRoles(self.portal, TEST_USER_ID, ['Manager'])
        portal_types = self.portal.portal_types
        parent_id = portal_types.constructContent(
            'SelectionField',
            self.portal,
            'parent_container',
            title='Parent container',
        )
        self.parent = self.portal[parent_id]

    def test_ct_option_list_schema(self):
        fti = queryUtility(IDexterityFTI, name='OptionList')
        schema = fti.lookupSchema()
        self.assertEqual(IOptionList, schema)

    def test_ct_option_list_fti(self):
        fti = queryUtility(IDexterityFTI, name='OptionList')
        self.assertTrue(fti)

    def test_ct_option_list_factory(self):
        fti = queryUtility(IDexterityFTI, name='OptionList')
        factory = fti.factory
        obj = createObject(factory)

        self.assertTrue(
            IOptionList.providedBy(obj),
            u'IOptionList not provided by {0}!'.format(
                obj,
            ),
        )

    def test_ct_option_list_adding(self):
        setRoles(self.portal, TEST_USER_ID, ['Contributor'])
        obj = api.content.create(
            container=self.parent,
            type='OptionList',
            id='optionlist',
        )

        self.assertTrue(
            IOptionList.providedBy(obj),
            u'IOptionList not provided by {0}!'.format(
                obj.id,
            ),
        )

        parent = obj.__parent__
        self.assertIn('optionlist', parent.objectIds())

        # check that deleting the object works too
        api.content.delete(obj=obj)
        self.assertNotIn('optionlist', parent.objectIds())

    def test_ct_option_list_globally_not_addable(self):
        setRoles(self.portal, TEST_USER_ID, ['Contributor'])
        fti = queryUtility(IDexterityFTI, name='OptionList')
        self.assertFalse(
            fti.global_allow,
            u'{0} is globally addable!'.format(fti.id)
        )


class OptionListFunctionalityTest(unittest.TestCase):
    """Test OptionList functionality"""

    layer = EDI_JSONFORMS_INTEGRATION_TESTING

    def setUp(self):
        """Custom shared utility setup for tests."""
        self.portal = self.layer['portal']
        setRoles(self.portal, TEST_USER_ID, ['Manager'])
        portal_types = self.portal.portal_types
        parent_id = portal_types.constructContent(
            'SelectionField',
            self.portal,
            'parent_container',
            title='Parent container',
        )
        self.parent = self.portal[parent_id]
        self.optionlist = api.content.create(
            container=self.parent,
            type='OptionList',
            id='optionlist',
        )

    def test_get_keys_and_values_simple(self):
        """Test simple options without ids"""
        self.optionlist.options = ['Option 1', 'Option 2', 'Option 3']
        keys, values = get_keys_and_values_for_options_list(self.optionlist)
        self.assertEqual(keys, ['Option 1', 'Option 2', 'Option 3'])
        self.assertEqual(values, ['Option 1', 'Option 2', 'Option 3'])

    def test_get_keys_and_values_with_ids(self):
        """Test options with id:value format"""
        self.optionlist.options = ['opt1:Option 1', 'opt2:Option 2', 'opt3:Option 3']
        keys, values = get_keys_and_values_for_options_list(self.optionlist)
        self.assertEqual(keys, ['opt1', 'opt2', 'opt3'])
        self.assertEqual(values, ['Option 1', 'Option 2', 'Option 3'])

    def test_get_keys_and_values_mixed(self):
        """Test mixed options with and without ids"""
        self.optionlist.options = ['opt1:Option 1', 'Option 2', 'opt3:Option 3']
        keys, values = get_keys_and_values_for_options_list(self.optionlist)
        self.assertEqual(keys, ['opt1', 'Option 2', 'opt3'])
        self.assertEqual(values, ['Option 1', 'Option 2', 'Option 3'])

    def test_get_keys_and_values_with_colons_in_value(self):
        """Test options with multiple colons in value"""
        self.optionlist.options = ['opt1:Value: with colons', 'opt2:Another: value: here']
        keys, values = get_keys_and_values_for_options_list(self.optionlist)
        self.assertEqual(keys, ['opt1', 'opt2'])
        self.assertEqual(values, ['Value: with colons', 'Another: value: here'])

    def test_get_keys_and_values_empty(self):
        """Test empty options list"""
        self.optionlist.options = []
        keys, values = get_keys_and_values_for_options_list(self.optionlist)
        self.assertEqual(keys, [])
        self.assertEqual(values, [])
