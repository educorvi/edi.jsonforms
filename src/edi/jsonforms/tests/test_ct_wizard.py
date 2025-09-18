# -*- coding: utf-8 -*-
from edi.jsonforms.content.wizard import IWizard  # NOQA E501
from edi.jsonforms.testing import EDI_JSONFORMS_INTEGRATION_TESTING  # noqa
from plone import api
from plone.api.exc import InvalidParameterError
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from plone.dexterity.interfaces import IDexterityFTI
from zope.component import createObject
from zope.component import queryUtility

import unittest




class WizardIntegrationTest(unittest.TestCase):

    layer = EDI_JSONFORMS_INTEGRATION_TESTING

    def setUp(self):
        """Custom shared utility setup for tests."""
        self.portal = self.layer['portal']
        setRoles(self.portal, TEST_USER_ID, ['Manager'])
        self.parent = self.portal

    def test_ct_wizard_schema(self):
        fti = queryUtility(IDexterityFTI, name='Wizard')
        schema = fti.lookupSchema()
        self.assertEqual(IWizard, schema)

    def test_ct_wizard_fti(self):
        fti = queryUtility(IDexterityFTI, name='Wizard')
        self.assertTrue(fti)

    def test_ct_wizard_factory(self):
        fti = queryUtility(IDexterityFTI, name='Wizard')
        factory = fti.factory
        obj = createObject(factory)

        self.assertTrue(
            IWizard.providedBy(obj),
            u'IWizard not provided by {0}!'.format(
                obj,
            ),
        )

    def test_ct_wizard_adding(self):
        setRoles(self.portal, TEST_USER_ID, ['Contributor'])
        obj = api.content.create(
            container=self.portal,
            type='Wizard',
            id='wizard',
        )

        self.assertTrue(
            IWizard.providedBy(obj),
            u'IWizard not provided by {0}!'.format(
                obj.id,
            ),
        )

        parent = obj.__parent__
        self.assertIn('wizard', parent.objectIds())

        # check that deleting the object works too
        api.content.delete(obj=obj)
        self.assertNotIn('wizard', parent.objectIds())

    def test_ct_wizard_globally_addable(self):
        setRoles(self.portal, TEST_USER_ID, ['Contributor'])
        fti = queryUtility(IDexterityFTI, name='Wizard')
        self.assertTrue(
            fti.global_allow,
            u'{0} is not globally addable!'.format(fti.id)
        )

    def test_ct_wizard_filter_content_type_true(self):
        setRoles(self.portal, TEST_USER_ID, ['Contributor'])
        fti = queryUtility(IDexterityFTI, name='Wizard')
        portal_types = self.portal.portal_types
        parent_id = portal_types.constructContent(
            fti.id,
            self.portal,
            'wizard_id',
            title='Wizard container',
        )
        self.parent = self.portal[parent_id]
        with self.assertRaises(InvalidParameterError):
            api.content.create(
                container=self.parent,
                type='Document',
                title='My Content',
            )
