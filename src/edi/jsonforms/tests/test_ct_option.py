# -*- coding: utf-8 -*-
from edi.jsonforms.content.option import IOption  # NOQA E501
from edi.jsonforms.testing import EDI_JSONFORMS_INTEGRATION_TESTING  # noqa
from plone import api
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from plone.dexterity.interfaces import IDexterityFTI
from zope.component import createObject
from zope.component import queryUtility

import unittest




class OptionIntegrationTest(unittest.TestCase):

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

    def test_ct_option_schema(self):
        fti = queryUtility(IDexterityFTI, name='Option')
        schema = fti.lookupSchema()
        self.assertEqual(IOption, schema)

    def test_ct_option_fti(self):
        fti = queryUtility(IDexterityFTI, name='Option')
        self.assertTrue(fti)

    def test_ct_option_factory(self):
        fti = queryUtility(IDexterityFTI, name='Option')
        factory = fti.factory
        obj = createObject(factory)

        self.assertTrue(
            IOption.providedBy(obj),
            u'IOption not provided by {0}!'.format(
                obj,
            ),
        )

    def test_ct_option_adding(self):
        setRoles(self.portal, TEST_USER_ID, ['Contributor'])
        obj = api.content.create(
            container=self.parent,
            type='Option',
            id='option',
        )

        self.assertTrue(
            IOption.providedBy(obj),
            u'IOption not provided by {0}!'.format(
                obj.id,
            ),
        )

        parent = obj.__parent__
        self.assertIn('option', parent.objectIds())

        # check that deleting the object works too
        api.content.delete(obj=obj)
        self.assertNotIn('option', parent.objectIds())

    def test_ct_option_globally_not_addable(self):
        setRoles(self.portal, TEST_USER_ID, ['Contributor'])
        fti = queryUtility(IDexterityFTI, name='Option')
        self.assertFalse(
            fti.global_allow,
            u'{0} is globally addable!'.format(fti.id)
        )
