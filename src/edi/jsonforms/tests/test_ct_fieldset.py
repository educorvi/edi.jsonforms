# -*- coding: utf-8 -*-
from edi.jsonforms.content.fieldset import IFieldset  # NOQA E501
from edi.jsonforms.testing import EDI_JSONFORMS_INTEGRATION_TESTING  # noqa
from plone import api
from plone.api.exc import InvalidParameterError
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from plone.dexterity.interfaces import IDexterityFTI
from zope.component import createObject
from zope.component import queryUtility

import unittest




class FieldsetIntegrationTest(unittest.TestCase):

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

    def test_ct_fieldset_schema(self):
        fti = queryUtility(IDexterityFTI, name='Fieldset')
        schema = fti.lookupSchema()
        self.assertEqual(IFieldset, schema)

    def test_ct_fieldset_fti(self):
        fti = queryUtility(IDexterityFTI, name='Fieldset')
        self.assertTrue(fti)

    def test_ct_fieldset_factory(self):
        fti = queryUtility(IDexterityFTI, name='Fieldset')
        factory = fti.factory
        obj = createObject(factory)

        self.assertTrue(
            IFieldset.providedBy(obj),
            u'IFieldset not provided by {0}!'.format(
                obj,
            ),
        )

    def test_ct_fieldset_adding(self):
        setRoles(self.portal, TEST_USER_ID, ['Contributor'])
        obj = api.content.create(
            container=self.parent,
            type='Fieldset',
            id='fieldset',
        )

        self.assertTrue(
            IFieldset.providedBy(obj),
            u'IFieldset not provided by {0}!'.format(
                obj.id,
            ),
        )

        parent = obj.__parent__
        self.assertIn('fieldset', parent.objectIds())

        # check that deleting the object works too
        api.content.delete(obj=obj)
        self.assertNotIn('fieldset', parent.objectIds())

    def test_ct_fieldset_globally_not_addable(self):
        setRoles(self.portal, TEST_USER_ID, ['Contributor'])
        fti = queryUtility(IDexterityFTI, name='Fieldset')
        self.assertFalse(
            fti.global_allow,
            u'{0} is globally addable!'.format(fti.id)
        )

    def test_ct_fieldset_filter_content_type_true(self):
        setRoles(self.portal, TEST_USER_ID, ['Contributor'])
        fti = queryUtility(IDexterityFTI, name='Fieldset')
        portal_types = self.portal.portal_types
        parent_id = portal_types.constructContent(
            fti.id,
            self.portal,
            'fieldset_id',
            title='Fieldset container',
         )
        self.parent = self.portal[parent_id]
        with self.assertRaises(InvalidParameterError):
            api.content.create(
                container=self.parent,
                type='Document',
                title='My Content',
            )
