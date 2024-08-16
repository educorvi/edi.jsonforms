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
from edi.jsonforms.content.field import Answer_types
from edi.jsonforms.views.common import create_id


class ViewsIntegrationTest(unittest.TestCase):

    layer = EDI_JSONFORMS_INTEGRATION_TESTING
    ids = {}

    def setUp(self):
        setUpTests(self)

    def test_json_schema_view_is_registered(self):
        test_json_schema_view_is_registered(self, "json-schema-view")

    def test_json_schema_view_not_matching_interface(self):
        test_json_schema_view_not_matching_interface(self, "json-schema-view")

class ViewsJsonSchemaPlainFormTest(unittest.TestCase):

    layer = EDI_JSONFORMS_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        self.request = self.layer['request']
        setRoles(self.portal, TEST_USER_ID, ['Manager'])
        api.content.create(self.portal, "Form", "Fragebogen")

    def test_plain_form(self):
        view = api.content.get_view(
            name="json-schema-view",
            context=self.portal['Fragebogen'],
            request=self.request,
        )
        self.assertEqual('{"type": "object", "title": "", "properties": {}, "required": [], "dependentRequired": {}}', view())

    def test_plain_form2(self):
        self.portal['Fragebogen'].title = "A Title"
        self.portal['Fragebogen'].description = "A Description"
        view = api.content.get_view(
            name="json-schema-view",
            context=self.portal['Fragebogen'],
            request=self.request,
        )
        self.assertEqual('{"type": "object", "title": "A Title", "properties": {}, "required": [], "dependentRequired": {}, "description": "A Description"}', view())

class ViewsJsonSchemaFormWithFieldTest(unittest.TestCase):

    layer = EDI_JSONFORMS_INTEGRATION_TESTING
    field = None
    view = None

    def _test_field_schema(self, ref_schema):
        computed_schema = json.loads(self.view())['properties']
        self.assertEqual(dict(computed_schema), dict(ref_schema))

    def _test_textlike_fields(self):
        # should not change the schema
        self.field.placeholder = "a placeholder"

        ref_schema = {create_id(self.field): {"title": "a field", "type": "string"}}
        self._test_field_schema(ref_schema)

        self.field.minimum = 3
        ref_schema = {create_id(self.field): {"title": "a field", "type": "string", "minLength": 3}}
        self._test_field_schema(ref_schema)

        self.field.minimum = None
        self.field.maximum = 5
        ref_schema = {create_id(self.field): {"title": "a field", "type": "string", "maxLength": 5}}
        self._test_field_schema(ref_schema)

        self.field.minimum = 3
        ref_schema = {create_id(self.field): {"title": "a field", "type": "string", "minLength": 3, "maxLength": 5}}
        self._test_field_schema(ref_schema)

    def _test_numberlike_fields(self, type):
        # should not change the schema
        self.field.unit = "a unit"

        ref_schema = {create_id(self.field): {"title": "a field", "type": type}}
        self._test_field_schema(ref_schema)

        self.field.minimum = 3
        ref_schema = {create_id(self.field): {"title": "a field", "type": type, "minimum": 3}}
        self._test_field_schema(ref_schema)

        self.field.minimum = None
        self.field.maximum = 5
        ref_schema = {create_id(self.field): {"title": "a field", "type": type, "maximum": 5}}
        self._test_field_schema(ref_schema)

        self.field.minimum = 3
        ref_schema = {create_id(self.field): {"title": "a field", "type": type, "minimum": 3, "maximum": 5}}
        self._test_field_schema(ref_schema)

    def setUp(self):
        self.portal = self.layer['portal']
        self.request = self.layer['request']
        setRoles(self.portal, TEST_USER_ID, ['Manager'])
        form = api.content.create(self.portal, "Form", "Fragebogen")
        self.field = api.content.create(type="Field", title="a field", container=form)
        # field_id = str(field.id)
        # field_uid = str(field.UID())
        self.view = api.content.get_view(
            name="json-schema-view",
            context=self.portal['Fragebogen'],
            request=self.request,
        )


    def test_text_field(self):
        self.field.answer_type = "text"
        self._test_textlike_fields()

    def test_textarea_field(self):
        self.field.answer_type = "textarea"
        self._test_textlike_fields()

    def test_password_field(self):
        self.field.answer_type = "password"
        self._test_textlike_fields()

    def test_tel_field(self):
        self.field.answer_type = "tel"
        self.field.placeholder = "a placeholder phone number"   # should not change the schema

        ref_schema = {create_id(self.field): {"title": "a field", "type": "string", "pattern": "^\\+?(\\d{1,3})?[-.\\s]?(\\(?\\d{1,4}\\)?)?[-.\\s]?\\d{1,4}[-.\\s]?\\d{1,4}[-.\\s]?\\d{1,9}$"}}
        self._test_field_schema(ref_schema)

    def test_url_field(self):
        self.field.answer_type = "url"
        self.field.placeholder = "a placeholder url"        # should not change the schema

        ref_schema = {create_id(self.field): {"title": "a field", "type": "string", "format": "hostname"}}
        self._test_field_schema(ref_schema)

    def test_email_field(self):
        self.field.answer_type = "email"
        self.field.placeholder = "a placeholder email"        # should not change the schema

        ref_schema = {create_id(self.field): {"title": "a field", "type": "string", "format": "email"}}
        self._test_field_schema(ref_schema)

    def test_date_field(self):
        self.field.answer_type = "date"
        
        ref_schema = {create_id(self.field): {"title": "a field", "type": "string", "format": "date"}}
        self._test_field_schema(ref_schema)

    def test_datetimelocal_field(self):
        self.field.answer_type = "datetime-local"

        ref_schema = {create_id(self.field): {"title": "a field", "type": "string", "format": "date-time"}}
        self._test_field_schema(ref_schema)

    def test_time_field(self):
        self.field.answer_type = "time"

        ref_schema = {create_id(self.field): {"title": "a field", "type": "string", "format": "time"}}
        self._test_field_schema(ref_schema)

    def test_number_field(self):
        self.field.answer_type = "number"
        self._test_numberlike_fields("number")

    def test_integer_field(self):
        self.field.answer_type = "integer"
        self._test_numberlike_fields("integer")

    def test_boolean_field(self):
        self.field.answer_type = "boolean"

        ref_schema = {create_id(self.field): {"title": "a field", "type": "boolean"}}
        self._test_field_schema(ref_schema)

    def test_additional_attributes(self):
        # should not change the schema
        self.field.user_helptext = "a tipp"
        field_id = create_id(self.field)

        for type in Answer_types:
            ref_schema = {"title": "a field", "type": "string"}
            self.field.answer_type = type.value

            if type.value == "tel":
                ref_schema["pattern"] = "^\\+?(\\d{1,3})?[-.\\s]?(\\(?\\d{1,4}\\)?)?[-.\\s]?\\d{1,4}[-.\\s]?\\d{1,4}[-.\\s]?\\d{1,9}$"
            elif type.value == "url":
                ref_schema["format"] = "hostname"
            elif type.value == "email":
                ref_schema["format"] = "email"
            elif type.value == "date":
                ref_schema["format"] = "date"
            elif type.value == "datetime-local":
                ref_schema["format"] = "date-time"
            elif type.value == "time":
                ref_schema["format"] = "time"
            elif type.value == "number":
                ref_schema["type"] = "number"
            elif type.value == "integer":
                ref_schema["type"] = "integer"
            elif type.value in "boolean":
                ref_schema["type"] = "boolean"
            elif type.value not in ["text", "textarea", "password"]:
                assert False

            ref_schema = {field_id: ref_schema}

            self.field.description = "a description"
            ref_schema[field_id]["description"] = "a description"
            self._test_field_schema(ref_schema)

            self.field.intern_information = "an extra info"
            ref_schema[field_id]["comment"] = "an extra info"
            self._test_field_schema(ref_schema)

            self.field.description = None
            del ref_schema[field_id]['description']
            self._test_field_schema(ref_schema)

            self.field.intern_information = None


class ViewsJsonSchemaFormRequiredTest(unittest.TestCase):
    layer = EDI_JSONFORMS_INTEGRATION_TESTING
    view = None
    form = None

    def setUp(self):
        self.portal = self.layer['portal']
        self.request = self.layer['request']
        setRoles(self.portal, TEST_USER_ID, ['Manager'])
        self.form = api.content.create(self.portal, "Form", "Fragebogen")
        self.field = api.content.create(type="Field", title="a field", container=self.form)







# class ViewsFunctionalTest(unittest.TestCase):

#     layer = EDI_JSONFORMS_FUNCTIONAL_TESTING

#     def setUp(self):
#         self.portal = self.layer['portal']
#         setRoles(self.portal, TEST_USER_ID, ['Manager'])
