from edi.jsonforms.testing import EDI_JSONFORMS_FUNCTIONAL_TESTING
from edi.jsonforms.testing import EDI_JSONFORMS_INTEGRATION_TESTING
from edi.jsonforms.tests._test_schema_views import setUp_integration_test
from edi.jsonforms.tests._test_schema_views import test_json_schema_view_is_registered
from edi.jsonforms.tests._test_schema_views import (
    test_json_schema_view_not_matching_interface,
)
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID

import unittest


class ViewsIntegrationTest(unittest.TestCase):
    layer = EDI_JSONFORMS_INTEGRATION_TESTING
    ids: dict

    def __init__(self):
        super().__init__()
        self.ids = {}

    def setUp(self):
        setUp_integration_test(self)

    def test_form_view_is_registered(self):
        test_json_schema_view_is_registered(self, "form-view")

    def test_form_view_not_matching_interface(self):
        test_json_schema_view_not_matching_interface(self, "form-view")


class ViewsFunctionalTest(unittest.TestCase):
    layer = EDI_JSONFORMS_FUNCTIONAL_TESTING

    def setUp(self):
        self.portal = self.layer["portal"]
        setRoles(self.portal, TEST_USER_ID, ["Manager"])
