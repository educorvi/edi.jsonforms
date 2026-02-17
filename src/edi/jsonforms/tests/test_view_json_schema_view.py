# -*- coding: utf-8 -*-
from edi.jsonforms.testing import EDI_JSONFORMS_FUNCTIONAL_TESTING
from edi.jsonforms.testing import EDI_JSONFORMS_INTEGRATION_TESTING
from plone import api
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from zope import component
from zope.intid.interfaces import IIntIds
from zope.interface.exceptions import Invalid
from zope.lifecycleevent import modified
from z3c.relationfield import RelationValue
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
from edi.jsonforms.tests.utils._test_required_choice import (
    test_required_choices,
    test_object_required,
    test_object_not_required,
    test_object_children_required,
)
from edi.jsonforms.tests.utils._test_schema_views import (
    test_view_is_registered,
    test_view_not_matching_interface,
    setUp_integration_test,
    setUp_json_schema_test,
)


class ViewsIntegrationTest(unittest.TestCase):
    layer = EDI_JSONFORMS_INTEGRATION_TESTING
    ids = {}

    def setUp(self):
        setUp_integration_test(self)

    def test_json_schema_view_is_registered(self):
        test_view_is_registered(self, "json-schema-view")

    def test_json_schema_view_not_matching_interface(self):
        test_view_not_matching_interface(self, "json-schema-view")


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
        self.portal["Fragebogen"].title = "a form"
        self.portal["Fragebogen"].description = "a description"
        ref_schema = reference_schemata.get_form_ref_schema()
        ref_schema["description"] = "a description"
        computed_schema = json.loads(self.view())
        self.assertEqual(ref_schema, dict(computed_schema))


class ViewsJsonSchemaFormWithFieldTest(unittest.TestCase):
    layer = EDI_JSONFORMS_INTEGRATION_TESTING
    form = None
    view = None
    field = None

    def _test_field_schema(self, ref_schema):
        computed_schema = json.loads(self.view())["properties"]
        self.assertEqual(dict(computed_schema), dict(ref_schema))

    def _test_textlike_fields(self, type):
        # should not change the schema
        self.field.placeholder = "a placeholder"

        field_id = create_id(self.field)
        ref_schema = {field_id: reference_schemata.get_field_ref_schema(type)}
        self._test_field_schema(ref_schema)

        self.field.minimum = 3
        ref_schema[field_id]["minLength"] = 3
        self._test_field_schema(ref_schema)

        self.field.minimum = None
        self.field.maximum = 5
        del ref_schema[field_id]["minLength"]
        ref_schema[field_id]["maxLength"] = 5
        self._test_field_schema(ref_schema)

        self.field.minimum = 3
        ref_schema[field_id]["minLength"] = 3
        self._test_field_schema(ref_schema)

    def _test_numberlike_fields(self, type):
        # should not change the schema
        self.field.unit = "a unit"

        field_id = create_id(self.field)
        ref_schema = {field_id: reference_schemata.get_field_ref_schema(type)}
        self._test_field_schema(ref_schema)

        self.field.minimum = 3
        ref_schema[field_id]["minimum"] = 3
        self._test_field_schema(ref_schema)

        self.field.minimum = None
        self.field.maximum = 5
        del ref_schema[field_id]["minimum"]
        ref_schema[field_id]["maximum"] = 5
        self._test_field_schema(ref_schema)

        self.field.minimum = 3
        ref_schema[field_id]["minimum"] = 3
        self._test_field_schema(ref_schema)

    def setUp(self):
        setUp_json_schema_test(self)
        self.field = api.content.create(
            type="Field", title="a field", container=self.form
        )

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
        self.field.placeholder = (
            "a placeholder phone number"  # should not change the schema
        )

        ref_schema = {
            create_id(self.field): reference_schemata.get_field_ref_schema("tel")
        }
        self._test_field_schema(ref_schema)

    def test_url_field(self):
        self.field.answer_type = "url"
        self.field.placeholder = "a placeholder url"  # should not change the schema

        ref_schema = {
            create_id(self.field): reference_schemata.get_field_ref_schema("url")
        }
        self._test_field_schema(ref_schema)

    def test_email_field(self):
        self.field.answer_type = "email"
        self.field.placeholder = "a placeholder email"  # should not change the schema

        ref_schema = {
            create_id(self.field): reference_schemata.get_field_ref_schema("email")
        }
        self._test_field_schema(ref_schema)

    def test_date_field(self):
        self.field.answer_type = "date"

        ref_schema = {
            create_id(self.field): reference_schemata.get_field_ref_schema("date")
        }
        self._test_field_schema(ref_schema)

    def test_datetimelocal_field(self):
        self.field.answer_type = "datetime-local"

        ref_schema = {
            create_id(self.field): reference_schemata.get_field_ref_schema(
                "datetime-local"
            )
        }
        self._test_field_schema(ref_schema)

    def test_time_field(self):
        self.field.answer_type = "time"

        ref_schema = {
            create_id(self.field): reference_schemata.get_field_ref_schema("time")
        }
        self._test_field_schema(ref_schema)

    def test_number_field(self):
        self.field.answer_type = "number"
        self._test_numberlike_fields("number")

    def test_integer_field(self):
        self.field.answer_type = "integer"
        self._test_numberlike_fields("integer")

    def test_boolean_field(self):
        self.field.answer_type = "boolean"

        ref_schema = {
            create_id(self.field): reference_schemata.get_field_ref_schema("boolean")
        }
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
            del ref_schema[field_id]["description"]
            self._test_field_schema(ref_schema)

            self.field.intern_information = None
            del ref_schema[field_id]["comment"]

    def test_multiple_fields(self):
        field_id = create_id(self.field)
        ref_schema = reference_schemata.get_form_ref_schema("")
        ref_schema["properties"][create_id(self.field)] = (
            reference_schemata.get_field_ref_schema(self.field.answer_type)
        )
        self.field = []

        for type in Answer_types:
            f = api.content.create(
                type="Field", title=type.value + "field" + "0", container=self.form
            )
            f.answer_type = type.value
            self.field.append(f)
            ref_schema["properties"][create_id(f)] = (
                reference_schemata.get_field_ref_schema(f.answer_type, f.title)
            )

            f = api.content.create(
                type="Field", title=type.value + "field" + "1", container=self.form
            )
            f.answer_type = type.value
            self.field.append(f)
            ref_schema["properties"][create_id(f)] = (
                reference_schemata.get_field_ref_schema(f.answer_type, f.title)
            )

        computed_schema = json.loads(self.view())
        self.assertEqual(dict(computed_schema), dict(ref_schema))

    ### validate invariants

    def test_validate_min_max_invariant(self):
        for field_type in Answer_types:
            field_type = field_type.value

            self.field.answer_type = field_type

            def check_invariant():
                if self.field.answer_type in [
                    "text",
                    "textarea",
                    "number",
                    "integer",
                    "password",
                ]:
                    try:
                        IField.validateInvariants(self.field)
                    except:
                        self.fail(
                            "Min_max_invariant falsely raised an Invalid for answer_type "
                            + self.field.answer_type
                        )
                elif self.field.answer_type in [
                    "tel",
                    "url",
                    "email",
                    "date",
                    "datetime-local",
                    "time",
                    "boolean",
                ]:
                    try:
                        IField.validateInvariants(self.field)
                        self.fail(
                            "Min_max_invariant didn't raise an Invalid for answer_type "
                            + self.field.answer_type
                        )
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
                self.fail(
                    "Min_max_invariant didn't raise an Invalid a minimum bigger than the maximum."
                )
            except Invalid:
                pass

            self.field.maximum = 0
            try:
                IField.validateInvariants(self.field)
                self.fail(
                    "Min_max_invariant didn't raise an Invalid for a maximum of 0."
                )
            except Invalid:
                pass

    def test_validate_placeholder_invariant(self):
        for field_type in Answer_types:
            field_type = field_type.value

            self.field.answer_type = field_type

            self.field.placeholder = "placeholder"
            if self.field.answer_type in [
                "text",
                "textarea",
                "password",
                "tel",
                "url",
                "email",
            ]:
                try:
                    IField.validateInvariants(self.field)
                except:
                    self.fail(
                        "Placeholder_invariant falsely raised an Invalid for answer_type "
                        + self.field.answer_type
                    )
            elif self.field.answer_type in [
                "date",
                "datetime-local",
                "time",
                "number",
                "integer",
                "boolean",
            ]:
                try:
                    IField.validateInvariants(self.field)
                    self.fail(
                        "Placeholder_invariant didn't raise an Invalid for answer_type "
                        + self.field.answer_type
                    )
                except Invalid:
                    pass
            else:
                self.fail("Unknown answer_type: " + self.field.answer_type)

    def test_validate_unit_invariant(self):
        for field_type in Answer_types:
            field_type = field_type.value

            self.field.answer_type = field_type

            self.field.unit = "unit"
            if self.field.answer_type in ["number", "integer"]:
                try:
                    IField.validateInvariants(self.field)
                except:
                    self.fail(
                        "Unit_invariant falsely raised an Invalid for answer_type "
                        + self.field.answer_type
                    )
            elif self.field.answer_type in [
                "text",
                "textarea",
                "password",
                "tel",
                "url",
                "email",
                "date",
                "datetime-local",
                "time",
                "boolean",
            ]:
                try:
                    IField.validateInvariants(self.field)
                    self.fail(
                        "Unit_invariant didn't raise an Invalid for answer_type "
                        + self.field.answer_type
                    )
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
        computed_schema = json.loads(self.view())["properties"]
        self.assertEqual(dict(computed_schema), dict(ref_schema))

    def setUp(self):
        setUp_json_schema_test(self)
        self.selectionfield = api.content.create(
            type="SelectionField", title="a selectionfield", container=self.form
        )

    def test_radio_selectionfield(self):
        self.selectionfield.answer_type = "radio"
        ref_schema = {
            create_id(
                self.selectionfield
            ): reference_schemata.get_selectionfield_ref_schema("radio")
        }
        self._test_selectionfield_schema(ref_schema)

    def test_checkbox_selectionfield(self):
        self.selectionfield.answer_type = "checkbox"
        ref_schema = {
            create_id(
                self.selectionfield
            ): reference_schemata.get_selectionfield_ref_schema("checkbox")
        }
        self._test_selectionfield_schema(ref_schema)

    def test_select_selectionfield(self):
        self.selectionfield.answer_type = "select"
        ref_schema = {
            create_id(
                self.selectionfield
            ): reference_schemata.get_selectionfield_ref_schema("select")
        }
        self._test_selectionfield_schema(ref_schema)

    def test_selectmultiple_selectionfield(self):
        self.selectionfield.answer_type = "selectmultiple"
        ref_schema = {
            create_id(
                self.selectionfield
            ): reference_schemata.get_selectionfield_ref_schema("selectmultiple")
        }
        self._test_selectionfield_schema(ref_schema)

    def _test_option_enum(self, ref_enum_list, id):
        computed_list = None
        type = self.selectionfield.answer_type
        if type in ["radio", "select"]:
            computed_list = json.loads(self.view())["properties"][id]["enum"]
        elif type in ["checkbox", "selectmultiple"]:
            computed_list = json.loads(self.view())["properties"][id]["items"]["enum"]
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

        api.content.create(
            type="Option", title="option 1", container=self.selectionfield
        )
        test_options_for_answer_types(["option 1"])

        api.content.create(
            type="Option", title="option 2", container=self.selectionfield
        )
        test_options_for_answer_types(["option 1", "option 2"])

        api.content.create(
            type="Option", title="option 3", container=self.selectionfield
        )
        test_options_for_answer_types(["option 1", "option 2", "option 3"])

    def test_additional_information(self):
        # should not change the schema
        self.selectionfield.user_helptext = "a tipp"
        field_id = create_id(self.selectionfield)

        for type in Selection_answer_types:
            type = type.value
            self.selectionfield.answer_type = type
            ref_schema = {
                field_id: reference_schemata.get_selectionfield_ref_schema(type)
            }

            self.selectionfield.description = "a description"
            ref_schema[field_id]["description"] = "a description"
            self._test_selectionfield_schema(ref_schema)

            self.selectionfield.intern_information = "an extra info"
            ref_schema[field_id]["comment"] = "an extra info"
            self._test_selectionfield_schema(ref_schema)

            self.selectionfield.description = None
            del ref_schema[field_id]["description"]
            self._test_selectionfield_schema(ref_schema)

            self.selectionfield.intern_information = None


class ViewsJsonSchemaFormWithUploadFieldTest(unittest.TestCase):
    layer = EDI_JSONFORMS_INTEGRATION_TESTING
    view = None
    form = None
    uploadfield = None

    def _test_uploadfield_schema(self, ref_schema):
        computed_schema = json.loads(self.view())["properties"]
        self.assertEqual(dict(computed_schema), dict(ref_schema))

    def setUp(self):
        setUp_json_schema_test(self)
        self.uploadfield = api.content.create(
            type="UploadField", title="an uploadfield", container=self.form
        )

    def test_file_uploadfield(self):
        self.uploadfield.answer_type = "file"
        ref_schema = {
            create_id(self.uploadfield): reference_schemata.get_uploadfield_ref_schema(
                "file"
            )
        }
        self._test_uploadfield_schema(ref_schema)

    def test_filemulti_uploadfield(self):
        self.uploadfield.answer_type = "file-multi"
        ref_schema = {
            create_id(self.uploadfield): reference_schemata.get_uploadfield_ref_schema(
                "file-multi"
            )
        }
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
            del ref_schema[field_id]["description"]
            self._test_uploadfield_schema(ref_schema)

            self.uploadfield.intern_information = None
            del ref_schema[field_id]["comment"]


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
            self.field.append(
                api.content.create(
                    type="Field", title="field" + str(i), container=self.form
                )
            )
            self.field[i].answer_type = answer_type[i]

    def test_schema(self):
        computed_schema = json.loads(self.view())
        ref_schema = reference_schemata.get_form_ref_schema("")
        for f in self.field:
            ref_schema["properties"][create_id(f)] = (
                reference_schemata.get_field_ref_schema(f.answer_type, f.title)
            )

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
            self.field.append(
                api.content.create(
                    type="SelectionField",
                    title="selectionfield" + str(i),
                    container=self.form,
                )
            )
            self.field[i].answer_type = selection_answer_type[i]

    def test_schema(self):
        computed_schema = json.loads(self.view())
        ref_schema = reference_schemata.get_form_ref_schema("")
        for f in self.field:
            ref_schema["properties"][create_id(f)] = (
                reference_schemata.get_selectionfield_ref_schema(f.answer_type, f.title)
            )

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
            self.field.append(
                api.content.create(
                    type="UploadField",
                    title="uploadfield" + str(i),
                    container=self.form,
                )
            )
            self.field[i].answer_type = upload_answer_type[i]

    def test_schema(self):
        computed_schema = json.loads(self.view())
        ref_schema = reference_schemata.get_form_ref_schema("")
        for f in self.field:
            ref_schema["properties"][create_id(f)] = (
                reference_schemata.get_uploadfield_ref_schema(f.answer_type, f.title)
            )

        self.assertEqual(dict(computed_schema), dict(ref_schema))

    def test_required_choices(self):
        test_required_choices(self)


class ViewsJsonSchemaFormWithArrayTest(unittest.TestCase):
    layer = EDI_JSONFORMS_INTEGRATION_TESTING
    form = None
    view = None
    array = None

    def _test_array_schema(self, ref_schema):
        computed_schema = json.loads(self.view())["properties"]
        self.assertEqual(dict(computed_schema), dict(ref_schema))

    def _test_array_with_children(self, type, answer_types, ref_schema={}):
        array_id = create_id(self.array)
        if ref_schema == {}:
            ref_schema = {array_id: reference_schemata.get_array_ref_schema()}

        for at in answer_types:
            ref_schema = test_content.create_child_in_object(
                ref_schema, type, at, self.array
            )
            self._test_array_schema(ref_schema)
        return ref_schema

    def setUp(self):
        setUp_json_schema_test(self)
        self.array = api.content.create(
            type="Array", title="an array", container=self.form
        )

    def test_basic_array(self):
        ref_schema = {create_id(self.array): reference_schemata.get_array_ref_schema()}
        self._test_array_schema(ref_schema)

    def test_additional_information(self):
        array_id = create_id(self.array)
        ref_schema = {array_id: reference_schemata.get_array_ref_schema()}

        self.array.description = "a description"
        ref_schema[array_id]["description"] = "a description"
        self._test_array_schema(ref_schema)

        self.array.intern_information = "an extra info"
        ref_schema[array_id]["comment"] = "an extra info"
        self._test_array_schema(ref_schema)

        self.array.description = None
        del ref_schema[array_id]["description"]
        self._test_array_schema(ref_schema)

        self.array.intern_information = None
        del ref_schema[array_id]["comment"]

    def test_array_with_fields(self):
        field_answer_types = [t.value for t in Answer_types]
        self._test_array_with_children("Field", field_answer_types)

    def test_array_with_selectionfields(self):
        selectionfield_answer_types = [t.value for t in Selection_answer_types]
        ref_schema = self._test_array_with_children(
            "SelectionField", selectionfield_answer_types
        )
        self._test_array_schema(ref_schema)

    def test_array_with_uploadfields(self):
        uploadfield_answer_types = [t.value for t in Upload_answer_types]
        self._test_array_with_children("UploadField", uploadfield_answer_types)

    def test_array_with_children(self):
        array_id = create_id(self.array)
        ref_schema = {array_id: reference_schemata.get_array_ref_schema()}

        ref_schema = test_content.create_all_child_types_in_object(
            ref_schema, self.array
        )
        self._test_array_schema(ref_schema)

    def test_array_with_array(self):
        array_id = create_id(self.array)
        ref_schema = {array_id: reference_schemata.get_array_ref_schema()}

        # test array with empty array
        child_array = api.content.create(
            type="Array", title="child array", container=self.array
        )
        child_array_id = create_id(child_array)
        child_ref_schema = reference_schemata.get_array_ref_schema(child_array.title)
        ref_schema[array_id]["items"]["properties"][child_array_id] = child_ref_schema
        self._test_array_schema(ref_schema)

        # test array with two empty arrays
        child_array2 = api.content.create(
            type="Array", title="child array 2", container=self.array
        )
        child_array_id2 = create_id(child_array2)
        child_ref_schema2 = reference_schemata.get_array_ref_schema(child_array2.title)
        ref_schema[array_id]["items"]["properties"][child_array_id2] = child_ref_schema2
        self._test_array_schema(ref_schema)

        # test array with non-empty array and empty array
        child_ref_schema = test_content.create_all_child_types_in_object(
            {child_array_id: child_ref_schema}, child_array
        )[child_array_id]
        self._test_array_schema(ref_schema)

        # test array with two non-empty arrays
        child_ref_schema2 = test_content.create_all_child_types_in_object(
            {child_array_id2: child_ref_schema2}, child_array2
        )[child_array_id2]
        self._test_array_schema(ref_schema)

        # test array with children and with two non-empty arrays
        ref_schema = test_content.create_all_child_types_in_object(
            ref_schema, self.array
        )
        self._test_array_schema(ref_schema)


class ViewsJsonSchemaArrayRequiredTest(unittest.TestCase):
    layer = EDI_JSONFORMS_INTEGRATION_TESTING
    form = None
    view = None
    array = None
    array_id = None

    def setUp(self):
        setUp_json_schema_test(self)
        self.array = api.content.create(
            type="Array", title="an array", container=self.form
        )
        self.array_id = create_id(self.array)

    def _test_array_schema(self, ref_schema):
        computed_schema = json.loads(self.view())["properties"]
        self.assertEqual(dict(computed_schema), dict(ref_schema))

    def test_array_required(self):
        test_object_not_required(self, self.array_id)

        # test that array occurs in required list of the form
        self.array.required_choice = "required"
        test_object_required(self, self.array_id)
        # test that array has minItems and that it is 1
        ref_schema = {self.array_id: reference_schemata.get_array_ref_schema()}
        ref_schema[self.array_id]["minItems"] = 1
        self._test_array_schema(ref_schema)

    def test_array_children_required(self):
        ref_schema = {self.array_id: reference_schemata.get_array_ref_schema()}
        ref_schema = test_content.create_all_child_types_in_object(
            ref_schema, self.array
        )

        test_object_children_required(
            self, self.array, ref_schema, self._test_array_schema
        )

    def test_array_in_array_required(self):
        ref_schema = {self.array_id: reference_schemata.get_array_ref_schema()}

        # test empty array in array required
        child_array = api.content.create(
            type="Array", title="Child Array", container=self.array
        )
        child_array_id = create_id(child_array)
        child_array_schema = reference_schemata.get_array_ref_schema(child_array.title)
        child_array.required_choice = "required"
        ref_schema[self.array_id]["items"]["required"].append(child_array_id)
        child_array_schema["minItems"] = 1

        ref_schema[self.array_id]["items"]["properties"][child_array_id] = (
            child_array_schema
        )
        self._test_array_schema(ref_schema)

        # test empty child_array in array required and other fields in array optional
        ref_schema = test_content.create_all_child_types_in_object(
            ref_schema, self.array
        )
        self._test_array_schema(ref_schema)

        # test empty child_array in array required and other fields in array required
        ref_schema = test_content.create_all_child_types_in_object(
            ref_schema, self.array
        )
        child_array.required_choice = "optional"
        ref_schema[self.array_id]["items"]["required"] = []
        del child_array_schema["minItems"]
        test_object_children_required(
            self, self.array, ref_schema, self._test_array_schema
        )

        # test non-empty child_array in array required and other fields in array optional and fields in child_array optional
        child_array.required_choice = "required"
        ref_schema[self.array_id]["items"]["required"] = [child_array_id]
        child_array_schema["minItems"] = 1
        child_array_schema = test_content.create_all_child_types_in_object(
            {child_array_id: child_array_schema}, child_array
        )[child_array_id]
        self._test_array_schema(ref_schema)

        # test non-empty child_array in array required and other fields in array required and fields in child_array required
        for child in child_array.getFolderContents():
            child = child.getObject()
            child.required_choice = "required"
            child_array_schema["items"]["required"].append(create_id(child))
        test_object_children_required(
            self, self.array, ref_schema, self._test_array_schema
        )


class ViewsJsonSchemaFormWithComplexTest(unittest.TestCase):
    layer = EDI_JSONFORMS_INTEGRATION_TESTING
    form = None
    view = None
    complex = None

    def _test_complex_schema(self, ref_schema):
        computed_schema = json.loads(self.view())["properties"]
        self.assertEqual(dict(computed_schema), dict(ref_schema))

    def _test_complex_with_children(self, type, answer_types, ref_schema={}):
        complex_id = create_id(self.complex)
        if ref_schema == {}:
            ref_schema = {
                complex_id: reference_schemata.get_complex_ref_schema(
                    self.complex.title
                )
            }

        for at in answer_types:
            ref_schema = test_content.create_child_in_object(
                ref_schema, type, at, self.complex
            )
            self._test_complex_schema(ref_schema)

        return ref_schema

    def setUp(self):
        setUp_json_schema_test(self)
        self.complex = api.content.create(
            type="Complex", title="a complex object", container=self.form
        )

    def test_basic_complex(self):
        ref_schema = {
            create_id(self.complex): reference_schemata.get_complex_ref_schema(
                self.complex.title
            )
        }
        self._test_complex_schema(ref_schema)

    def test_additional_information(self):
        complex_id = create_id(self.complex)
        ref_schema = {complex_id: reference_schemata.get_complex_ref_schema()}

        self.complex.description = "a description"
        ref_schema[complex_id]["description"] = "a description"
        self._test_complex_schema(ref_schema)

        self.complex.intern_information = "an extra info"
        ref_schema[complex_id]["comment"] = "an extra info"
        self._test_complex_schema(ref_schema)

        self.complex.description = None
        del ref_schema[complex_id]["description"]
        self._test_complex_schema(ref_schema)

        self.complex.intern_information = None
        del ref_schema[complex_id]["comment"]

    def test_complex_with_fields(self):
        field_answer_types = [t.value for t in Answer_types]
        self._test_complex_with_children("Field", field_answer_types)

    def test_complex_with_selectionfields(self):
        selectionfield_answer_types = [t.value for t in Selection_answer_types]
        ref_schema = self._test_complex_with_children(
            "SelectionField", selectionfield_answer_types
        )
        self._test_complex_schema(ref_schema)

    def test_complex_with_uploadfields(self):
        uploadfield_answer_types = [t.value for t in Upload_answer_types]
        self._test_complex_with_children("UploadField", uploadfield_answer_types)

    def test_complex_with_children(self):
        complex_id = create_id(self.complex)
        ref_schema = {
            complex_id: reference_schemata.get_complex_ref_schema(self.complex.title)
        }

        ref_schema = test_content.create_all_child_types_in_object(
            ref_schema, self.complex
        )
        self._test_complex_schema(ref_schema)

    def test_complex_with_complex(self):
        complex_id = create_id(self.complex)
        ref_schema = {
            complex_id: reference_schemata.get_complex_ref_schema(self.complex.title)
        }

        # test complex with empty complex
        child_complex = api.content.create(
            type="Complex", title="child complex", container=self.complex
        )
        child_complex_id = create_id(child_complex)
        child_ref_schema = reference_schemata.get_complex_ref_schema(
            child_complex.title
        )
        ref_schema[complex_id]["properties"][child_complex_id] = child_ref_schema
        self._test_complex_schema(ref_schema)

        # test complex with two empty complexes
        child_complex2 = api.content.create(
            type="Complex", title="child complex 2", container=self.complex
        )
        child_complex_id2 = create_id(child_complex2)
        child_ref_schema2 = reference_schemata.get_complex_ref_schema(
            child_complex2.title
        )
        ref_schema[complex_id]["properties"][child_complex_id2] = child_ref_schema2
        self._test_complex_schema(ref_schema)

        # test complex with non-empty complex and empty complex
        child_ref_schema = test_content.create_all_child_types_in_object(
            {child_complex_id: child_ref_schema}, child_complex
        )[child_complex_id]
        self._test_complex_schema(ref_schema)

        # test complex with two non-empty complexes
        child_ref_schema2 = test_content.create_all_child_types_in_object(
            {child_complex_id2: child_ref_schema2}, child_complex2
        )[child_complex_id2]
        self._test_complex_schema(ref_schema)

        # test complex with children and with two non-empty complexes
        ref_schema = test_content.create_all_child_types_in_object(
            ref_schema, self.complex
        )
        self._test_complex_schema(ref_schema)


class ViewsJsonSchemaComplexRequiredTest(unittest.TestCase):
    layer = EDI_JSONFORMS_INTEGRATION_TESTING
    form = None
    view = None
    complex = None
    complex_id = None

    def setUp(self):
        setUp_json_schema_test(self)
        self.complex = api.content.create(
            type="Complex", title="a complex object", container=self.form
        )
        self.complex_id = create_id(self.complex)

    def _test_complex_schema(self, ref_schema):
        computed_schema = json.loads(self.view())["properties"]
        self.assertEqual(dict(computed_schema), dict(ref_schema))

    def test_complex_required(self):
        test_object_not_required(self, self.complex_id)

        try:
            tmp = self.complex.required_choice
            self.fail(
                "A complex object should not have an attribute to set the required status. An object cannot be required."
            )
        except AttributeError:
            pass

    def test_complex_children_required(self):
        ref_schema = {
            self.complex_id: reference_schemata.get_complex_ref_schema(
                self.complex.title
            )
        }
        ref_schema = test_content.create_all_child_types_in_object(
            ref_schema, self.complex
        )

        test_object_children_required(
            self, self.complex, ref_schema, self._test_complex_schema
        )

    def test_complex_in_complex_required(self):
        ref_schema = {self.complex_id: reference_schemata.get_complex_ref_schema()}

        # create child complex
        child_complex = api.content.create(
            type="Complex", title="Child Complex", container=self.complex
        )
        child_complex_id = create_id(child_complex)
        child_complex_schema = reference_schemata.get_complex_ref_schema(
            child_complex.title
        )
        ref_schema[self.complex_id]["properties"][child_complex_id] = (
            child_complex_schema
        )
        self._test_complex_schema(ref_schema)

        # create other fields in complex that are optional
        ref_schema = test_content.create_all_child_types_in_object(
            ref_schema, self.complex
        )
        self._test_complex_schema(ref_schema)

        # test that the other fields are required
        ref_schema = test_content.create_all_child_types_in_object(
            ref_schema, self.complex
        )
        # import pdb; pdb.set_trace()
        test_object_children_required(
            self, self.complex, ref_schema, self._test_complex_schema
        )

        # test non-empty child_complex in complex with optional fields and other fields in complex optional
        child_complex_schema = test_content.create_all_child_types_in_object(
            {child_complex_id: child_complex_schema}, child_complex
        )[child_complex_id]
        self._test_complex_schema(ref_schema)

        # test non-empty child_complex in complex and other fields in complex required and fields in child_complex required
        for child in child_complex.getFolderContents():
            child = child.getObject()
            child.required_choice = "required"
            child_complex_schema["required"].append(create_id(child))
        test_object_children_required(
            self, self.complex, ref_schema, self._test_complex_schema
        )


class ViewsJsonSchemaNestedTest(unittest.TestCase):
    layer = EDI_JSONFORMS_INTEGRATION_TESTING
    form = None
    view = None
    maxDiff = None

    def setUp(self):
        setUp_json_schema_test(self)

    def _test_schema(self, ref_schema):
        computed_schema = json.loads(self.view())["properties"]
        self.assertEqual(dict(computed_schema), dict(ref_schema))

    def test_complex_in_array(self):
        outer_array = api.content.create(
            type="Array", title="outer array", container=self.form
        )
        array_id = create_id(outer_array)
        inner_complex = api.content.create(
            type="Complex", title="inner complex", container=outer_array
        )
        complex_id = create_id(inner_complex)

        # test empty complex in array
        ref_schema = {
            array_id: reference_schemata.get_array_ref_schema(outer_array.title)
        }
        complex_schema = reference_schemata.get_complex_ref_schema(inner_complex.title)
        ref_schema[array_id]["items"]["properties"][complex_id] = complex_schema
        self._test_schema(ref_schema)

        # test complex with children in array with children
        complex_schema = test_content.create_all_child_types_in_object(
            {complex_id: complex_schema}, inner_complex
        )
        ref_schema = test_content.create_all_child_types_in_object(
            ref_schema, outer_array
        )
        self._test_schema(ref_schema)

    def create_array_and_complex(self, container, ref_schema):
        ref_props = {}
        if container.portal_type == "Array":
            ref_props = ref_schema["items"]["properties"]
        else:
            ref_props = ref_schema["properties"]
        array = api.content.create(type="Array", title="an array", container=container)
        complex = api.content.create(
            type="Complex", title="a complex", container=container
        )
        ref_props[create_id(array)] = reference_schemata.get_array_ref_schema(
            array.title
        )
        ref_props[create_id(complex)] = reference_schemata.get_complex_ref_schema(
            complex.title
        )

    def test_nested_depth_3(self):
        # test depth 1
        ref_schema = reference_schemata.get_form_ref_schema()
        self.create_array_and_complex(self.form, ref_schema)
        self._test_schema(ref_schema["properties"])

        # test depth 2
        children = [child.getObject() for child in self.form.getFolderContents()]
        for child in children:
            self.create_array_and_complex(
                child, ref_schema["properties"][create_id(child)]
            )
        self._test_schema(ref_schema["properties"])

        # test depth 3
        for child in children:
            child_id = create_id(child)
            ref = ref_schema["properties"][child_id]
            if child.portal_type == "Array":
                ref = ref["items"]["properties"]
            else:
                ref = ref["properties"]
            for c in child.getFolderContents():
                c = c.getObject()
                self.create_array_and_complex(c, ref[create_id(c)])
        self._test_schema(ref_schema["properties"])


class ViewsJsonSchemaFieldsetTest(unittest.TestCase):
    layer = EDI_JSONFORMS_INTEGRATION_TESTING
    form = None
    view = None
    ref_schema = None

    def _test_fieldset_schema(self, ref_schema=None):
        ref_schema = ref_schema if ref_schema != None else self.ref_schema
        computed_schema = json.loads(self.view())
        self.assertEqual(dict(computed_schema), dict(ref_schema))

    def setUp(self):
        setUp_json_schema_test(self)
        self.ref_schema = reference_schemata.get_form_ref_schema("")

    def test_empty_fieldset(self):
        api.content.create(type="Fieldset", title="a fieldset", container=self.form)
        self._test_fieldset_schema()

    def create_everything_in_fieldset(self, schema, container):
        for t in Answer_types:
            t = t.value
            child = api.content.create(
                type="Field", title="field_" + t, container=container
            )
            child.answer_type = t
            schema["properties"][create_id(child)] = (
                reference_schemata.get_field_ref_schema(t, child.title)
            )

        for t in Selection_answer_types:
            t = t.value
            child = api.content.create(
                type="SelectionField", title="selectionfield_" + t, container=container
            )
            child.answer_type = t
            opt = api.content.create(
                type="Option", title="option1" + t, container=child
            )
            schema["properties"][create_id(child)] = (
                reference_schemata.get_selectionfield_ref_schema(
                    t, child.title, [opt.title]
                )
            )

        for t in Upload_answer_types:
            t = t.value
            child = api.content.create(
                type="UploadField", title="uploadfield_" + t, container=container
            )
            child.answer_type = t
            schema["properties"][create_id(child)] = (
                reference_schemata.get_uploadfield_ref_schema(t, child.title)
            )

        array = api.content.create(type="Array", title="an array", container=container)
        schema["properties"][create_id(array)] = (
            reference_schemata.get_array_ref_schema(array.title)
        )

        array_child = api.content.create(
            type="Field", title="a field in an array", container=array
        )
        schema["properties"][create_id(array)]["items"]["properties"][
            create_id(array_child)
        ] = reference_schemata.get_field_ref_schema(
            array_child.answer_type, array_child.title
        )

        complex = api.content.create(
            type="Complex", title="a complex", container=container
        )
        schema["properties"][create_id(complex)] = (
            reference_schemata.get_complex_ref_schema(complex.title)
        )

        complex_child = api.content.create(
            type="Field", title="a field in a complex", container=complex
        )
        schema["properties"][create_id(complex)]["properties"][
            create_id(complex_child)
        ] = reference_schemata.get_field_ref_schema(
            complex_child.answer_type, complex_child.title
        )

        fieldset2 = api.content.create(
            type="Fieldset", title="a fieldset in a fieldset", container=container
        )
        fieldset2_child = api.content.create(
            type="Field",
            title="a field in an fieldset in an fieldset",
            container=fieldset2,
        )
        schema["properties"][create_id(fieldset2_child)] = (
            reference_schemata.get_field_ref_schema(
                fieldset2_child.answer_type, fieldset2_child.title
            )
        )

    def test_fieldset_with_children(self):
        fieldset = api.content.create(
            type="Fieldset", title="a fieldset", container=self.form
        )
        self.create_everything_in_fieldset(self.ref_schema, fieldset)

        self._test_fieldset_schema()

    def test_nested_fieldset(self):
        array = api.content.create(type="Array", title="an array", container=self.form)
        self.ref_schema["properties"][create_id(array)] = (
            reference_schemata.get_array_ref_schema(array.title)
        )

        fieldset1 = api.content.create(
            type="Fieldset", title="a fieldset in an array", container=array
        )
        self.create_everything_in_fieldset(
            self.ref_schema["properties"][create_id(array)]["items"], fieldset1
        )

        complex = api.content.create(
            type="Complex", title="a complex", container=self.form
        )
        self.ref_schema["properties"][create_id(complex)] = (
            reference_schemata.get_complex_ref_schema(complex.title)
        )

        fieldset2 = api.content.create(
            type="Fieldset", title="a fieldset in a complex", container=complex
        )
        self.create_everything_in_fieldset(
            self.ref_schema["properties"][create_id(complex)], fieldset2
        )

        self._test_fieldset_schema()

    # TODO first: unit test of add_dependent_required with every possible type (also array etc) -> think about what should happen if array is required


class ViewsJsonSchemaDependentRequiredTest(unittest.TestCase):
    layer = EDI_JSONFORMS_INTEGRATION_TESTING
    form = None
    view = None
    maxDiff = None
    intids = None
    ref_schema = None
    # field = []
    # selectionfield = []

    def setUp(self):
        setUp_json_schema_test(self)
        self.intids = component.getUtility(IIntIds)
        self.ref_schema = reference_schemata.get_form_ref_schema("")

    def create_all_content_types(self, container):
        # create dependent field in form
        dependent_field = api.content.create(
            type="Field", title="dependent field", container=container
        )
        dependent_field_id = create_id(dependent_field)
        self.ref_schema["properties"][dependent_field_id] = (
            reference_schemata.get_field_ref_schema(
                dependent_field.answer_type, "dependent field"
            )
        )

        # create dependent selectionfield in form
        dependent_selectionfield = api.content.create(
            type="SelectionField", title="dependent selectionfield", container=container
        )
        dependent_selectionfield_id = create_id(dependent_selectionfield)
        self.ref_schema["properties"][dependent_selectionfield_id] = (
            reference_schemata.get_selectionfield_ref_schema(
                dependent_selectionfield.answer_type, "dependent selectionfield"
            )
        )

        dependent_field.dependencies.append(
            RelationValue(self.intids.getId(dependent_selectionfield))
        )

        # create dependent complex in form
        dependent_complex = api.content.create(
            type="Complex", title="dependent complex", container=container
        )
        dependent_complex_id = create_id(dependent_complex)
        self.ref_schema["properties"][dependent_complex_id] = (
            reference_schemata.get_complex_ref_schema("dependent complex")
        )

        # create dependent array in form
        dependent_array = api.content.create(
            type="Array", title="dependent array", container=container
        )
        dependent_array_id = create_id(dependent_array)
        self.ref_schema["properties"][dependent_array_id] = (
            reference_schemata.get_array_ref_schema("dependent array")
        )

        return (
            dependent_field,
            dependent_selectionfield,
            dependent_complex,
            dependent_array,
        )

    def _test_form_schema(self, ref_schema=None):
        ref_schema = ref_schema if ref_schema is not None else self.ref_schema
        computed_schema = json.loads(self.view())
        self.assertEqual(dict(computed_schema), dict(ref_schema))

    def test_dependent_from_field(self):
        # create independent field in the form
        independent_field = api.content.create(
            type="Field", title="independent", container=self.form
        )
        independent_field_id = create_id(independent_field)
        self.ref_schema["properties"][independent_field_id] = (
            reference_schemata.get_field_ref_schema(
                independent_field.answer_type, "independent"
            )
        )

        # create dependent field/selectionfield/complex/array
        dep_field, dep_sel_field, dep_complex, dep_array = (
            self.create_all_content_types(self.form)
        )
        ids = [
            create_id(dep_field),
            create_id(dep_sel_field),
            create_id(dep_complex),
            create_id(dep_array),
        ]

        # test dep_field (type field, selection_field, upload_field, complex or array) is dependent required from the independent field
        def test_dep_req(dep_field, id):
            # add dependency to the independent_field
            dep_field.dependencies = [
                RelationValue(self.intids.getId(independent_field))
            ]
            modified(dep_field)
            # test schema, nothing should be changed
            self._test_form_schema()

            # make independent field required
            independent_field.required_choice = "required"
            self.ref_schema["required"].append(independent_field_id)
            # test schema, nothing should be changed (except for the required status)
            self._test_form_schema()

            # make dependent one required
            dep_field.required_choice = "required"
            if dep_field.portal_type != "Complex":
                if independent_field_id in self.ref_schema["dependentRequired"]:
                    self.ref_schema["dependentRequired"][independent_field_id].append(
                        [id]
                    )
                else:
                    self.ref_schema["dependentRequired"][independent_field_id] = [id]
                if dep_field.portal_type == "Array":
                    self.ref_schema["properties"][id]["minItems"] = 1
            # test schema, dependentrequired should be changed (unless it is a complex object)
            self._test_form_schema()

            # make independent one optional again, dependentrequired should stay the same
            independent_field.required_choice = "optional"
            self.ref_schema["required"].remove(independent_field_id)
            self._test_form_schema()

            # revert changes
            dep_field.required_choice = "optional"
            if dep_field.portal_type != "Complex":
                self.ref_schema["dependentRequired"][independent_field_id].remove(id)
                if self.ref_schema["dependentRequired"][independent_field_id] == []:
                    del self.ref_schema["dependentRequired"][independent_field_id]
                if dep_field.portal_type == "Array":
                    del self.ref_schema["properties"][create_id(dep_field)]["minItems"]
            dep_field.dependencies = []

        answer_types = [a.value for a in Answer_types]
        # test 'dependentRequired' for different answer types of undependent field
        for at_independent in answer_types:
            independent_field.answer_type = at_independent
            self.ref_schema["properties"][independent_field_id] = (
                reference_schemata.get_field_ref_schema(
                    at_independent, independent_field.title
                )
            )

            self._test_dependencies(
                [dep_field, dep_sel_field, dep_complex, dep_array], test_dep_req
            )

    """
    test_dep_req takes a field and its id as argument
    """

    def _test_dependencies(self, dependents: list, test_dep_req):
        answer_types = [a.value for a in Answer_types]
        selection_answer_types = [a.value for a in Selection_answer_types]
        ids = [create_id(obj) for obj in dependents]

        id = 0
        for d in dependents:
            if d.portal_type == "Field":
                for at_dependent in answer_types:
                    d.answer_type = at_dependent
                    self.ref_schema["properties"][ids[id]] = (
                        reference_schemata.get_field_ref_schema(at_dependent, d.title)
                    )
                    test_dep_req(d, ids[id])
            elif d.portal_type == "SelectionField":
                for at_dependent in selection_answer_types:
                    d.answer_type = at_dependent
                    self.ref_schema["properties"][ids[id]] = (
                        reference_schemata.get_selectionfield_ref_schema(
                            at_dependent, d.title
                        )
                    )
                    test_dep_req(d, ids[id])
            else:
                test_dep_req(d, ids[id])
            id += 1

    def test_dependent_from_selectionfield(self):
        # create independent selectionfield in the form with two options
        independent_field = api.content.create(
            type="SelectionField", title="independent", container=self.form
        )
        opt1 = api.content.create(
            type="Option", title="yes", container=independent_field
        )
        opt2 = api.content.create(
            type="Option", title="no", container=independent_field
        )
        options = [opt1.title, opt2.title]

        independent_field_id = create_id(independent_field)
        self.ref_schema["properties"][independent_field_id] = (
            reference_schemata.get_selectionfield_ref_schema(
                independent_field.answer_type, "independent", options
            )
        )

        # create dependent field/selectionfield/complex/array
        dep_field, dep_sel_field, dep_complex, dep_array = (
            self.create_all_content_types(self.form)
        )
        ids = [
            create_id(dep_field),
            create_id(dep_sel_field),
            create_id(dep_complex),
            create_id(dep_array),
        ]

        # test dep_field (type field, selection_field, upload_field, complex or array) is dependent required from the independent selectionfield
        def test_dep_req(dep_field, id):
            # add dependency to the option of the independent_field
            dep_field.dependencies = [RelationValue(self.intids.getId(opt1))]
            modified(dep_field)
            # test schema, nothing should be changed
            self._test_form_schema()

            # make independent field required
            independent_field.required_choice = "required"
            self.ref_schema["required"].append(independent_field_id)
            # test schema, nothing should be changed (except for the required status)
            self._test_form_schema()

            # make dependent one required
            dep_field.required_choice = "required"
            if dep_field.portal_type != "Complex":
                self.ref_schema["allOf"] = [
                    {
                        "if": {
                            "properties": {independent_field_id: {"const": opt1.title}}
                        },
                        "then": {"required": id},
                    }
                ]
                if dep_field.portal_type == "Array":
                    self.ref_schema["properties"][id]["minItems"] = 1
            # test schema, dependentrequired should be changed (unless it is a complex object)
            self._test_form_schema()

            # make independent one optional again, dependentrequired should stay the same
            independent_field.required_choice = "optional"
            self.ref_schema["required"].remove(independent_field_id)
            self._test_form_schema()

            # revert changes
            dep_field.required_choice = "optional"
            if dep_field.portal_type != "Complex":
                self.ref_schema["allOf"] = []
                if dep_field.portal_type == "Array":
                    del self.ref_schema["properties"][create_id(dep_field)]["minItems"]
            dep_field.dependencies = []

        selection_answer_types = [a.value for a in Selection_answer_types]
        # test 'dependentRequired' for different answer types
        for at_independent in selection_answer_types:
            independent_field.answer_type = at_independent
            self.ref_schema["properties"][independent_field_id] = (
                reference_schemata.get_selectionfield_ref_schema(
                    at_independent, independent_field.title, options
                )
            )

            self._test_dependencies(
                [dep_field, dep_sel_field, dep_complex, dep_array], test_dep_req
            )

    # TODO test additionally manually with JP after implementation
    def test_dependent_from_uploadfield(self):
        pass

    # TODO currently a dependency from an array is not possible
    # def test_dependent_from_array(self):
    #     pass


# # class ViewsFunctionalTest(unittest.TestCase):

# #     layer = EDI_JSONFORMS_FUNCTIONAL_TESTING

# #     def setUp(self):
# #         self.portal = self.layer['portal']
# #         setRoles(self.portal, TEST_USER_ID, ['Manager'])
