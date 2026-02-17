# -*- coding: utf-8 -*-
from edi.jsonforms.testing import EDI_JSONFORMS_FUNCTIONAL_TESTING
from edi.jsonforms.testing import EDI_JSONFORMS_INTEGRATION_TESTING
from edi.jsonforms.views.wizard_view import IWizardView
from plone import api
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from zope.component import getMultiAdapter
from zope.interface.interfaces import ComponentLookupError

import unittest


class ViewsIntegrationTest(unittest.TestCase):
    layer = EDI_JSONFORMS_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer["portal"]
        setRoles(self.portal, TEST_USER_ID, ["Manager"])
        api.content.create(self.portal, "Wizard", "test-wizard")
        api.content.create(self.portal, "Form", "test-form")

    def test_wizard_view_is_registered(self):
        view = getMultiAdapter(
            (self.portal["test-wizard"], self.portal.REQUEST), name="wizard-view"
        )
        self.assertTrue(
            IWizardView.providedBy(view),
            msg="ComponentLookUpError should not happen when trying to apply the wizard-view to a Wizard.",
        )

    def test_wizard_view_not_matching_interface(self):
        view_found = True
        try:
            view = getMultiAdapter(
                (self.portal["test-form"], self.portal.REQUEST),
                name="wizard-view",
            )
        except ComponentLookupError:
            view_found = False
        else:
            view_found = IWizardView.providedBy(view)
        self.assertFalse(view_found)


class ViewsFunctionalTest(unittest.TestCase):
    layer = EDI_JSONFORMS_FUNCTIONAL_TESTING

    def setUp(self):
        self.portal = self.layer["portal"]
        setRoles(self.portal, TEST_USER_ID, ["Manager"])
