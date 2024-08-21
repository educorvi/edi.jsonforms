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

from edi.jsonforms.tests._test_schema_views import test_json_schema_view_is_registered, test_json_schema_view_not_matching_interface, setUp_integration_test, setUp_json_schema_test
from edi.jsonforms.content.field import Answer_types
from edi.jsonforms.content.selection_field import Selection_answer_types
from edi.jsonforms.views.common import create_id



class ViewsIntegrationTest(unittest.TestCase):

    layer = EDI_JSONFORMS_INTEGRATION_TESTING
    ids = {}

    def setUp(self):
        setUp_integration_test(self)

    def test_json_schema_view_is_registered(self):
        test_json_schema_view_is_registered(self, "json-schema-view")

    def test_json_schema_view_not_matching_interface(self):
        test_json_schema_view_not_matching_interface(self, "json-schema-view")

class ViewsJsonSchemaPlainFormTest(unittest.TestCase):
    layer = EDI_JSONFORMS_INTEGRATION_TESTING
    form = None
    view = None

    def setUp(self):
        setUp_json_schema_test(self)

    def test_plain_form(self):
        self.assertEqual('{"type": "object", "title": "", "properties": {}, "required": [], "dependentRequired": {}}', self.view())

    def test_plain_form2(self):
        self.portal['Fragebogen'].title = "A Title"
        self.portal['Fragebogen'].description = "A Description"
        self.assertEqual('{"type": "object", "title": "A Title", "properties": {}, "required": [], "dependentRequired": {}, "description": "A Description"}', self.view())

class ViewsJsonSchemaFormWithFieldTest(unittest.TestCase):
    layer = EDI_JSONFORMS_INTEGRATION_TESTING
    form = None
    view = None
    field = None

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
        setUp_json_schema_test(self)
        self.field = api.content.create(type="Field", title="a field", container=self.form)

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

    def test_multiple_fields(self):
        field_id = create_id(self.field)
        self.field = []
        for type in Answer_types:
            f = api.content.create(type="Field", title=type.value + "field" + "0", container=self.form)
            f.answer_type = type.value
            self.field.append(f)

            f = api.content.create(type="Field", title=type.value + "field" + "1", container=self.form)
            f.answer_type = type.value
            self.field.append(f)
        
        ref_schema = {"type": "object", "title": "", "properties": {field_id: {"title": "a field", "type": "string"}, create_id(self.field[0]): {"title": "textfield0", "type": "string"}, create_id(self.field[1]): {"title": "textfield1", "type": "string"}, create_id(self.field[2]): {"title": "textareafield0", "type": "string"}, create_id(self.field[3]): {"title": "textareafield1", "type": "string"}, create_id(self.field[4]): {"title": "passwordfield0", "type": "string"}, create_id(self.field[5]): {"title": "passwordfield1", "type": "string"}, create_id(self.field[6]): {"title": "telfield0", "type": "string", "pattern": "^\\+?(\\d{1,3})?[-.\\s]?(\\(?\\d{1,4}\\)?)?[-.\\s]?\\d{1,4}[-.\\s]?\\d{1,4}[-.\\s]?\\d{1,9}$"}, create_id(self.field[7]): {"title": "telfield1", "type": "string", "pattern": "^\\+?(\\d{1,3})?[-.\\s]?(\\(?\\d{1,4}\\)?)?[-.\\s]?\\d{1,4}[-.\\s]?\\d{1,4}[-.\\s]?\\d{1,9}$"}, create_id(self.field[8]): {"title": "urlfield0", "type": "string", "format": "hostname"}, create_id(self.field[9]): {"title": "urlfield1", "type": "string", "format": "hostname"}, create_id(self.field[10]): {"title": "emailfield0", "type": "string", "format": "email"}, create_id(self.field[11]): {"title": "emailfield1", "type": "string", "format": "email"}, create_id(self.field[12]): {"title": "datefield0", "type": "string", "format": "date"}, create_id(self.field[13]): {"title": "datefield1", "type": "string", "format": "date"}, create_id(self.field[14]): {"title": "datetime-localfield0", "type": "string", "format": "date-time"}, create_id(self.field[15]): {"title": "datetime-localfield1", "type": "string", "format": "date-time"}, create_id(self.field[16]): {"title": "timefield0", "type": "string", "format": "time"}, create_id(self.field[17]): {"title": "timefield1", "type": "string", "format": "time"}, create_id(self.field[18]): {"title": "numberfield0", "type": "number"}, create_id(self.field[19]): {"title": "numberfield1", "type": "number"}, create_id(self.field[20]): {"title": "integerfield0", "type": "integer"}, create_id(self.field[21]): {"title": "integerfield1", "type": "integer"}, create_id(self.field[22]): {"title": "booleanfield0", "type": "boolean"}, create_id(self.field[23]): {"title": "booleanfield1", "type": "boolean"}}, "required": [], "dependentRequired": {}}

        computed_schema = json.loads(self.view())
        self.assertEqual(dict(computed_schema), dict(ref_schema))

class ViewsJsonSchemaFieldsRequiredTest(unittest.TestCase):
    layer = EDI_JSONFORMS_INTEGRATION_TESTING
    view = None
    form = None
    field = []
    selectionfield = []

    def _test_required(self, ref_required):
        computed_schema = {'required': json.loads(self.view())['required']}
        ref_schema = {'required': ref_required}
        self.assertEqual(dict(computed_schema), dict(ref_schema))

    def setUp(self):
        setUp_json_schema_test(self)
        answer_type = ["text", "number", "boolean"]
        self.field = []
        # self.selectionfield = []
        for i in range(3):
            self.field.append(api.content.create(type="Field", title="field" + str(i), container=self.form))
            self.field[i].answer_type = answer_type[i]

            # self.selectionfield.append(api.content.create(type="SelectionField", title="selectionfield" + str(i), container=self.form))

    def test_schema(self):
        computed_schema = json.loads(self.view())
        ref_schema = {"type": "object", "title": "", "properties": {create_id(self.field[0]): {"title": "field0", "type": "string"}, create_id(self.field[1]): {"title": "field1", "type": "number"}, create_id(self.field[2]): {"title": "field2", "type": "boolean"}}, "required": [], "dependentRequired": {}}

        self.assertEqual(dict(computed_schema), dict(ref_schema))

    def test_zero_field_required_choice(self):
        ref_required = []
        self._test_required(ref_required)

    def test_one_field_required_choice(self):
        self.field[0].required_choice = "required"
        ref_required = [create_id(self.field[0])]
        self._test_required(ref_required)

        self.field[0].required_choice = "optional"
        self.field[1].required_choice = "required"
        ref_required = [create_id(self.field[1])]
        self._test_required(ref_required)

        self.field[1].required_choice = "optional"
        self.field[2].required_choice = "required"
        ref_required = [create_id(self.field[2])]
        self._test_required(ref_required)

    def test_two_fields_required_choices(self):
        self.field[0].required_choice = "required"
        self.field[1].required_choice = "required"
        create_id(self.field[0])
        create_id(self.field[1])
        ref_required = [create_id(self.field[0]), create_id(self.field[1])]
        self._test_required(ref_required)

        self.field[0].required_choice = "optional"
        self.field[1].required_choice = "required"
        self.field[2].required_choice = "required"
        ref_required = [create_id(self.field[1]), create_id(self.field[2])]
        self._test_required(ref_required)

        self.field[1].required_choice = "optional"
        self.field[2].required_choice = "required"
        self.field[0].required_choice = "required"
        ref_required = [create_id(self.field[0]), create_id(self.field[2])]
        self._test_required(ref_required)

    def test_three_fields_required_choices(self):
        self.field[0].required_choice = "required"
        self.field[1].required_choice = "required"
        self.field[2].required_choice = "required"
        ref_required = [create_id(self.field[0]), create_id(self.field[1]), create_id(self.field[2])]
        self._test_required(ref_required)


class ViewsJsonSchemaFormWithSelectionFieldTest(unittest.TestCase):
    layer = EDI_JSONFORMS_INTEGRATION_TESTING
    view = None
    form = None
    selectionfield = None

    def _test_selectionfield_schema(self, ref_schema):
        computed_schema = json.loads(self.view())['properties']
        self.assertEqual(dict(computed_schema), dict(ref_schema))

    def setUp(self):
        setUp_json_schema_test(self)
        self.selectionfield = api.content.create(type="SelectionField", title="a selectionfield", container=self.form)

    def test_radio_selectionfield(self):
        f_id = create_id(self.selectionfield)
        self.selectionfield.answer_type = "radio"
        ref_schema = {create_id(self.selectionfield): {"title": "a selectionfield", "type": "string", "enum": []}}
        self._test_selectionfield_schema(ref_schema)

    def test_checkbox_selectionfield(self):
        self.selectionfield.answer_type = "checkbox"
        ref_schema = {create_id(self.selectionfield): {"title": "a selectionfield", "type": "array", "items": {"enum": [], "type": "string"}}}
        self._test_selectionfield_schema(ref_schema)

    def test_select_selectionfield(self):
        self.selectionfield.answer_type = "select"
        ref_schema = {create_id(self.selectionfield): {"title": "a selectionfield", "type": "string", "enum": []}}
        self._test_selectionfield_schema(ref_schema)

    def test_selectmultiple_selectionfield(self):
        self.selectionfield.answer_type = "selectmultiple"
        ref_schema = {create_id(self.selectionfield): {"title": "a selectionfield", "type": "array", "items": {"enum": [], "type": "string"}}}
        self._test_selectionfield_schema(ref_schema)





            


class ViewsJsonSchemaFormWithUploadFieldTest(unittest.TestCase):
    pass


class ViewsJsonSchemaFormWithArrayTest(unittest.TestCase):
    pass


class ViewsJsonSchemaFormWithComplexTest(unittest.TestCase):
    pass


class ViewsJsonSchemaFormWithFieldsetTest(unittest.TestCase):
    pass



class ViewsJsonSchemaDependentRequiredTest(unittest.TestCase):
    layer = EDI_JSONFORMS_INTEGRATION_TESTING
    view = None
    form = None
    field = []
    selectionfield = []

    # TODO first: unit test of add_dependent_required with every possible type (also array etc) -> think about what should happen if array is required





# class ViewsFunctionalTest(unittest.TestCase):

#     layer = EDI_JSONFORMS_FUNCTIONAL_TESTING

#     def setUp(self):
#         self.portal = self.layer['portal']
#         setRoles(self.portal, TEST_USER_ID, ['Manager'])
