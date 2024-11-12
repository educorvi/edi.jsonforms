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

from edi.jsonforms.tests.utils._test_schema_views import test_json_schema_view_is_registered, test_json_schema_view_not_matching_interface, setUp_integration_test, setUp_ui_schema_test
from edi.jsonforms.tests.utils import create_content_ui
import edi.jsonforms.tests.utils.reference_schemata as reference_schemata
from edi.jsonforms.content.field import Answer_types
from edi.jsonforms.content.selection_field import Selection_answer_types
from edi.jsonforms.content.upload_field import Upload_answer_types
from edi.jsonforms.views.common import create_id
from edi.jsonforms.content.field import IField




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

    def test_fields_in_form(self):
        ref_schema = reference_schemata.get_form_ref_schema_ui()
        create_content_ui.create_and_test_children(self, ref_schema, ref_schema['layout']['elements'], self.form, "Field", Answer_types, "/properties/")

    def test_selectionfields_in_form(self):
        ref_schema = reference_schemata.get_form_ref_schema_ui()
        create_content_ui.create_and_test_children(self, ref_schema, ref_schema['layout']['elements'], self.form, "SelectionField", Selection_answer_types, "/properties/")
        for sf in self.form.getFolderContents():
            sf = sf.getObject()
            api.content.create(type="Option", title="opt_" + sf.answer_type, container=sf)
        self._test_schema(ref_schema)

    def test_uploadfields_in_form(self):
        ref_schema = reference_schemata.get_form_ref_schema_ui()
        create_content_ui.create_and_test_children(self, ref_schema, ref_schema['layout']['elements'], self.form, "UploadField", Upload_answer_types, "/properties/")

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
            child_schema = reference_schemata.get_child_ref_schema_ui(field_type, "/properties/" + create_id(field), field.title)
            if 'options' in child_schema:
                child_schema['options'][option_label] = option
            else:
                child_schema['options'] = {option_label: option}

            buttons = copy.deepcopy(ref_schema['layout']['elements'])
            ref_schema['layout']['elements'] = reference_schemata.insert_into_elements(ref_schema['layout']['elements'], child_schema)
            self._test_schema(ref_schema)
            ref_schema['layout']['elements'] = buttons

    def test_unit_of_fields(self):
        field = api.content.create(type="Field", title="field", container=self.form)
        field.unit = "unit"
        self._test_options(field, ["number", "integer"], "append", field.unit)

    def test_placeholder_of_fields(self):
        field = api.content.create(type="Field", title="field", container=self.form)
        field.placeholder = "placeholder"
        self._test_options(field, ["text", "textarea", "password", "tel", "url", "email"], "placeholder", field.placeholder)

    def test_acceptedfiletypes_for_uploadfields(self):
        uploadfield = api.content.create(type="UploadField", title="uploadfield", container=self.form)
        uploadfield.accepted_file_types = ["pdf", "png"]
        self._test_options(uploadfield, ["file", "file-multi"], "acceptedFileType", uploadfield.accepted_file_types)


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
        self.fieldset = api.content.create(type="Fieldset", title="Fieldset", container=self.form)
        self.ref_schema = reference_schemata.get_form_ref_schema_ui()
        fieldset_schema = reference_schemata.get_fieldset_ref_schema_ui(self.fieldset.title)
        self.ref_schema['layout']['elements'] = reference_schemata.insert_into_elements(self.ref_schema['layout']['elements'], fieldset_schema)

    def test_empty_fieldset(self):
        self._test_schema(self.ref_schema)

    def test_children_in_fieldset(self):
        create_content_ui.create_and_test_all_children(self, self.ref_schema, self.ref_schema['layout']['elements'][0]['elements'], self.fieldset, "/properties/")

    def test_fieldset_in_fieldset(self):
        # test empty fieldset in fieldset
        nested_fieldset = api.content.create(type="Fieldset", title="Nested Fieldset", container=self.fieldset)
        nested_fieldset_schema = reference_schemata.get_fieldset_ref_schema_ui(nested_fieldset.title)
        self.ref_schema['layout']['elements'][0]['elements'] = reference_schemata.insert_into_elements(self.ref_schema['layout']['elements'][0]['elements'], nested_fieldset_schema)
        self._test_schema(self.ref_schema)

        # test filled fieldset in fieldset
        create_content_ui.create_and_test_all_children(self, self.ref_schema, self.ref_schema['layout']['elements'][0]['elements'][0]['elements'], nested_fieldset, "/properties/")

        # test filled fieldset in filled fieldset
        create_content_ui.create_and_test_all_children(self, self.ref_schema, self.ref_schema['layout']['elements'][0]['elements'], self.fieldset, "/properties/")

    def test_array_in_fieldset(self):
        pass
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
        self.array = api.content.create(type="Array", title="Array", container=self.form)
        self.ref_schema = reference_schemata.get_form_ref_schema_ui()
        array_schema = reference_schemata.get_array_ref_schema_ui("/properties/")
        self.ref_schema['layout']['elements'] = reference_schemata.insert_into_elements(self.ref_schema['layout']['elements'], array_schema)

    def test_empty_array(self):
        pass
        # TODO
        # self._test_schema(self.ref_schema)

    def test_children_in_array(self):
        pass
        # TODO

    def test_array_in_array(self):
        pass
        # TODO

    def test_fieldset_in_array(self):
        pass
        # TODO

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
        self.complex = api.content.create(type="Complex", title="Complex", container=self.form)
        self.ref_schema = reference_schemata.get_form_ref_schema_ui()
        complex_schema = reference_schemata.get_complex_ref_schema_ui("/properties/")
        self.ref_schema['layout']['elements'] = reference_schemata.insert_into_elements(self.ref_schema['layout']['elements'], complex_schema)

    def test_empty_complex(self):
        pass
        # TODO
        # self._test_schema(self.ref_schema)

    def test_children_in_complex(self):
        pass
        # TODO

    def test_complex_in_complex(self):
        pass
        # TODO

    def test_fieldset_in_complex(self):
        pass
        # TODO

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
        fieldset = api.content.create(type="Fieldset", title="Fieldset", container=self.form)
        array = api.content.create(type="Array", title="Array", container=self.form)
        complex = api.content.create(type="Complex", title="Complex", container=self.form)
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
        computed_schema = json.loads(self.view())['properties']

    def setUp(self):
        setUp_ui_schema_test(self)
        # self.field = api.content.create(type="Field", title="a field", container=self.form)

    def test_textlike_showon_properties(self):
        pass