from plone import api

from edi.jsonforms.content.field import Answer_types
from edi.jsonforms.content.selection_field import Selection_answer_types
from edi.jsonforms.content.upload_field import Upload_answer_types
from edi.jsonforms.views.common import create_id

import edi.jsonforms.tests.utils.reference_schemata as reference_schemata



"""
creates one child of type type (Field or SelectionField or UploadField) with the given answer_type in the given Array-Container

ref_schema has to be of type {id-of-array-container: { ... }, ...}
"""
def create_child_in_array(ref_schema, type, answer_type, container):
    child = api.content.create(type=type, title="title_" + str(answer_type), container=container)
    child.answer_type = answer_type
    child_ref_schema = reference_schemata.get_child_ref_schema(child.answer_type, child.title)
    ref_schema[create_id(container)]['items']['properties'][create_id(child)] = child_ref_schema
    return ref_schema


"""
creates all types of Fields, SelectionFields and UploadFields inside the given Array-Container
the ref_schema has to be of type {id-of-array-container: { ... }, ...}
"""
def create_all_child_types(ref_schema, container):
    container_id = create_id(container)

    # Fields
    for type in Answer_types:
        type = type.value
        ref_schema = create_child_in_array(ref_schema, "Field", type, container)

    # SelectionFields
    for type in Selection_answer_types:
        type = type.value
        ref_schema = create_child_in_array(ref_schema, "SelectionField", type, container)

        # Options
        child = container.getFolderContents()[-1].getObject()
        api.content.create(type="Option", title="yes", container=child)
        api.content.create(type="Option", title="no", container=child)
        if type in ["radio", "select"]:
            ref_schema[container_id]['items']['properties'][create_id(child)]['enum'] = ["yes", "no"]
        elif type in ["checkbox", "selectmultiple"]:
            ref_schema[container_id]['items']['properties'][create_id(child)]['items']['enum'] = ["yes", "no"]

    # UploadFields
    for type in Upload_answer_types:
        type = type.value
        ref_schema = create_child_in_array(ref_schema, "UploadField", type, container)

    return ref_schema

