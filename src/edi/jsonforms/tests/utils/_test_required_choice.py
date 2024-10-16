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


"""
requirements:
    * TestClass that calls the test_required_choice() function needs a self.field = [] with all the fields that can be required/optional

    len(self.field) must be at least 3
"""


def _test_required(self, ref_required):
    computed_schema = {'required': json.loads(self.view())['required']}
    ref_schema = {'required': ref_required}
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
    ref_required = [create_id(self.field[0]), create_id(self.field[1]), create_id(self.field[2])]
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
        computed_schema = computed_schema['properties'][parent_id]['items']
    elif parent_id:
        computed_schema = computed_schema['properties'][parent_id]
    required_list = computed_schema['required']
    context.assertIn(id, required_list)

def test_object_not_required(context, id, parent_id=None, parent_type=None):
    computed_schema = json.loads(context.view())
    if parent_id and parent_type == "Array":
        computed_schema = computed_schema['properties'][parent_id]['items']
    elif parent_id:
        computed_schema = computed_schema['properties'][parent_id]
    required_list = computed_schema['required']
    context.assertNotIn(id, required_list)

"""
ref_schema needs to be of type {'id-of-object': {... schema ...}}

test_schema_method must be of type test_schema_method(ref_schema)

object can be of portal_type Array or Complex
"""
def test_object_children_required(self, obj, ref_schema, test_schema_method):
    obj_id = create_id(obj)
    is_array = obj.portal_type == "Array"

    # save original schema
    tmp_ref_schema = copy.deepcopy(ref_schema)

    if is_array:
        ref_schema[obj_id]['items']['required'] = []
    else:
        ref_schema[obj_id]['required'] = []

    # test that each child is required
    for child in obj.getFolderContents():
        child = child.getObject()
        if child.portal_type == "Complex":
            continue
        child_id = create_id(child)

        # test that object is not in required-list
        test_object_not_required(self, obj_id)

        # test that child is in the required-list of the object
        child.required_choice = "required"
        if is_array:
            ref_schema[obj_id]['items']['required'].append(child_id)
        else:
            ref_schema[obj_id]['required'].append(child_id)
        if child.portal_type == "Array":
            if is_array:
                ref_schema[obj_id]['items']['properties'][child_id]['minItems'] = 1
            else:
                ref_schema[obj_id]['properties'][child_id]['minItems'] = 1
        test_schema_method(ref_schema)

        # test that each child and the object are required
        if is_array:
            obj.required_choice = "required"
            ref_schema[obj_id]['minItems'] = 1
            test_object_required(self, obj_id)
        test_schema_method(ref_schema)

        # revert required-status
        child.required_choice = "optional"
        if is_array:
            obj.required_choice = "optional"
            ref_schema[obj_id]['items']['required'] = []
            del ref_schema[obj_id]['minItems']
        else:
            ref_schema[obj_id]['required'] = []
        if child.portal_type == "Array":
            del ref_schema[obj_id]['items']['properties'][child_id]['minItems']
        

    # test that all children are required
    for child in obj.getFolderContents():
        child = child.getObject()
        if child.portal_type == "Complex":
            continue
        child_id = create_id(child)

        # test that object is not in required-list
        test_object_not_required(self, obj_id)

        # test that child is in the required-list of the object
        child.required_choice = "required"
        if is_array:
            ref_schema[obj_id]['items']['required'].append(child_id)
        else:
            ref_schema[obj_id]['required'].append(child_id)
        if child.portal_type == "Array":
            ref_schema[obj_id]['items']['properties'][child_id]['minItems'] = 1
        test_schema_method(ref_schema)

        # test that each child and the object are required
        if is_array:
            obj.required_choice = "required"
            ref_schema[obj_id]['minItems'] = 1
            test_object_required(self, obj_id)
        test_schema_method(ref_schema)

        # revert required-status of object
        if is_array:
            obj.required_choice = "optional"
            del ref_schema[obj_id]['minItems']

    # restore original schema
    import pdb; pdb.set_trace()
    ref_schema = tmp_ref_schema
    for child in obj.getFolderContents():
        child = child.getObject()
        if child.portal_type != "Complex":
            child.required_choice = "optional"

