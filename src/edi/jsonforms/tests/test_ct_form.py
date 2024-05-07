# -*- coding: utf-8 -*-
from edi.jsonforms.content.form import IForm  # NOQA E501
from edi.jsonforms.testing import EDI_JSONFORMS_INTEGRATION_TESTING  # noqa
from plone import api
from plone.api.exc import InvalidParameterError
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from plone.dexterity.interfaces import IDexterityFTI
from zope.component import createObject
from zope.component import queryUtility

import unittest




class FormIntegrationTest(unittest.TestCase):

    layer = EDI_JSONFORMS_INTEGRATION_TESTING

    def setUp(self):
        """Custom shared utility setup for tests."""
        self.portal = self.layer['portal']
        setRoles(self.portal, TEST_USER_ID, ['Manager'])
        self.parent = self.portal

    def test_ct_form_schema(self):
        fti = queryUtility(IDexterityFTI, name='Form')
        schema = fti.lookupSchema()
        self.assertEqual(IForm, schema)

    def test_ct_form_fti(self):
        fti = queryUtility(IDexterityFTI, name='Form')
        self.assertTrue(fti)

    def test_ct_form_factory(self):
        fti = queryUtility(IDexterityFTI, name='Form')
        factory = fti.factory
        obj = createObject(factory)

        self.assertTrue(
            IForm.providedBy(obj),
            u'IForm not provided by {0}!'.format(
                obj,
            ),
        )

    def test_ct_form_adding(self):
        setRoles(self.portal, TEST_USER_ID, ['Contributor'])
        obj = api.content.create(
            container=self.portal,
            type='Form',
            id='form',
        )

        self.assertTrue(
            IForm.providedBy(obj),
            u'IForm not provided by {0}!'.format(
                obj.id,
            ),
        )

        parent = obj.__parent__
        self.assertIn('form', parent.objectIds())

        # check that deleting the object works too
        api.content.delete(obj=obj)
        self.assertNotIn('form', parent.objectIds())

    def test_ct_form_globally_addable(self):
        setRoles(self.portal, TEST_USER_ID, ['Contributor'])
        fti = queryUtility(IDexterityFTI, name='Form')
        self.assertTrue(
            fti.global_allow,
            u'{0} is not globally addable!'.format(fti.id)
        )

    def test_ct_form_filter_content_type_true(self):
        setRoles(self.portal, TEST_USER_ID, ['Contributor'])
        fti = queryUtility(IDexterityFTI, name='Form')
        portal_types = self.portal.portal_types
        parent_id = portal_types.constructContent(
            fti.id,
            self.portal,
            'form_id',
            title='Form container',
         )
        self.parent = self.portal[parent_id]
        with self.assertRaises(InvalidParameterError):
            api.content.create(
                container=self.parent,
                type='Document',
                title='My Content',
            )
