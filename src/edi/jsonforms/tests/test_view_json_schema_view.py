# -*- coding: utf-8 -*-
from edi.jsonforms.testing import EDI_JSONFORMS_FUNCTIONAL_TESTING
from edi.jsonforms.testing import EDI_JSONFORMS_INTEGRATION_TESTING
from plone import api
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from zope.interface.exceptions import Invalid
# from zope.component import getMultiAdapter
# from zope.interface.interfaces import ComponentLookupError

import copy
import json
import unittest

from edi.jsonforms.content.field import Answer_types
from edi.jsonforms.content.field import IField
from edi.jsonforms.content.selection_field import Selection_answer_types
from edi.jsonforms.content.upload_field import Upload_answer_types
from edi.jsonforms.views.common import create_id

import edi.jsonforms.tests.utils.reference_schemata as reference_schemata
import edi.jsonforms.tests.utils.create_content as test_content
from edi.jsonforms.tests.utils._test_required_choice import test_required_choices, test_object_required, test_object_not_required, test_object_children_required
from edi.jsonforms.tests.utils._test_schema_views import test_json_schema_view_is_registered, test_json_schema_view_not_matching_interface, setUp_integration_test, setUp_json_schema_test




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
        ref_schema = reference_schemata.get_form_ref_schema("")
        computed_schema = json.loads(self.view())
        self.assertEqual(ref_schema, dict(computed_schema))

    def test_plain_form2(self):
        self.portal['Fragebogen'].title = "a form"
        self.portal['Fragebogen'].description = "a description"
        ref_schema = reference_schemata.get_form_ref_schema()
        ref_schema['description'] = "a description"
        computed_schema = json.loads(self.view())
        self.assertEqual(ref_schema, dict(computed_schema))

class ViewsJsonSchemaFormWithFieldTest(unittest.TestCase):
    layer = EDI_JSONFORMS_INTEGRATION_TESTING
    form = None
    view = None
    field = None

    def _test_field_schema(self, ref_schema):
        computed_schema = json.loads(self.view())['properties']
        self.assertEqual(dict(computed_schema), dict(ref_schema))

    def _test_textlike_fields(self, type):
        # should not change the schema
        self.field.placeholder = "a placeholder"

        field_id = create_id(self.field)
        ref_schema = {field_id: reference_schemata.get_field_ref_schema(type)}
        self._test_field_schema(ref_schema)

        self.field.minimum = 3
        ref_schema[field_id]['minLength'] = 3
        self._test_field_schema(ref_schema)

        self.field.minimum = None
        self.field.maximum = 5
        del ref_schema[field_id]['minLength']
        ref_schema[field_id]['maxLength'] = 5
        self._test_field_schema(ref_schema)

        self.field.minimum = 3
        ref_schema[field_id]['minLength'] = 3
        self._test_field_schema(ref_schema)

    def _test_numberlike_fields(self, type):
        # should not change the schema
        self.field.unit = "a unit"

        field_id = create_id(self.field)
        ref_schema = {field_id: reference_schemata.get_field_ref_schema(type)}
        self._test_field_schema(ref_schema)

        self.field.minimum = 3
        ref_schema[field_id]['minimum'] = 3
        self._test_field_schema(ref_schema)

        self.field.minimum = None
        self.field.maximum = 5
        del ref_schema[field_id]['minimum']
        ref_schema[field_id]['maximum'] = 5
        self._test_field_schema(ref_schema)

        self.field.minimum = 3
        ref_schema[field_id]['minimum'] = 3
        self._test_field_schema(ref_schema)

    def setUp(self):
        setUp_json_schema_test(self)
        self.field = api.content.create(type="Field", title="a field", container=self.form)


    def test_text_field(self):
        self.field.answer_type = "text"
        self._test_textlike_fields("text")

    def test_textarea_field(self):
        self.field.answer_type = "textarea"
        self._test_textlike_fields("textarea")

    def test_password_field(self):
        self.field.answer_type = "password"
        self._test_textlike_fields("password")

    def test_tel_field(self):
        self.field.answer_type = "tel"
        self.field.placeholder = "a placeholder phone number"   # should not change the schema

        ref_schema = {create_id(self.field): reference_schemata.get_field_ref_schema("tel")}
        self._test_field_schema(ref_schema)

    def test_url_field(self):
        self.field.answer_type = "url"
        self.field.placeholder = "a placeholder url"        # should not change the schema

        ref_schema = {create_id(self.field): reference_schemata.get_field_ref_schema("url")}
        self._test_field_schema(ref_schema)

    def test_email_field(self):
        self.field.answer_type = "email"
        self.field.placeholder = "a placeholder email"        # should not change the schema

        ref_schema = {create_id(self.field): reference_schemata.get_field_ref_schema("email")}
        self._test_field_schema(ref_schema)

    def test_date_field(self):
        self.field.answer_type = "date"
        
        ref_schema = {create_id(self.field): reference_schemata.get_field_ref_schema("date")}
        self._test_field_schema(ref_schema)

    def test_datetimelocal_field(self):
        self.field.answer_type = "datetime-local"

        ref_schema = {create_id(self.field): reference_schemata.get_field_ref_schema("datetime-local")}
        self._test_field_schema(ref_schema)

    def test_time_field(self):
        self.field.answer_type = "time"

        ref_schema = {create_id(self.field): reference_schemata.get_field_ref_schema("time")}
        self._test_field_schema(ref_schema)

    def test_number_field(self):
        self.field.answer_type = "number"
        self._test_numberlike_fields("number")

    def test_integer_field(self):
        self.field.answer_type = "integer"
        self._test_numberlike_fields("integer")

    def test_boolean_field(self):
        self.field.answer_type = "boolean"

        ref_schema = {create_id(self.field): reference_schemata.get_field_ref_schema("boolean")}
        self._test_field_schema(ref_schema)

    def test_additional_attributes(self):
        # should not change the schema
        self.field.user_helptext = "a tipp"
        field_id = create_id(self.field)

        for type in Answer_types:
            type = type.value
            self.field.answer_type = type

            ref_schema = {field_id: reference_schemata.get_field_ref_schema(type)}

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
            del ref_schema[field_id]['comment']

    def test_multiple_fields(self):
        field_id = create_id(self.field)
        ref_schema = reference_schemata.get_form_ref_schema("")
        ref_schema['properties'][create_id(self.field)] = reference_schemata.get_field_ref_schema(self.field.answer_type)
        self.field = []
        
        for type in Answer_types:
            f = api.content.create(type="Field", title=type.value + "field" + "0", container=self.form)
            f.answer_type = type.value
            self.field.append(f)
            ref_schema['properties'][create_id(f)] = reference_schemata.get_field_ref_schema(f.answer_type, f.title)

            f = api.content.create(type="Field", title=type.value + "field" + "1", container=self.form)
            f.answer_type = type.value
            self.field.append(f)
            ref_schema['properties'][create_id(f)] = reference_schemata.get_field_ref_schema(f.answer_type, f.title)

        computed_schema = json.loads(self.view())
        self.assertEqual(dict(computed_schema), dict(ref_schema))

    ### validate invariants

    def test_validate_min_max_invariant(self):
        for field_type in Answer_types:
            field_type = field_type.value

            self.field.answer_type = field_type

            def check_invariant():
                if self.field.answer_type in ['text', 'textarea', 'number', 'integer', 'password']:
                    try:
                        IField.validateInvariants(self.field)
                    except:
                        self.fail("Min_max_invariant falsely raised an Invalid for answer_type " + self.field.answer_type)
                elif self.field.answer_type in ['tel', 'url', 'email', 'date', 'datetime-local', 'time', 'boolean']:
                    try:
                        IField.validateInvariants(self.field)
                        self.fail("Min_max_invariant didn't raise an Invalid for answer_type " + self.field.answer_type)
                    except Invalid:
                        pass
                else:
                    self.fail("Unknown answer_type: " + self.field.answer_type)
            
            self.field.minimum = 2
            self.field.maximum = 3
            check_invariant()

            self.field.maximum = 2
            check_invariant()

            self.field.minimum = 3
            try:
                IField.validateInvariants(self.field)
                self.fail("Min_max_invariant didn't raise an Invalid a minimum bigger than the maximum.")
            except Invalid:
                pass

            self.field.maximum = 0
            try:
                IField.validateInvariants(self.field)
                self.fail("Min_max_invariant didn't raise an Invalid for a maximum of 0.")
            except Invalid:
                pass

    def test_validate_placeholder_invariant(self):
        for field_type in Answer_types:
            field_type = field_type.value

            self.field.answer_type = field_type

            self.field.placeholder = "placeholder"
            if self.field.answer_type in ['text', 'textarea', 'password', 'tel', 'url', 'email']:
                try:
                    IField.validateInvariants(self.field)
                except:
                    self.fail("Placeholder_invariant falsely raised an Invalid for answer_type " + self.field.answer_type)
            elif self.field.answer_type in ['date', 'datetime-local', 'time', 'number', 'integer', 'boolean']:
                try:
                    IField.validateInvariants(self.field)
                    self.fail("Placeholder_invariant didn't raise an Invalid for answer_type " + self.field.answer_type)
                except Invalid:
                    pass
            else:
                self.fail("Unknown answer_type: " + self.field.answer_type)

    def test_validate_unit_invariant(self):
        for field_type in Answer_types:
            field_type = field_type.value

            self.field.answer_type = field_type

            self.field.unit = "unit"
            if self.field.answer_type in ['number', 'integer']:
                try:
                    IField.validateInvariants(self.field)
                except:
                    self.fail("Unit_invariant falsely raised an Invalid for answer_type " + self.field.answer_type)
            elif self.field.answer_type in ['text', 'textarea', 'password', 'tel', 'url', 'email', 'date', 'datetime-local', 'time', 'boolean']:
                try:
                    IField.validateInvariants(self.field)
                    self.fail("Unit_invariant didn't raise an Invalid for answer_type " + self.field.answer_type)
                except Invalid:
                    pass
            else:
                self.fail("Unknown answer_type: " + self.field.answer_type)

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
        self.selectionfield.answer_type = "radio"
        ref_schema = {create_id(self.selectionfield): reference_schemata.get_selectionfield_ref_schema("radio")}
        self._test_selectionfield_schema(ref_schema)

    def test_checkbox_selectionfield(self):
        self.selectionfield.answer_type = "checkbox"
        ref_schema = {create_id(self.selectionfield): reference_schemata.get_selectionfield_ref_schema("checkbox")}
        self._test_selectionfield_schema(ref_schema)

    def test_select_selectionfield(self):
        self.selectionfield.answer_type = "select"
        ref_schema = {create_id(self.selectionfield): reference_schemata.get_selectionfield_ref_schema("select")}
        self._test_selectionfield_schema(ref_schema)

    def test_selectmultiple_selectionfield(self):
        self.selectionfield.answer_type = "selectmultiple"
        ref_schema = {create_id(self.selectionfield): reference_schemata.get_selectionfield_ref_schema("selectmultiple")}
        self._test_selectionfield_schema(ref_schema)


    def _test_option_enum(self, ref_enum_list, id):
        computed_list = None
        type = self.selectionfield.answer_type
        if type in ["radio", "select"]:
            computed_list = json.loads(self.view())['properties'][id]['enum']
        elif type in ["checkbox", "selectmultiple"]:
            computed_list = json.loads(self.view())['properties'][id]['items']['enum']
        else:
            self.assertIn(type, ["radio", "select", "checkbox", "selectmultiple"])
        self.assertEqual(computed_list, ref_enum_list)

    def test_options_selectionfield(self):
        id = create_id(self.selectionfield)

        def test_options_for_answer_types(ref_enum_list):
            for type in Selection_answer_types:
                self.selectionfield.answer_type = type.value
                self._test_option_enum(ref_enum_list, id)

        test_options_for_answer_types([])

        api.content.create(type="Option", title="option 1", container=self.selectionfield)
        test_options_for_answer_types(["option 1"])
        
        api.content.create(type="Option", title="option 2", container=self.selectionfield)
        test_options_for_answer_types(["option 1", "option 2"])

        api.content.create(type="Option", title="option 3", container=self.selectionfield)
        test_options_for_answer_types(["option 1", "option 2", "option 3"])
        
    def test_additional_information(self):
        # should not change the schema
        self.selectionfield.user_helptext = "a tipp"
        field_id = create_id(self.selectionfield)

        for type in Selection_answer_types:
            type = type.value
            self.selectionfield.answer_type = type
            ref_schema = {field_id: reference_schemata.get_selectionfield_ref_schema(type)}

            self.selectionfield.description = "a description"
            ref_schema[field_id]["description"] = "a description"
            self._test_selectionfield_schema(ref_schema)

            self.selectionfield.intern_information = "an extra info"
            ref_schema[field_id]["comment"] = "an extra info"
            self._test_selectionfield_schema(ref_schema)

            self.selectionfield.description = None
            del ref_schema[field_id]['description']
            self._test_selectionfield_schema(ref_schema)

            self.selectionfield.intern_information = None

class ViewsJsonSchemaFormWithUploadFieldTest(unittest.TestCase):
    layer = EDI_JSONFORMS_INTEGRATION_TESTING
    view = None
    form = None
    uploadfield = None

    def _test_uploadfield_schema(self, ref_schema):
        computed_schema = json.loads(self.view())['properties']
        self.assertEqual(dict(computed_schema), dict(ref_schema))

    def setUp(self):
        setUp_json_schema_test(self)
        self.uploadfield = api.content.create(type="UploadField", title="an uploadfield", container=self.form)

    def test_file_uploadfield(self):
        self.uploadfield.answer_type = "file"
        ref_schema = {create_id(self.uploadfield): reference_schemata.get_uploadfield_ref_schema("file")}
        self._test_uploadfield_schema(ref_schema)

    def test_filemulti_uploadfield(self):
        self.uploadfield.answer_type = "file-multi"
        ref_schema = {create_id(self.uploadfield): reference_schemata.get_uploadfield_ref_schema("file-multi")}
        self._test_uploadfield_schema(ref_schema)

    def test_additional_information(self):
        # should not change the schema
        self.uploadfield.user_helptext = "a tipp"
        field_id = create_id(self.uploadfield)

        for type in Upload_answer_types:
            type = type.value
            self.uploadfield.answer_type = type
            ref_schema = {field_id: reference_schemata.get_uploadfield_ref_schema(type)}

            self.uploadfield.description = "a description"
            ref_schema[field_id]["description"] = "a description"
            self._test_uploadfield_schema(ref_schema)

            self.uploadfield.intern_information = "an extra info"
            ref_schema[field_id]["comment"] = "an extra info"
            self._test_uploadfield_schema(ref_schema)

            self.uploadfield.description = None
            del ref_schema[field_id]['description']
            self._test_uploadfield_schema(ref_schema)

            self.uploadfield.intern_information = None
            del ref_schema[field_id]['comment']
        


class ViewsJsonSchemaFieldsRequiredTest(unittest.TestCase):
    layer = EDI_JSONFORMS_INTEGRATION_TESTING
    view = None
    form = None
    field = []        

    def setUp(self):
        setUp_json_schema_test(self)
        answer_type = ["text", "number", "boolean"]
        self.field = []
        for i in range(3):
            self.field.append(api.content.create(type="Field", title="field" + str(i), container=self.form))
            self.field[i].answer_type = answer_type[i]

    def test_schema(self):
        computed_schema = json.loads(self.view())
        ref_schema = reference_schemata.get_form_ref_schema("")
        for f in self.field:
            ref_schema['properties'][create_id(f)] = reference_schemata.get_field_ref_schema(f.answer_type, f.title)

        self.assertEqual(dict(computed_schema), dict(ref_schema))

    def test_required_choices(self):
        test_required_choices(self)

class ViewsJsonSchemaSelectionfieldsRequiredTest(unittest.TestCase):
    layer = EDI_JSONFORMS_INTEGRATION_TESTING
    view = None
    form = None
    field = []

    def setUp(self):
        setUp_json_schema_test(self)
        selection_answer_type = ["radio", "checkbox", "selectmultiple"]
        self.field = []
        for i in range(3):
            self.field.append(api.content.create(type="SelectionField", title="selectionfield" + str(i), container=self.form))
            self.field[i].answer_type = selection_answer_type[i]

    def test_schema(self):
        computed_schema = json.loads(self.view())
        ref_schema = reference_schemata.get_form_ref_schema("")
        for f in self.field:
            ref_schema['properties'][create_id(f)] = reference_schemata.get_selectionfield_ref_schema(f.answer_type, f.title)

        self.assertEqual(dict(computed_schema), dict(ref_schema))

    def test_required_choices(self):
        test_required_choices(self)

class ViewsJsonSchemaUploadfieldsRequiredTest(unittest.TestCase):
    layer = EDI_JSONFORMS_INTEGRATION_TESTING
    view = None
    form = None
    field = []

    def setUp(self):
        setUp_json_schema_test(self)
        upload_answer_type = ["file", "file-multi", "file-multi"]
        self.field = []
        for i in range(3):
            self.field.append(api.content.create(type="UploadField", title="uploadfield" + str(i), container=self.form))
            self.field[i].answer_type = upload_answer_type[i]

    def test_schema(self):
        computed_schema = json.loads(self.view())
        ref_schema = reference_schemata.get_form_ref_schema("")
        for f in self.field:
            ref_schema['properties'][create_id(f)] = reference_schemata.get_uploadfield_ref_schema(f.answer_type, f.title)

        self.assertEqual(dict(computed_schema), dict(ref_schema))

    def test_required_choices(self):
        test_required_choices(self)



class ViewsJsonSchemaFormWithArrayTest(unittest.TestCase):
    layer = EDI_JSONFORMS_INTEGRATION_TESTING
    form = None
    view = None
    array = None

    def _test_array_schema(self, ref_schema):
        computed_schema = json.loads(self.view())['properties']
        self.assertEqual(dict(computed_schema), dict(ref_schema))

    def _test_array_with_children(self, type, answer_types, ref_schema={}):
        array_id = create_id(self.array)
        if ref_schema == {}: 
            ref_schema = {array_id: reference_schemata.get_array_ref_schema()}

        for at in answer_types:
            ref_schema = test_content.create_child_in_object(ref_schema, type, at, self.array)
            self._test_array_schema(ref_schema)
        return ref_schema

    def setUp(self):
        setUp_json_schema_test(self)
        self.array = api.content.create(type="Array", title="an array", container=self.form)

    def test_basic_array(self):
        ref_schema = {create_id(self.array): reference_schemata.get_array_ref_schema()}
        self._test_array_schema(ref_schema)

    def test_additional_information(self):
        array_id = create_id(self.array)
        ref_schema = {array_id: reference_schemata.get_array_ref_schema()}

        self.array.description = "a description"
        ref_schema[array_id]['description'] = "a description"
        self._test_array_schema(ref_schema)

        self.array.intern_information = "an extra info"
        ref_schema[array_id]['comment'] = "an extra info"
        self._test_array_schema(ref_schema)

        self.array.description = None
        del ref_schema[array_id]['description']
        self._test_array_schema(ref_schema)

        self.array.intern_information = None
        del ref_schema[array_id]['comment']

    def test_array_with_fields(self):
        field_answer_types = [t.value for t in Answer_types]
        self._test_array_with_children("Field", field_answer_types)

    def test_array_with_selectionfields(self):
        selectionfield_answer_types = [t.value for t in Selection_answer_types]
        ref_schema = self._test_array_with_children("SelectionField", selectionfield_answer_types)
        self._test_array_schema(ref_schema)

    def test_array_with_uploadfields(self):
        uploadfield_answer_types = [t.value for t in Upload_answer_types]
        self._test_array_with_children("UploadField", uploadfield_answer_types)

    def test_array_with_children(self):
        array_id = create_id(self.array)
        ref_schema = {array_id: reference_schemata.get_array_ref_schema()}

        ref_schema = test_content.create_all_child_types_in_object(ref_schema, self.array)
        self._test_array_schema(ref_schema)

    def test_array_with_array(self):
        array_id = create_id(self.array)
        ref_schema = {array_id: reference_schemata.get_array_ref_schema()}

        # test array with empty array
        child_array = api.content.create(type="Array", title="child array", container=self.array)
        child_array_id = create_id(child_array)
        child_ref_schema = reference_schemata.get_array_ref_schema(child_array.title)
        ref_schema[array_id]['items']['properties'][child_array_id] = child_ref_schema
        self._test_array_schema(ref_schema)

        # test array with two empty arrays
        child_array2 = api.content.create(type="Array", title="child array 2", container=self.array)
        child_array_id2 = create_id(child_array2)
        child_ref_schema2 = reference_schemata.get_array_ref_schema(child_array2.title)
        ref_schema[array_id]['items']['properties'][child_array_id2] = child_ref_schema2
        self._test_array_schema(ref_schema)

        # test array with non-empty array and empty array
        child_ref_schema = test_content.create_all_child_types_in_object({child_array_id:child_ref_schema}, child_array)[child_array_id]
        self._test_array_schema(ref_schema)

        # test array with two non-empty arrays
        child_ref_schema2 = test_content.create_all_child_types_in_object({child_array_id2:child_ref_schema2}, child_array2)[child_array_id2]
        self._test_array_schema(ref_schema)

        # test array with children and with two non-empty arrays
        ref_schema = test_content.create_all_child_types_in_object(ref_schema, self.array)
        self._test_array_schema(ref_schema)

class ViewsJsonSchemaArrayRequiredTest(unittest.TestCase):
    layer = EDI_JSONFORMS_INTEGRATION_TESTING
    form = None
    view = None
    array = None
    array_id = None

    def setUp(self):
        setUp_json_schema_test(self)
        self.array = api.content.create(type="Array", title="an array", container=self.form)
        self.array_id = create_id(self.array)

    def _test_array_schema(self, ref_schema):
        computed_schema = json.loads(self.view())['properties']
        self.assertEqual(dict(computed_schema), dict(ref_schema))

    def test_array_required(self):
        test_object_not_required(self, self.array_id)

        # test that array occurs in required list of the form
        self.array.required_choice = "required"
        test_object_required(self, self.array_id)
        # test that array has minItems and that it is 1
        ref_schema = {self.array_id: reference_schemata.get_array_ref_schema()}
        ref_schema[self.array_id]['minItems'] = 1
        self._test_array_schema(ref_schema)

    def test_array_children_required(self):
        ref_schema = {self.array_id: reference_schemata.get_array_ref_schema()}
        ref_schema = test_content.create_all_child_types_in_object(ref_schema, self.array)

        test_object_children_required(self, self.array, ref_schema, self._test_array_schema)

    def test_array_in_array_required(self):
        ref_schema = {self.array_id: reference_schemata.get_array_ref_schema()}

        # test empty array in array required
        child_array = api.content.create(type="Array", title="Child Array", container=self.array)
        child_array_id = create_id(child_array)
        child_array_schema = reference_schemata.get_array_ref_schema(child_array.title)
        child_array.required_choice = "required"
        ref_schema[self.array_id]['items']['required'].append(child_array_id)
        child_array_schema['minItems'] = 1

        ref_schema[self.array_id]['items']['properties'][child_array_id] = child_array_schema
        self._test_array_schema(ref_schema)

        # test empty child_array in array required and other fields in array optional
        ref_schema = test_content.create_all_child_types_in_object(ref_schema, self.array)
        self._test_array_schema(ref_schema)

        # test empty child_array in array required and other fields in array required
        ref_schema = test_content.create_all_child_types_in_object(ref_schema, self.array)
        child_array.required_choice = "optional"
        ref_schema[self.array_id]['items']['required'] = []
        del child_array_schema['minItems']
        test_object_children_required(self, self.array, ref_schema, self._test_array_schema)

        # test non-empty child_array in array required and other fields in array optional and fields in child_array optional
        child_array.required_choice = "required"
        ref_schema[self.array_id]['items']['required'] = [child_array_id]
        child_array_schema['minItems'] = 1
        child_array_schema = test_content.create_all_child_types_in_object({child_array_id: child_array_schema}, child_array)[child_array_id]
        self._test_array_schema(ref_schema)

        # test non-empty child_array in array required and other fields in array required and fields in child_array required
        for child in child_array.getFolderContents():
            child = child.getObject()
            child.required_choice = "required"
            child_array_schema['items']['required'].append(create_id(child))
        test_object_children_required(self, self.array, ref_schema, self._test_array_schema)



class ViewsJsonSchemaFormWithComplexTest(unittest.TestCase):
    layer = EDI_JSONFORMS_INTEGRATION_TESTING
    form = None
    view = None
    complex = None

    def _test_complex_schema(self, ref_schema):
        computed_schema = json.loads(self.view())['properties']
        self.assertEqual(dict(computed_schema), dict(ref_schema))

    def _test_complex_with_children(self, type, answer_types, ref_schema={}):
        complex_id = create_id(self.complex)
        if ref_schema == {}:
            ref_schema = {complex_id: reference_schemata.get_complex_ref_schema(self.complex.title)}

        for at in answer_types:
            ref_schema = test_content.create_child_in_object(ref_schema, type, at, self.complex)
            self._test_complex_schema(ref_schema)
            
        return ref_schema

    def setUp(self):
        setUp_json_schema_test(self)
        self.complex = api.content.create(type="Complex", title="a complex object", container=self.form)

    def test_basic_complex(self):
        ref_schema = {create_id(self.complex): reference_schemata.get_complex_ref_schema(self.complex.title)}
        self._test_complex_schema(ref_schema)

    def test_additional_information(self):
        complex_id = create_id(self.complex)
        ref_schema = {complex_id: reference_schemata.get_complex_ref_schema()}

        self.complex.description = "a description"
        ref_schema[complex_id]['description'] = "a description"
        self._test_complex_schema(ref_schema)

        self.complex.intern_information = "an extra info"
        ref_schema[complex_id]['comment'] = "an extra info"
        self._test_complex_schema(ref_schema)

        self.complex.description = None
        del ref_schema[complex_id]['description']
        self._test_complex_schema(ref_schema)

        self.complex.intern_information = None
        del ref_schema[complex_id]['comment']

    def test_complex_with_fields(self):
        field_answer_types = [t.value for t in Answer_types]
        self._test_complex_with_children("Field", field_answer_types)

    def test_complex_with_selectionfields(self):
        selectionfield_answer_types = [t.value for t in Selection_answer_types]
        ref_schema = self._test_complex_with_children("SelectionField", selectionfield_answer_types)
        self._test_complex_schema(ref_schema)

    def test_complex_with_uploadfields(self):
        uploadfield_answer_types = [t.value for t in Upload_answer_types]
        self._test_complex_with_children("UploadField", uploadfield_answer_types)

    def test_complex_with_children(self):
        complex_id = create_id(self.complex)
        ref_schema = {complex_id: reference_schemata.get_complex_ref_schema(self.complex.title)}

        ref_schema = test_content.create_all_child_types_in_object(ref_schema, self.complex)
        self._test_complex_schema(ref_schema)

    def test_complex_with_complex(self):
        complex_id = create_id(self.complex)
        ref_schema = {complex_id: reference_schemata.get_complex_ref_schema(self.complex.title)}

        # test complex with empty complex
        child_complex = api.content.create(type="Complex", title="child complex", container=self.complex)
        child_complex_id = create_id(child_complex)
        child_ref_schema = reference_schemata.get_complex_ref_schema(child_complex.title)
        ref_schema[complex_id]['properties'][child_complex_id] = child_ref_schema
        self._test_complex_schema(ref_schema)

        # test complex with two empty complexes
        child_complex2 = api.content.create(type="Complex", title="child complex 2", container=self.complex)
        child_complex_id2 = create_id(child_complex2)
        child_ref_schema2 = reference_schemata.get_complex_ref_schema(child_complex2.title)
        ref_schema[complex_id]['properties'][child_complex_id2] = child_ref_schema2
        self._test_complex_schema(ref_schema)

        # test complex with non-empty complex and empty complex
        child_ref_schema = test_content.create_all_child_types_in_object({child_complex_id:child_ref_schema}, child_complex)[child_complex_id]
        self._test_complex_schema(ref_schema)

        # test complex with two non-empty complexes
        child_ref_schema2 = test_content.create_all_child_types_in_object({child_complex_id2:child_ref_schema2}, child_complex2)[child_complex_id2]
        self._test_complex_schema(ref_schema)

        # test complex with children and with two non-empty complexes
        ref_schema = test_content.create_all_child_types_in_object(ref_schema, self.complex)
        self._test_complex_schema(ref_schema)

class ViewsJsonSchemaComplexRequiredTest(unittest.TestCase):
    layer = EDI_JSONFORMS_INTEGRATION_TESTING
    form = None
    view = None
    complex = None
    complex_id = None

    def setUp(self):
        setUp_json_schema_test(self)
        self.complex = api.content.create(type="Complex", title="a complex object", container=self.form)
        self.complex_id = create_id(self.complex)

    def _test_complex_schema(self, ref_schema):
        computed_schema = json.loads(self.view())['properties']
        self.assertEqual(dict(computed_schema), dict(ref_schema))

    def test_complex_required(self):
        test_object_not_required(self, self.complex_id)

        try:
            tmp = self.complex.required_choice
            self.fail("A complex object should not have an attribute to set the required status. An object cannot be required.")
        except AttributeError:
            pass

    def test_complex_children_required(self):
        ref_schema = {self.complex_id: reference_schemata.get_complex_ref_schema(self.complex.title)}
        ref_schema = test_content.create_all_child_types_in_object(ref_schema, self.complex)

        test_object_children_required(self, self.complex, ref_schema, self._test_complex_schema)

    def test_complex_in_complex_required(self):
        ref_schema = {self.complex_id: reference_schemata.get_complex_ref_schema()}

        # create child complex
        child_complex = api.content.create(type="Complex", title="Child Complex", container=self.complex)
        child_complex_id = create_id(child_complex)
        child_complex_schema = reference_schemata.get_complex_ref_schema(child_complex.title)
        ref_schema[self.complex_id]['properties'][child_complex_id] = child_complex_schema
        self._test_complex_schema(ref_schema)

        # create other fields in complex that are optional
        ref_schema = test_content.create_all_child_types_in_object(ref_schema, self.complex)
        self._test_complex_schema(ref_schema)

        # test that the other fields are required
        ref_schema = test_content.create_all_child_types_in_object(ref_schema, self.complex)
        # import pdb; pdb.set_trace()
        test_object_children_required(self, self.complex, ref_schema, self._test_complex_schema)

        # test non-empty child_complex in complex with optional fields and other fields in complex optional
        child_complex_schema = test_content.create_all_child_types_in_object({child_complex_id: child_complex_schema}, child_complex)[child_complex_id]
        self._test_complex_schema(ref_schema)

        # test non-empty child_complex in complex and other fields in complex required and fields in child_complex required
        for child in child_complex.getFolderContents():
            child = child.getObject()
            child.required_choice = "required"
            child_complex_schema['items']['required'].append(create_id(child))
        test_object_children_required(self, self.array, ref_schema, self._test_complex_schema)



# # class ViewsJsonSchemaFormWithFieldsetTest(unittest.TestCase):
# #     pass



# class ViewsJsonSchemaDependentRequiredTest(unittest.TestCase):
#     layer = EDI_JSONFORMS_INTEGRATION_TESTING
#     view = None
#     form = None
#     field = []
#     selectionfield = []

#     # TODO first: unit test of add_dependent_required with every possible type (also array etc) -> think about what should happen if array is required





# # class ViewsFunctionalTest(unittest.TestCase):

# #     layer = EDI_JSONFORMS_FUNCTIONAL_TESTING

# #     def setUp(self):
# #         self.portal = self.layer['portal']
# #         setRoles(self.portal, TEST_USER_ID, ['Manager'])
