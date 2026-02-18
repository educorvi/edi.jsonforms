# -*- coding: utf-8 -*-
from edi.jsonforms.testing import EDI_JSONFORMS_INTEGRATION_TESTING
from plone import api
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from zope.component import getMultiAdapter
from zope.interface.interfaces import ComponentLookupError

import copy
import json

from edi.jsonforms.views.common import create_id
from edi.jsonforms.views.pydantic_models.FieldModel import string_type_fields


"""
requirements:
    * TestClass that calls the test_required_choice() function needs a self.field = [] with all the fields that can be required/optional

    len(self.field) must be at least 3
"""


def _test_required(self, ref_required):
    computed_schema = json.loads(self.view())
    if len(ref_required) == 0:
        self.assertNotIn("required", computed_schema)
        return
    computed_schema = {"required": computed_schema["required"]}
    ref_schema = {"required": ref_required}
    self.assertEqual(dict(computed_schema), dict(ref_schema))


def test_zero_required_choice(self):
    ref_required = []
    _test_required(self, ref_required)


def test_one_required_choice(self):
    self.field[0].required_choice = "required"
    ref_required = [create_id(self.field[0])]
    _test_required(self, ref_required)

    self.field[0].required_choice = "optional"
    self.field[1].required_choice = "required"
    ref_required = [create_id(self.field[1])]
    _test_required(self, ref_required)

    self.field[1].required_choice = "optional"
    self.field[2].required_choice = "required"
    ref_required = [create_id(self.field[2])]

    _test_required(self, ref_required)


def test_two_required_choice(self):
    id_0 = create_id(self.field[0])
    id_1 = create_id(self.field[1])
    id_2 = create_id(self.field[2])

    self.field[0].required_choice = "required"
    self.field[1].required_choice = "required"
    ref_required = [id_0, id_1]
    _test_required(self, ref_required)

    self.field[0].required_choice = "optional"
    self.field[1].required_choice = "required"
    self.field[2].required_choice = "required"
    ref_required = [id_1, id_2]
    _test_required(self, ref_required)

    self.field[1].required_choice = "optional"
    self.field[2].required_choice = "required"
    self.field[0].required_choice = "required"
    ref_required = [id_0, id_2]
    _test_required(self, ref_required)


def test_three_required_choice(self):
    self.field[0].required_choice = "required"
    self.field[1].required_choice = "required"
    self.field[2].required_choice = "required"
    ref_required = [
        create_id(self.field[0]),
        create_id(self.field[1]),
        create_id(self.field[2]),
    ]
    _test_required(self, ref_required)


def test_required_choices(self):
    for f in self.field:
        f.required_choice = "optional"
    test_zero_required_choice(self)
    test_one_required_choice(self)
    for f in self.field:
        f.required_choice = "optional"
    test_two_required_choice(self)
    for f in self.field:
        f.required_choice = "optional"
    test_three_required_choice(self)


def test_object_required(context, id, parent_id=None, parent_type=None):
    computed_schema = json.loads(context.view())
    if parent_id and parent_type == "Array":
        computed_schema = computed_schema["properties"][parent_id]["items"]
    elif parent_id:
        computed_schema = computed_schema["properties"][parent_id]
    required_list = computed_schema["required"]
    context.assertIn(id, required_list)


def test_object_not_required(context, id, parent_id=None, parent_type=None):
    computed_schema = json.loads(context.view())
    if parent_id and parent_type == "Array":
        computed_schema = computed_schema["properties"][parent_id]["items"]
    elif parent_id:
        computed_schema = computed_schema["properties"][parent_id]
    if "required" not in computed_schema:
        return
    required_list = computed_schema["required"]
    context.assertNotIn(id, required_list)


def set_child_required(child, child_id, schema, parent_id):
    """
    schema is the schema of the parent of the child (with {parent_id: {...}})
    helper function to set a child required and add the child to the required-list of the parent in the ref_schema
    """
    is_array = "items" in schema[parent_id]
    if is_array and "required" not in schema[parent_id]["items"]:
        schema[parent_id]["items"]["required"] = []
    elif not is_array and "required" not in schema[parent_id]:
        schema[parent_id]["required"] = []

    child.required_choice = "required"
    if is_array:
        schema[parent_id]["items"]["required"].append(child_id)
    else:
        schema[parent_id]["required"].append(child_id)
    if child.portal_type == "Array" or (
        child.portal_type == "SelectionField" and child.answer_type == "checkbox"
    ):
        if is_array:
            schema[parent_id]["items"]["properties"][child_id]["minItems"] = 1
        else:
            schema[parent_id]["properties"][child_id]["minItems"] = 1

    if child.portal_type == "Field" and child.answer_type in string_type_fields:
        if is_array:
            schema[parent_id]["items"]["properties"][child_id]["minLength"] = 1
        else:
            schema[parent_id]["properties"][child_id]["minLength"] = 1

    return schema


"""
ref_schema needs to be of type {'id-of-object': {... schema ...}}

test_schema_method must be of type test_schema_method(ref_schema)

object can be of portal_type Array or Complex

ref_schema isn't changed
"""


def test_object_children_required(self, obj, ref_schema, test_schema_method):
    obj_id = create_id(obj)
    is_array = obj.portal_type == "Array"

    # save original schema
    ref_schema_copy = copy.deepcopy(ref_schema)

    if is_array:
        ref_schema_copy[obj_id]["items"]["required"] = []
    else:
        ref_schema_copy[obj_id]["required"] = []

    # test that each child is required
    for child in obj.getFolderContents():
        child = child.getObject()
        if child.portal_type == "Complex":
            continue
        child_id = create_id(child)

        # test that object is not in required-list
        test_object_not_required(self, obj_id)

        # test that child is in the required-list of the object
        set_child_required(child, child_id, ref_schema_copy, obj_id)
        test_schema_method(ref_schema_copy)

        # test that each child and the object are required
        if is_array:
            obj.required_choice = "required"
            ref_schema_copy[obj_id]["minItems"] = 1
            test_object_required(self, obj_id)
            test_schema_method(ref_schema_copy)

        # revert required-status
        child.required_choice = "optional"
        if is_array:
            obj.required_choice = "optional"
            ref_schema_copy[obj_id]["items"]["required"] = []
            del ref_schema_copy[obj_id]["minItems"]
        else:
            ref_schema_copy[obj_id]["required"] = []
        if child.portal_type == "Array" or (
            child.portal_type == "SelectionField" and child.answer_type == "checkbox"
        ):
            if is_array:
                del ref_schema_copy[obj_id]["items"]["properties"][child_id]["minItems"]
            else:
                del ref_schema_copy[obj_id]["properties"][child_id]["minItems"]
        if child.portal_type == "Field" and child.answer_type in string_type_fields:
            if is_array:
                del ref_schema_copy[obj_id]["items"]["properties"][child_id][
                    "minLength"
                ]
            else:
                del ref_schema_copy[obj_id]["properties"][child_id]["minLength"]

    # test that all children are required
    for child in obj.getFolderContents():
        child = child.getObject()
        if child.portal_type == "Complex":
            continue
        child_id = create_id(child)

        # test that object is not in required-list
        test_object_not_required(self, obj_id)

        # test that child is in the required-list of the object
        ref_schema_copy = set_child_required(child, child_id, ref_schema_copy, obj_id)
        test_schema_method(ref_schema_copy)

        # test that each child and the object are required
        if is_array:
            obj.required_choice = "required"
            ref_schema_copy[obj_id]["minItems"] = 1
            test_object_required(self, obj_id)
            test_schema_method(ref_schema_copy)

        # revert required-status of object
        if is_array:
            obj.required_choice = "optional"
            del ref_schema_copy[obj_id]["minItems"]

    # restore original state
    for child in obj.getFolderContents():
        child = child.getObject()
        if child.portal_type != "Complex":
            child.required_choice = "optional"
