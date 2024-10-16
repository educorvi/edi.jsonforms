from plone import api

from edi.jsonforms.content.field import Answer_types
from edi.jsonforms.content.selection_field import Selection_answer_types
from edi.jsonforms.content.upload_field import Upload_answer_types
from edi.jsonforms.views.common import create_id

import edi.jsonforms.tests.utils.reference_schemata as reference_schemata



"""
creates one child of type type (Field or SelectionField or UploadField) with the given answer_type in the given Array- or Object-Container

if the child is of type SelectionField, two Options will be created in that child as well

ref_schema has to be of type {id-of-object-container: { ... }, ...}
"""
def create_child_in_object(ref_schema, type, answer_type, container):
    child = api.content.create(type=type, title="title_" + str(answer_type), container=container)
    child_id = create_id(child)
    child.answer_type = answer_type
    child_ref_schema = reference_schemata.get_child_ref_schema(child.answer_type, child.title)

    if type == "SelectionField":
        api.content.create(type="Option", title="yes", container=child)
        api.content.create(type="Option", title="no", container=child)
        if child.answer_type in ["radio", "select"]:
            child_ref_schema['enum'] = ["yes", "no"]
        elif child.answer_type in ["checkbox", "selectmultiple"]:
            child_ref_schema['items']['enum'] = ["yes", "no"]

    if container.portal_type == "Array":
        ref_schema[create_id(container)]['items']['properties'][child_id] = child_ref_schema
    else:
        ref_schema[create_id(container)]['properties'][child_id] = child_ref_schema
    return ref_schema


"""
creates a child of type Array or Complex in the given Array- or Object-Container

ref_schema has to be of type {id-of-object-container: { ... }, ...}
"""
def create_containerchild_in_object(ref_schema, type, container, title=None):
    if title == None:
        if type == "Array":
            title = "an array"
        elif type == "Complex":
            title = "a complex object"

    child = api.content.create(type=type, title=title, container=container)
    child_id = create_id(child)
    child_ref_schema = reference_schemata.get_child_ref_schema(child.title)

    if container.portal_type == "Array":
        ref_schema[create_id(container)]['items']['properties'][child_id] = child_ref_schema
    else:
        ref_schema[create_id(container)]['properties'][child_id] = child_ref_schema
    return ref_schema


"""
creates all types of Fields, SelectionFields and UploadFields inside the given Array- or Object-Container
the ref_schema has to be of type {id-of-object-container: { ... }, ...}
"""
def create_all_child_types_in_object(ref_schema, container):
    container_id = create_id(container)

    # Fields
    for type in Answer_types:
        type = type.value
        ref_schema = create_child_in_object(ref_schema, "Field", type, container)

    # SelectionFields
    for type in Selection_answer_types:
        type = type.value
        ref_schema = create_child_in_object(ref_schema, "SelectionField", type, container)

    # UploadFields
    for type in Upload_answer_types:
        type = type.value
        ref_schema = create_child_in_object(ref_schema, "UploadField", type, container)

    return ref_schema

