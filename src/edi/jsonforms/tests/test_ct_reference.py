# -*- coding: utf-8 -*-
from edi.jsonforms.content.reference import IReference  # NOQA E501
from edi.jsonforms.testing import EDI_JSONFORMS_INTEGRATION_TESTING  # noqa
from plone import api
from plone.api.exc import InvalidParameterError
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from plone.dexterity.interfaces import IDexterityFTI
from zope.component import createObject
from zope.component import queryUtility

import unittest




class ReferenceIntegrationTest(unittest.TestCase):

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

    def test_ct_reference_schema(self):
        fti = queryUtility(IDexterityFTI, name='Reference')
        schema = fti.lookupSchema()
        self.assertEqual(IReference, schema)

    def test_ct_reference_fti(self):
        fti = queryUtility(IDexterityFTI, name='Reference')
        self.assertTrue(fti)

    def test_ct_reference_factory(self):
        fti = queryUtility(IDexterityFTI, name='Reference')
        factory = fti.factory
        obj = createObject(factory)

        self.assertTrue(
            IReference.providedBy(obj),
            u'IReference not provided by {0}!'.format(
                obj,
            ),
        )

    def test_ct_reference_adding(self):
        setRoles(self.portal, TEST_USER_ID, ['Contributor'])
        obj = api.content.create(
            container=self.parent,
            type='Reference',
            id='reference',
        )

        self.assertTrue(
            IReference.providedBy(obj),
            u'IReference not provided by {0}!'.format(
                obj.id,
            ),
        )

        parent = obj.__parent__
        self.assertIn('reference', parent.objectIds())

        # check that deleting the object works too
        api.content.delete(obj=obj)
        self.assertNotIn('reference', parent.objectIds())

    def test_ct_reference_globally_not_addable(self):
        setRoles(self.portal, TEST_USER_ID, ['Contributor'])
        fti = queryUtility(IDexterityFTI, name='Reference')
        self.assertFalse(
            fti.global_allow,
            u'{0} is globally addable!'.format(fti.id)
        )

    def test_ct_reference_filter_content_type_true(self):
        setRoles(self.portal, TEST_USER_ID, ['Contributor'])
        fti = queryUtility(IDexterityFTI, name='Reference')
        portal_types = self.portal.portal_types
        parent_id = portal_types.constructContent(
            fti.id,
            self.portal,
            'reference_id',
            title='Reference container',
        )
        self.parent = self.portal[parent_id]
        with self.assertRaises(InvalidParameterError):
            api.content.create(
                container=self.parent,
                type='Document',
                title='My Content',
            )
