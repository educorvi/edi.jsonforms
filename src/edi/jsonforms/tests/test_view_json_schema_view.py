# -*- coding: utf-8 -*-
from edi.jsonforms.testing import EDI_JSONFORMS_FUNCTIONAL_TESTING
from edi.jsonforms.testing import EDI_JSONFORMS_INTEGRATION_TESTING
from plone import api
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
# from zope.component import getMultiAdapter
# from zope.interface.interfaces import ComponentLookupError

import json
import unittest

from edi.jsonforms.tests._test_schema_views import test_json_schema_view_is_registered, test_json_schema_view_not_matching_interface, setUp as setUpTests
from edi.jsonforms.views.common import create_id


class ViewsIntegrationTest(unittest.TestCase):

    layer = EDI_JSONFORMS_INTEGRATION_TESTING
    ids = {}

    def setUp(self):
        setUpTests(self)

    def test_json_schema_view_is_registered(self):
        test_json_schema_view_is_registered(self, 'json-schema-view')

    def test_json_schema_view_not_matching_interface(self):
        test_json_schema_view_not_matching_interface(self, 'json-schema-view')

class ViewsJsonSchemaPlainFormTest(unittest.TestCase):

    layer = EDI_JSONFORMS_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        self.request = self.layer['request']
        setRoles(self.portal, TEST_USER_ID, ['Manager'])
        api.content.create(self.portal, 'Form', 'Fragebogen')

    def test_plain_form(self):
        view = api.content.get_view(
            name='json-schema-view',
            context=self.portal['Fragebogen'],
            request=self.request,
        )
        self.assertEqual('{"type": "object", "title": "", "properties": {}, "required": [], "dependentRequired": {}}', view())

    def test_plain_form2(self):
        self.portal['Fragebogen'].title = "A Title"
        self.portal['Fragebogen'].description = "A Description"
        view = api.content.get_view(
            name='json-schema-view',
            context=self.portal['Fragebogen'],
            request=self.request,
        )
        self.assertEqual('{"type": "object", "title": "A Title", "properties": {}, "required": [], "dependentRequired": {}, "description": "A Description"}', view())

class ViewsJsonSchemaFormWithFieldTest(unittest.TestCase):

    layer = EDI_JSONFORMS_INTEGRATION_TESTING
    field = None
    view = None

    def load_field_schema(self):
        return json.loads(self.view())['properties']

    def setUp(self):
        self.portal = self.layer['portal']
        self.request = self.layer['request']
        setRoles(self.portal, TEST_USER_ID, ['Manager'])
        form = api.content.create(self.portal, 'Form', 'Fragebogen')
        self.field = api.content.create(type='Field', title='a field', container=form)
        # field_id = str(field.id)
        # field_uid = str(field.UID())
        self.view = api.content.get_view(
            name='json-schema-view',
            context=self.portal['Fragebogen'],
            request=self.request,
        )

    def _test_textlike_fields(self):
        # should not change the schema
        self.field.placeholder = "a placeholder"

        computed_schema = self.load_field_schema()
        ref_schema = {create_id(self.field): {"title": "a field", "type": "string"}}
        self.assertEqual(str(computed_schema), str(ref_schema))

        self.field.minimum = 3
        computed_schema = self.load_field_schema()
        ref_schema = {create_id(self.field): {"title": "a field", "type": "string", "minLength": 3}}
        self.assertEqual(str(computed_schema), str(ref_schema))

        self.field.minimum = None
        self.field.maximum = 5
        computed_schema = self.load_field_schema()
        ref_schema = {create_id(self.field): {"title": "a field", "type": "string", "maxLength": 5}}
        self.assertEqual(str(computed_schema), str(ref_schema))

        self.field.minimum = 3
        computed_schema = self.load_field_schema()
        ref_schema = {create_id(self.field): {"title": "a field", "type": "string", "minLength": 3, "maxLength": 5}}
        self.assertEqual(str(computed_schema), str(ref_schema))

    def test_text_field(self):
        self.field.answer_type = 'text'
        self._test_textlike_fields()

    def test_textarea_field(self):
        self.field.answer_type = 'textarea'
        self._test_textlike_fields()

    def test_password_field(self):
        self.field.answer_type = 'password'
        self._test_textlike_fields()

    def test_tel_field(self):
        self.field.answer_type = 'tel'
        self.field.placeholder = "a placeholder phone number"   # should not change the schema

        computed_schema = self.load_field_schema()
        ref_schema = {create_id(self.field): {"title": "a field", "type": "string", "pattern": "^\\+?(\\d{1,3})?[-.\\s]?(\\(?\\d{1,4}\\)?)?[-.\\s]?\\d{1,4}[-.\\s]?\\d{1,4}[-.\\s]?\\d{1,9}$"}}
        self.assertEqual(str(computed_schema), str(ref_schema))

    def test_url_field(self):
        self.field.answer_type = 'url'
        self.field.placeholder = 'a placeholder url'        # should not change the schema

        computed_schema = self.load_field_schema()
        ref_schema = {create_id(self.field): {"title": "a field", "type": "string", "format": "hostname"}}
        self.assertEqual(str(computed_schema), str(ref_schema))








# class ViewsFunctionalTest(unittest.TestCase):

#     layer = EDI_JSONFORMS_FUNCTIONAL_TESTING

#     def setUp(self):
#         self.portal = self.layer['portal']
#         setRoles(self.portal, TEST_USER_ID, ['Manager'])
