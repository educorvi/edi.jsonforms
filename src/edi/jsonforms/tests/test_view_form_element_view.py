# -*- coding: utf-8 -*-
from edi.jsonforms.testing import EDI_JSONFORMS_FUNCTIONAL_TESTING
from edi.jsonforms.testing import EDI_JSONFORMS_INTEGRATION_TESTING
from edi.jsonforms.views.form_element_view import IFormElementView
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
        form = api.content.create(self.portal, "Form", "test-form")
        api.content.create(form, "Field", "test-field")

    def test_form_element_view_is_registered(self):
        view = getMultiAdapter(
            (self.portal["test-form"]["test-field"], self.portal.REQUEST),
            name="form-element-view",
        )
        self.assertTrue(
            IFormElementView.providedBy(view),
            msg="ComponentLookUpError should not happen when trying to apply the form-element-view to a Field.",
        )

    def test_form_element_view_not_matching_interface(self):
        view_found = True
        try:
            view = getMultiAdapter(
                (self.portal["test-form"], self.portal.REQUEST),
                name="form-element-view",
            )
        except ComponentLookupError:
            view_found = False
        else:
            view_found = IFormElementView.providedBy(view)
        self.assertFalse(view_found)


class ViewsFunctionalTest(unittest.TestCase):
    layer = EDI_JSONFORMS_FUNCTIONAL_TESTING

    def setUp(self):
        self.portal = self.layer["portal"]
        setRoles(self.portal, TEST_USER_ID, ["Manager"])
