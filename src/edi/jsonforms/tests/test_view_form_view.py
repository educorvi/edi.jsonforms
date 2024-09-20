# -*- coding: utf-8 -*-
from edi.jsonforms.testing import EDI_JSONFORMS_FUNCTIONAL_TESTING
from edi.jsonforms.testing import EDI_JSONFORMS_INTEGRATION_TESTING
from plone import api
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from zope.component import getMultiAdapter
from zope.interface.interfaces import ComponentLookupError

import unittest

from edi.jsonforms.tests.utils._test_schema_views import test_json_schema_view_is_registered, test_json_schema_view_not_matching_interface, setUp_integration_test


class ViewsIntegrationTest(unittest.TestCase):

    layer = EDI_JSONFORMS_INTEGRATION_TESTING
    ids = {}

    def setUp(self):
        setUp_integration_test(self)

    def test_form_view_is_registered(self):
        test_json_schema_view_is_registered(self, 'form-view')  

    def test_form_view_not_matching_interface(self):
        test_json_schema_view_not_matching_interface(self, 'form-view')



class ViewsFunctionalTest(unittest.TestCase):

    layer = EDI_JSONFORMS_FUNCTIONAL_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        setRoles(self.portal, TEST_USER_ID, ['Manager'])
