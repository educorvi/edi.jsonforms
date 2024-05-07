# -*- coding: utf-8 -*-
from edi.jsonforms.content.field import IField  # NOQA E501
from edi.jsonforms.testing import EDI_JSONFORMS_INTEGRATION_TESTING  # noqa
from plone import api
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from plone.dexterity.interfaces import IDexterityFTI
from zope.component import createObject
from zope.component import queryUtility

import unittest




class FieldIntegrationTest(unittest.TestCase):

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

    def test_ct_field_schema(self):
        fti = queryUtility(IDexterityFTI, name='Field')
        schema = fti.lookupSchema()
        self.assertEqual(IField, schema)

    def test_ct_field_fti(self):
        fti = queryUtility(IDexterityFTI, name='Field')
        self.assertTrue(fti)

    def test_ct_field_factory(self):
        fti = queryUtility(IDexterityFTI, name='Field')
        factory = fti.factory
        obj = createObject(factory)

        self.assertTrue(
            IField.providedBy(obj),
            u'IField not provided by {0}!'.format(
                obj,
            ),
        )

    def test_ct_field_adding(self):
        setRoles(self.portal, TEST_USER_ID, ['Contributor'])
        obj = api.content.create(
            container=self.parent,
            type='Field',
            id='field',
        )

        self.assertTrue(
            IField.providedBy(obj),
            u'IField not provided by {0}!'.format(
                obj.id,
            ),
        )

        parent = obj.__parent__
        self.assertIn('field', parent.objectIds())

        # check that deleting the object works too
        api.content.delete(obj=obj)
        self.assertNotIn('field', parent.objectIds())

    def test_ct_field_globally_not_addable(self):
        setRoles(self.portal, TEST_USER_ID, ['Contributor'])
        fti = queryUtility(IDexterityFTI, name='Field')
        self.assertFalse(
            fti.global_allow,
            u'{0} is globally addable!'.format(fti.id)
        )
