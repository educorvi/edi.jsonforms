# -*- coding: utf-8 -*-
from edi.jsonforms.testing import EDI_JSONFORMS_FUNCTIONAL_TESTING
from edi.jsonforms.testing import EDI_JSONFORMS_INTEGRATION_TESTING
from plone import api
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from zope.component import getMultiAdapter
from zope.interface.interfaces import ComponentLookupError
from zope.interface.exceptions import Invalid

import copy
import json
import unittest

from edi.jsonforms.tests.utils._test_schema_views import (
    test_view_is_registered,
    test_view_not_matching_interface,
    setUp_integration_test,
    setUp_ui_schema_test,
)
from edi.jsonforms.tests.utils import create_content_ui
import edi.jsonforms.tests.utils.reference_schemata as reference_schemata
from edi.jsonforms.content.field import Answer_types
from edi.jsonforms.content.selection_field import Selection_answer_types
from edi.jsonforms.views.common import create_id


class ViewsIntegrationTest(unittest.TestCase):
    layer = EDI_JSONFORMS_INTEGRATION_TESTING
    ids = {}

    def setUp(self):
        setUp_integration_test(self)

    def test_ui_schema_view_is_registered(self):
        test_view_is_registered(self, "ui-schema-view")

    def test_ui_schema_view_not_matching_interface(self):
        test_view_not_matching_interface(self, "ui-schema-view")


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

    def test_fields_in_form(self):
        ref_schema = reference_schemata.get_form_ref_schema_ui()
        create_content_ui.create_and_test_children(
            self,
            ref_schema,
            ref_schema["layout"]["elements"],
            self.form,
            "Field",
            Answer_types,
            "/properties/",
        )

    def test_selectionfields_in_form(self):
        ref_schema = reference_schemata.get_form_ref_schema_ui()
        create_content_ui.create_and_test_children(
            self,
            ref_schema,
            ref_schema["layout"]["elements"],
            self.form,
            "SelectionField",
            Selection_answer_types,
            "/properties/",
        )

        for sf in self.form.getFolderContents():
            sf = sf.getObject()
            api.content.create(
                type="Option", title="opt_" + sf.answer_type, container=sf
            )
        self._test_schema(ref_schema)

    def test_uploadfields_in_form(self):
        ref_schema = reference_schemata.get_form_ref_schema_ui()
        create_content_ui.create_and_test_children(
            self,
            ref_schema,
            ref_schema["layout"]["elements"],
            self.form,
            "UploadField",
            ["file"],
            "/properties/",
        )

    # TODO
    # def test_helptext_in_form(self):
    #     helptext = api.content.create(type="Helptext", title="Helptext", container=self.form)
    #     helptext.helptext = "<p>This is a helptext</p>"

    #     helptext_schema = reference_schemata.get_child_ref_schema_ui(helptext.helptext)
    #     elements = reference_schemata.insert_into_elements(elements, helptext_schema)

    #     # test schema
    #     computed_schema = json.loads(self.view())
    #     self.assertEqual(dict(computed_schema), dict(self.ref_schema))

    def _test_options(self, field, answer_types, option_label, option):
        ref_schema = reference_schemata.get_form_ref_schema_ui()

        for field_type in answer_types:
            field.answer_type = field_type
            child_schema = reference_schemata.get_child_ref_schema_ui(
                field_type, "/properties/" + create_id(field), field.title
            )
            if "options" in child_schema:
                child_schema["options"][option_label] = option
            else:
                child_schema["options"] = {option_label: option}

            buttons = copy.deepcopy(ref_schema["layout"]["elements"])
            ref_schema["layout"]["elements"] = reference_schemata.insert_into_elements(
                ref_schema["layout"]["elements"], child_schema
            )
            self._test_schema(ref_schema)
            ref_schema["layout"]["elements"] = buttons

    def test_unit_of_fields(self):
        field = api.content.create(type="Field", title="field", container=self.form)
        field.unit = "unit"
        self._test_options(field, ["number", "integer"], "append", field.unit)

    def test_placeholder_of_fields(self):
        field = api.content.create(type="Field", title="field", container=self.form)
        field.placeholder = "placeholder"
        self._test_options(
            field,
            ["text", "textarea", "password", "tel", "url", "email"],
            "placeholder",
            field.placeholder,
        )

    def test_acceptedfiletypes_for_uploadfields(self):
        uploadfield = api.content.create(
            type="UploadField", title="uploadfield", container=self.form
        )
        uploadfield.accepted_file_types = ["application/pdf", "image/png"]
        self._test_options(
            uploadfield,
            ["file"],
            "acceptedFileType",
            uploadfield.accepted_file_types,
        )


class ViewsUiSchemaFormWithFieldsetTest(unittest.TestCase):
    layer = EDI_JSONFORMS_INTEGRATION_TESTING
    form = None
    view = None
    fieldset = None
    ref_schema = None

    def _test_schema(self, ref_schema):
        computed_schema = json.loads(self.view())
        self.assertEqual(dict(computed_schema), dict(ref_schema))

    def setUp(self):
        setUp_ui_schema_test(self)
        self.fieldset = api.content.create(
            type="Fieldset", title="Fieldset", container=self.form
        )
        self.ref_schema = reference_schemata.get_form_ref_schema_ui()
        fieldset_schema = reference_schemata.get_fieldset_ref_schema_ui(
            self.fieldset.title
        )
        self.ref_schema["layout"]["elements"] = reference_schemata.insert_into_elements(
            self.ref_schema["layout"]["elements"], fieldset_schema
        )

    def test_empty_fieldset(self):
        self._test_schema(self.ref_schema)

    def test_children_in_fieldset(self):
        create_content_ui.create_and_test_all_children(
            self,
            self.ref_schema,
            self.ref_schema["layout"]["elements"][0]["elements"],
            self.fieldset,
            "/properties/",
        )

    def test_fieldset_in_fieldset(self):
        # test empty fieldset in fieldset
        nested_fieldset = api.content.create(
            type="Fieldset", title="Nested Fieldset", container=self.fieldset
        )
        nested_fieldset_schema = reference_schemata.get_fieldset_ref_schema_ui(
            nested_fieldset.title
        )
        self.ref_schema["layout"]["elements"][0]["elements"] = (
            reference_schemata.insert_into_elements(
                self.ref_schema["layout"]["elements"][0]["elements"],
                nested_fieldset_schema,
            )
        )
        self._test_schema(self.ref_schema)

        # test filled fieldset in fieldset
        create_content_ui.create_and_test_all_children(
            self,
            self.ref_schema,
            self.ref_schema["layout"]["elements"][0]["elements"][0]["elements"],
            nested_fieldset,
            "/properties/",
        )

        # test filled fieldset in filled fieldset
        create_content_ui.create_and_test_all_children(
            self,
            self.ref_schema,
            self.ref_schema["layout"]["elements"][0]["elements"],
            self.fieldset,
            "/properties/",
        )

    # def test_array_in_fieldset(self):
    #     # test empty array in fieldset
    #     nested_array = api.content.create(type="Array", title="Nested Array", container=self.fieldset)
    #     nested_array_schema = reference_schemata.get_array_ref_schema_ui(nested_array.title)

    #     # insert schema of nested_scope into descendantControlOverrides of self.array (flattened)
    #     self.ref_schema['layout']['elements'][0]['elements'] = reference_schemata.insert_into_elements(self.ref_schema['layout']['elements'][0]['elements'], nested_array_schema)
    #     self._test_schema(self.ref_schema)

    #     # test filled array in fieldset
    #     base_nested_scope = "/properties/" + create_id(nested_array) + "/items/properties/"
    #     # insert children of nested_array into descendantControlOverrides of nested_array
    #     create_content_ui.create_and_test_all_children_descendantControlOverrides(self, self.ref_schema, nested_array_schema['options']['descendantControlOverrides'], nested_array, base_nested_scope)

    #     # test filled array in filled fieldset
    #     # create children in fieldset
    #     create_content_ui.create_and_test_all_children(self, self.ref_schema, self.ref_schema['layout']['elements'][0]['elements'], self.fieldset, "/properties/")
    # TODO

    def test_complex_in_fieldset(self):
        pass
        # TODO


class ViewsUiSchemaFormWithArrayTest(unittest.TestCase):
    layer = EDI_JSONFORMS_INTEGRATION_TESTING
    form = None
    view = None
    array = None
    ref_schema = None

    def _test_schema(self, ref_schema):
        computed_schema = json.loads(self.view())
        self.assertEqual(dict(computed_schema), dict(ref_schema))

    def setUp(self):
        setUp_ui_schema_test(self)
        self.array = api.content.create(
            type="Array", title="Array", container=self.form
        )
        self.ref_schema = reference_schemata.get_form_ref_schema_ui()
        array_schema = reference_schemata.get_array_ref_schema_ui("/properties/array")
        self.ref_schema["layout"]["elements"] = reference_schemata.insert_into_elements(
            self.ref_schema["layout"]["elements"], array_schema
        )

    def test_empty_array(self):
        self._test_schema(self.ref_schema)

    def test_children_in_array(self):
        base_scope = "/properties/" + create_id(self.array) + "/items/properties/"
        # create_content_ui.create_and_test_all_children_descendantControlOverrides(
        #     self,
        #     self.ref_schema,
        #     self.ref_schema["layout"]["elements"],
        #     self.array,
        #     base_scope,
        # )
        # TODO

    # def test_array_in_array(self):
    #     # test empty array in array
    #     nested_array = api.content.create(type="Array", title="Nested Array", container=self.array)
    #     nested_array_schema = reference_schemata.get_array_ref_schema_ui(nested_array.title)

    #     base_scope = "/properties/" + create_id(self.array) + "items/properties/"
    #     nested_scope = base_scope + create_id(nested_array)
    #     # insert nested_array_schema into descendantControlOverrides of self.array (flattened)
    #     reference_schemata.insert_schema_into_descConOv(self.array['options']['descendantControlOverrides'], nested_array_schema, nested_scope)
    #     self._test_schema(self.ref_schema)

    #     # test filled array in array
    #     base_nested_scope = nested_scope + "/items/properties/"
    #     # insert children of nested_array into descendantControlOverrides of self.array (is flattened) using base_nested_scope
    #     create_content_ui.create_and_test_all_children_descendantControlOverrides(self, self.ref_schema, self.array['options']['descendantControlOverrides'], nested_array, base_nested_scope)

    #     # test filled array in filled array
    #     # insert children of self.array into descendantControlOverrides of self.array (is flattened) using base_scope
    #     create_content_ui.create_and_test_all_children_descendantControlOverrides(self, self.ref_schema, self.array['options']['descendantControlOverrides'], self.array, base_scope)
    #     # TODO

    # NOT POSSIBLE
    # def test_fieldset_in_array(self):
    #     pass
    #     # TODO

    def test_complex_in_array(self):
        pass
        # TODO


class ViewsUiSchemaFormWithComplexTest(unittest.TestCase):
    layer = EDI_JSONFORMS_INTEGRATION_TESTING
    form = None
    view = None
    complex = None
    ref_schema = None

    def _test_schema(self, ref_schema):
        computed_schema = json.loads(self.view())
        self.assertEqual(dict(computed_schema), dict(ref_schema))

    def setUp(self):
        setUp_ui_schema_test(self)
        self.complex = api.content.create(
            type="Complex", title="Complex", container=self.form
        )
        self.ref_schema = reference_schemata.get_form_ref_schema_ui()
        complex_schema = reference_schemata.get_complex_ref_schema_ui(
            "/properties/complex"
        )
        self.ref_schema["layout"]["elements"] = reference_schemata.insert_into_elements(
            self.ref_schema["layout"]["elements"], complex_schema
        )

    def test_empty_complex(self):
        self._test_schema(self.ref_schema)

    def test_children_in_complex(self):
        base_scope = "/properties/" + create_id(self.complex) + "/properties/"

        # deprecated: children arent added to complex anymore. only their options to descendantControlOverrides
        # create_content_ui.create_and_test_all_children_descendantControlOverrides(
        #     self,
        #     self.ref_schema,
        #     self.ref_schema["layout"]["elements"],
        #     self.complex,
        #     base_scope,
        # )
        # TODO

    # def test_complex_in_complex(self):
    #     # TODO replace with create_children_test_container_in_container, also in other methods
    #     # test empty complex in complex
    #     nested_complex = api.content.create(type="Complex", title="Nested Complex", container=self.complex)
    #     nested_complex_schema = reference_schemata.get_complex_ref_schema_ui(nested_complex.title)

    #     base_scope = "/properties/" + create_id(self.complex) + "/properties/"
    #     nested_scope = base_scope + create_id(nested_complex)
    #     # insert nested_complex_schema into descendantControlOverrides of self.complex (flattened)
    #     reference_schemata.insert_schema_into_descConOv(self.complex['options']['descendantControlOverrides'], nested_complex_schema, nested_scope)
    #     self._test_schema(self.ref_schema)

    #     # test filled complex in complex
    #     base_nested_scope = nested_scope + "/properties/"
    #     # insert children of nested_complex into descendantControlOverrides of self.complex (is flattened) using base_nested_scope
    #     create_content_ui.create_and_test_all_children_descendantControlOverrides(self, self.ref_schema, self.complex['options']['descendantControlOverrides'], nested_complex, base_nested_scope)

    #     # test filled complex in filled complex
    #     # insert children of self.complex into descendantControlOverrides of self.complex (is flattened) using base_scope
    #     create_content_ui.create_and_test_all_children_descendantControlOverrides(self, self.ref_schema, self.complex['options']['descendantControlOverrides'], self.complex, base_scope)
    #     # TODO

    # def test_fieldset_in_complex(self):
    #     # test empty complex in complex
    #     nested_fieldset = api.content.create(type="Fieldset", title="Nested Fieldset", container=self.complex)
    #     nested_complex_schema = reference_schemata.get_complex_ref_schema_ui(nested_complex.title)

    #     base_scope = "/properties/" + create_id(self.complex) + "/properties/"
    #     nested_scope = base_scope + create_id(nested_complex)
    #     # insert nested_complex_schema into descendantControlOverrides of self.complex (flattened)
    #     reference_schemata.insert_schema_into_descConOv(self.complex['options']['descendantControlOverrides'], nested_complex_schema, nested_scope)
    #     self._test_schema(self.ref_schema)

    #     # test filled complex in complex
    #     base_nested_scope = nested_scope + "/properties/"
    #     # insert children of nested_complex into descendantControlOverrides of self.complex (is flattened) using base_nested_scope
    #     create_content_ui.create_and_test_all_children_descendantControlOverrides(self, self.ref_schema, self.complex['options']['descendantControlOverrides'], nested_complex, base_nested_scope)

    #     # test filled complex in filled complex
    #     # insert children of self.complex into descendantControlOverrides of self.complex (is flattened) using base_scope
    #     create_content_ui.create_and_test_all_children_descendantControlOverrides(self, self.ref_schema, self.complex['options']['descendantControlOverrides'], self.complex, base_scope)
    #     # TODO

    def test_array_in_complex(self):
        pass
        # TODO


class ViewsUiSchemaNestedTest(unittest.TestCase):
    layer = EDI_JSONFORMS_INTEGRATION_TESTING
    form = None
    view = None

    def setUp(self):
        setUp_ui_schema_test(self)

    def _test_schema(self, ref_schema):
        computed_schema = json.loads(self.view())
        self.assertEqual(dict(computed_schema), dict(ref_schema))

    def _create_all_container(self, ref_schema, elements, container):
        fieldset = api.content.create(
            type="Fieldset", title="Fieldset", container=self.form
        )
        array = api.content.create(type="Array", title="Array", container=self.form)
        complex = api.content.create(
            type="Complex", title="Complex", container=self.form
        )
        # TODO

    def test_nested(self):
        pass
        # self._create_all_container()
        # TODO


class ViewsUiSchemaShowOnTest(unittest.TestCase):
    layer = EDI_JSONFORMS_INTEGRATION_TESTING
    form = None
    view = None

    def setUp(self):
        setUp_ui_schema_test(self)


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
        computed_schema = json.loads(self.view())["properties"]

    def setUp(self):
        setUp_ui_schema_test(self)
        # self.field = api.content.create(type="Field", title="a field", container=self.form)

    def test_textlike_showon_properties(self):
        pass
