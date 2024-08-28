# -*- coding: utf-8 -*-
from edi.jsonforms.content.complex import IComplex  # NOQA E501
from edi.jsonforms.testing import EDI_JSONFORMS_INTEGRATION_TESTING  # noqa
from plone import api
from plone.api.exc import InvalidParameterError
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from plone.dexterity.interfaces import IDexterityFTI
from zope.component import createObject
from zope.component import queryUtility

import unittest




class ComplexIntegrationTest(unittest.TestCase):

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

    def test_ct_complex_schema(self):
        fti = queryUtility(IDexterityFTI, name='Complex')
        schema = fti.lookupSchema()
        self.assertEqual(IComplex, schema)

    def test_ct_complex_fti(self):
        fti = queryUtility(IDexterityFTI, name='Complex')
        self.assertTrue(fti)

    def test_ct_complex_factory(self):
        fti = queryUtility(IDexterityFTI, name='Complex')
        factory = fti.factory
        obj = createObject(factory)

        self.assertTrue(
            IComplex.providedBy(obj),
            u'IComplex not provided by {0}!'.format(
                obj,
            ),
        )

    def test_ct_complex_adding(self):
        setRoles(self.portal, TEST_USER_ID, ['Contributor'])
        obj = api.content.create(
            container=self.parent,
            type='Complex',
            id='complex',
        )

        self.assertTrue(
            IComplex.providedBy(obj),
            u'IComplex not provided by {0}!'.format(
                obj.id,
            ),
        )

        parent = obj.__parent__
        self.assertIn('complex', parent.objectIds())

        # check that deleting the object works too
        api.content.delete(obj=obj)
        self.assertNotIn('complex', parent.objectIds())

    def test_ct_complex_globally_not_addable(self):
        setRoles(self.portal, TEST_USER_ID, ['Contributor'])
        fti = queryUtility(IDexterityFTI, name='Complex')
        self.assertFalse(
            fti.global_allow,
            u'{0} is globally addable!'.format(fti.id)
        )

    def test_ct_complex_filter_content_type_true(self):
        setRoles(self.portal, TEST_USER_ID, ['Contributor'])
        fti = queryUtility(IDexterityFTI, name='Complex')
        portal_types = self.portal.portal_types
        parent_id = portal_types.constructContent(
            fti.id,
            self.portal,
            'complex_id',
            title='Complex container',
         )
        self.parent = self.portal[parent_id]
        with self.assertRaises(InvalidParameterError):
            api.content.create(
                container=self.parent,
                type='Document',
                title='My Content',
            )
