# -*- coding: utf-8 -*-
from edi.jsonforms.content.upload_field import IUploadField  # NOQA E501
from edi.jsonforms.testing import EDI_JSONFORMS_INTEGRATION_TESTING  # noqa
from plone import api
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from plone.dexterity.interfaces import IDexterityFTI
from zope.component import createObject
from zope.component import queryUtility

import unittest




class UploadFieldIntegrationTest(unittest.TestCase):

    layer = EDI_JSONFORMS_INTEGRATION_TESTING

    def setUp(self):
        """Custom shared utility setup for tests."""
        self.portal = self.layer['portal']
        setRoles(self.portal, TEST_USER_ID, ['Manager'])
        portal_types = self.portal.portal_types
        parent_id = portal_types.constructContent(
            'Form',
            self.portal,
            'parent_container',
            title='Parent container',
        )
        self.parent = self.portal[parent_id]

    def test_ct_upload_field_schema(self):
        fti = queryUtility(IDexterityFTI, name='UploadField')
        schema = fti.lookupSchema()
        self.assertEqual(IUploadField, schema)

    def test_ct_upload_field_fti(self):
        fti = queryUtility(IDexterityFTI, name='UploadField')
        self.assertTrue(fti)

    def test_ct_upload_field_factory(self):
        fti = queryUtility(IDexterityFTI, name='UploadField')
        factory = fti.factory
        obj = createObject(factory)

        self.assertTrue(
            IUploadField.providedBy(obj),
            u'IUploadField not provided by {0}!'.format(
                obj,
            ),
        )

    def test_ct_upload_field_adding(self):
        setRoles(self.portal, TEST_USER_ID, ['Contributor'])
        obj = api.content.create(
            container=self.parent,
            type='UploadField',
            id='upload_field',
        )

        self.assertTrue(
            IUploadField.providedBy(obj),
            u'IUploadField not provided by {0}!'.format(
                obj.id,
            ),
        )

        parent = obj.__parent__
        self.assertIn('upload_field', parent.objectIds())

        # check that deleting the object works too
        api.content.delete(obj=obj)
        self.assertNotIn('upload_field', parent.objectIds())

    def test_ct_upload_field_globally_not_addable(self):
        setRoles(self.portal, TEST_USER_ID, ['Contributor'])
        fti = queryUtility(IDexterityFTI, name='UploadField')
        self.assertFalse(
            fti.global_allow,
            u'{0} is globally addable!'.format(fti.id)
        )
