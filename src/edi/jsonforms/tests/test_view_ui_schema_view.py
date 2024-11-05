# -*- coding: utf-8 -*-
from edi.jsonforms.testing import EDI_JSONFORMS_FUNCTIONAL_TESTING
from edi.jsonforms.testing import EDI_JSONFORMS_INTEGRATION_TESTING
from plone import api
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from zope.component import getMultiAdapter
from zope.interface.interfaces import ComponentLookupError

import json
import unittest

from edi.jsonforms.tests.utils._test_schema_views import test_json_schema_view_is_registered, test_json_schema_view_not_matching_interface, setUp_integration_test, setUp_ui_schema_test
import edi.jsonforms.tests.utils.reference_schemata as reference_schemata
from edi.jsonforms.content.field import Answer_types
from edi.jsonforms.content.selection_field import Selection_answer_types
from edi.jsonforms.content.upload_field import Upload_answer_types
from edi.jsonforms.views.common import create_id




class ViewsIntegrationTest(unittest.TestCase):

    layer = EDI_JSONFORMS_INTEGRATION_TESTING
    ids = {}

    def setUp(self):
        setUp_integration_test(self)

    def test_ui_schema_view_is_registered(self):
        test_json_schema_view_is_registered(self, 'ui-schema-view')

    def test_ui_schema_view_not_matching_interface(self):
        test_json_schema_view_not_matching_interface(self, 'ui-schema-view')

class ViewsUiSchemaPlainFormTest(unittest.TestCase):
    layer = EDI_JSONFORMS_INTEGRATION_TESTING
    form = None
    view = None

    def setUp(self):
        setUp_ui_schema_test(self)

    def test_plain_form(self):
        ref_schema = reference_schemata.get_form_ref_schema_ui()
        computed_schema = json.loads(self.view())
        self.assertEqual(ref_schema, dict(computed_schema))

class ViewsUiSchemaFormWithChildrenTest(unittest.TestCase):
    layer = EDI_JSONFORMS_INTEGRATION_TESTING
    form = None
    view = None

    def _test_schema(self, ref_schema):
        computed_schema = json.loads(self.view())
        self.assertEqual(dict(computed_schema), dict(ref_schema))

    def setUp(self):
        setUp_ui_schema_test(self)

    def create_and_test_children(self, ref_schema, elements, container, content_type, answer_types, base_scope):
        for t in answer_types:
            t = t.value
            field = api.content.create(type=content_type, title=t + "_field", container=container)
            field.answer_type = t

            scope = base_scope + create_id(field)
            child_schema = reference_schemata.get_child_ref_schema_ui(t, scope)
            elements = reference_schemata.insert_into_elements(elements, child_schema)

            self._test_schema(ref_schema)


    def test_fields_in_form(self):
        ref_schema = reference_schemata.get_form_ref_schema_ui()
        self.create_and_test_children(ref_schema, ref_schema['layout']['elements'], self.form, "Field", Answer_types, "/properties/")

    def test_selectionfields_in_form(self):
        ref_schema = reference_schemata.get_form_ref_schema_ui()
        self.create_and_test_children(ref_schema, ref_schema['layout']['elements'], self.form, "SelectionField", Selection_answer_types, "/properties/")
        for sf in self.form.getFolderContents():
            sf = sf.getObject()
            api.content.create(type="Option", title="opt_" + sf.answer_type, container=sf)
        self._test_schema(ref_schema)

    def test_uploadfields_in_form(self):
        ref_schema = reference_schemata.get_form_ref_schema_ui()
        self.create_and_test_children(ref_schema, ref_schema['layout']['elements'], self.form, "UploadField", Upload_answer_types, "/properties/")

            
















# class ViewsFunctionalTest(unittest.TestCase):

#     layer = EDI_JSONFORMS_FUNCTIONAL_TESTING

#     def setUp(self):
#         self.portal = self.layer['portal']
#         setRoles(self.portal, TEST_USER_ID, ['Manager'])












class ShowOnPropertiesTest(unittest.TestCase):
    layer = EDI_JSONFORMS_INTEGRATION_TESTING
    view = None
    form = None

    def _test_showon_properties(self, ref_schema):
        computed_schema = json.loads(self.view())['properties']

    def setUp(self):
        setUp_ui_schema_test(self)
        # self.field = api.content.create(type="Field", title="a field", container=self.form)

    def test_textlike_showon_properties(self):
        pass