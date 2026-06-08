# -*- coding: utf-8 -*-
from edi.jsonforms.content.helptext_modal import IHelptextModal  # NOQA E501
from edi.jsonforms.testing import EDI_JSONFORMS_INTEGRATION_TESTING  # noqa
from plone import api
from plone.api.exc import InvalidParameterError
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from plone.dexterity.interfaces import IDexterityFTI
from zope.component import createObject
from zope.component import queryUtility

import unittest




class HelptextModalIntegrationTest(unittest.TestCase):

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

    def test_ct_helptext_modal_schema(self):
        fti = queryUtility(IDexterityFTI, name='Helptext Modal')
        schema = fti.lookupSchema()
        self.assertEqual(IHelptextModal, schema)

    def test_ct_helptext_modal_fti(self):
        fti = queryUtility(IDexterityFTI, name='Helptext Modal')
        self.assertTrue(fti)

    def test_ct_helptext_modal_factory(self):
        fti = queryUtility(IDexterityFTI, name='Helptext Modal')
        factory = fti.factory
        obj = createObject(factory)

        self.assertTrue(
            IHelptextModal.providedBy(obj),
            u'IHelptextModal not provided by {0}!'.format(
                obj,
            ),
        )

    def test_ct_helptext_modal_adding(self):
        setRoles(self.portal, TEST_USER_ID, ['Contributor'])
        obj = api.content.create(
            container=self.parent,
            type='Helptext Modal',
            id='helptext_modal',
        )

        self.assertTrue(
            IHelptextModal.providedBy(obj),
            u'IHelptextModal not provided by {0}!'.format(
                obj.id,
            ),
        )

        parent = obj.__parent__
        self.assertIn('helptext_modal', parent.objectIds())

        # check that deleting the object works too
        api.content.delete(obj=obj)
        self.assertNotIn('helptext_modal', parent.objectIds())

    def test_ct_helptext_modal_globally_not_addable(self):
        setRoles(self.portal, TEST_USER_ID, ['Contributor'])
        fti = queryUtility(IDexterityFTI, name='Helptext Modal')
        self.assertFalse(
            fti.global_allow,
            u'{0} is globally addable!'.format(fti.id)
        )

    def test_ct_helptext_modal_filter_content_type_true(self):
        setRoles(self.portal, TEST_USER_ID, ['Contributor'])
        fti = queryUtility(IDexterityFTI, name='Helptext Modal')
        portal_types = self.portal.portal_types
        parent_id = portal_types.constructContent(
            fti.id,
            self.portal,
            'helptext_modal_id',
            title='Helptext Modal container',
        )
        self.parent = self.portal[parent_id]
        with self.assertRaises(InvalidParameterError):
            api.content.create(
                container=self.parent,
                type='Document',
                title='My Content',
            )
