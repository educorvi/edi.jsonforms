# -*- coding: utf-8 -*-
from edi.jsonforms.content.selection_field import ISelectionField  # NOQA E501
from edi.jsonforms.testing import EDI_JSONFORMS_INTEGRATION_TESTING  # noqa
from plone import api
from plone.api.exc import InvalidParameterError
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from plone.dexterity.interfaces import IDexterityFTI
from zope.component import createObject
from zope.component import queryUtility

import unittest




class SelectionFieldIntegrationTest(unittest.TestCase):

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

    def test_ct_selection_field_schema(self):
        fti = queryUtility(IDexterityFTI, name='SelectionField')
        schema = fti.lookupSchema()
        self.assertEqual(ISelectionField, schema)

    def test_ct_selection_field_fti(self):
        fti = queryUtility(IDexterityFTI, name='SelectionField')
        self.assertTrue(fti)

    def test_ct_selection_field_factory(self):
        fti = queryUtility(IDexterityFTI, name='SelectionField')
        factory = fti.factory
        obj = createObject(factory)

        self.assertTrue(
            ISelectionField.providedBy(obj),
            u'ISelectionField not provided by {0}!'.format(
                obj,
            ),
        )

    def test_ct_selection_field_adding(self):
        setRoles(self.portal, TEST_USER_ID, ['Contributor'])
        obj = api.content.create(
            container=self.parent,
            type='SelectionField',
            id='selection_field',
        )

        self.assertTrue(
            ISelectionField.providedBy(obj),
            u'ISelectionField not provided by {0}!'.format(
                obj.id,
            ),
        )

        parent = obj.__parent__
        self.assertIn('selection_field', parent.objectIds())

        # check that deleting the object works too
        api.content.delete(obj=obj)
        self.assertNotIn('selection_field', parent.objectIds())

    def test_ct_selection_field_globally_not_addable(self):
        setRoles(self.portal, TEST_USER_ID, ['Contributor'])
        fti = queryUtility(IDexterityFTI, name='SelectionField')
        self.assertFalse(
            fti.global_allow,
            u'{0} is globally addable!'.format(fti.id)
        )

    def test_ct_selection_field_filter_content_type_true(self):
        setRoles(self.portal, TEST_USER_ID, ['Contributor'])
        fti = queryUtility(IDexterityFTI, name='SelectionField')
        portal_types = self.portal.portal_types
        parent_id = portal_types.constructContent(
            fti.id,
            self.portal,
            'selection_field_id',
            title='SelectionField container',
         )
        self.parent = self.portal[parent_id]
        with self.assertRaises(InvalidParameterError):
            api.content.create(
                container=self.parent,
                type='Document',
                title='My Content',
            )
