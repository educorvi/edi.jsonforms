from plone import api

import json

from edi.jsonforms.views.common import create_id
import edi.jsonforms.tests.utils.reference_schemata as reference_schemata
from edi.jsonforms.content.field import Answer_types
from edi.jsonforms.content.selection_field import Selection_answer_types

"""
ref_schema (dict): whole ui-schema
elements (list of dict elements (part of ui-schema)): the elements where to add the children
container (string): to which container to add the children
content_type (string): of the children to add
answer_types (list of strings): of the children
base_scope (string): of the children
"""


def create_and_test_children(
    self, ref_schema, elements, container, content_type, answer_types, base_scope
):
    for t in answer_types:
        t = t.value if hasattr(t, "value") else t
        field = api.content.create(
            type=content_type, title=t + "_" + content_type, container=container
        )
        field.answer_type = t

        scope = base_scope + create_id(field)
        child_schema = reference_schemata.get_child_ref_schema_ui(t, scope)
        elements = reference_schemata.insert_into_elements(elements, child_schema)

        # test schema
        computed_schema = json.loads(self.view())
        self.assertEqual(dict(computed_schema), dict(ref_schema))


def create_and_test_all_children(self, ref_schema, elements, container, base_scope):
    # test fields in fieldset
    create_and_test_children(
        self, ref_schema, elements, container, "Field", Answer_types, base_scope
    )

    # test selectionfields in fieldset
    create_and_test_children(
        self,
        ref_schema,
        elements,
        container,
        "SelectionField",
        Selection_answer_types,
        base_scope,
    )

    # test uploadfields in fieldset
    create_and_test_children(
        self,
        ref_schema,
        elements,
        container,
        "UploadField",
        ["file"],
        base_scope,
    )


"""
container: content_type Array or Complex
descendantControlOverrides needs the keys: "options":{"descendantControlOverrides":{}}
ref_schema: the full schema of the form
descendantControlOverrides is part of the ref_schema
"""


def create_and_test_children_descendantControlOverrides(
    self,
    ref_schema: dict,
    descendantControlOverrides: dict,
    container: type,
    content_type: type,
    answer_types: list,
    base_scope: str,
):
    for t in answer_types:
        t = t.value if hasattr(t, "value") else t
        field = api.content.create(
            type=content_type, title=t + "_" + content_type, container=container
        )
        field.answer_type = t

        scope = base_scope + create_id(field)
        child_schema = reference_schemata.get_child_ref_schema_ui(t, scope)

        reference_schemata.insert_schema_into_descConOv(
            descendantControlOverrides, child_schema, scope
        )

        # test schema
        computed_schema = json.loads(self.view())
        self.assertEqual(dict(computed_schema), dict(ref_schema))


"""
container: content_type Array or Complex
descendantControlOverrides needs the keys: "options":{"descendantControlOverrides":{}}
ref_schema: the full schema of the form
descendantControlOverrides is part of the ref_schema
"""


def create_and_test_all_children_descendantControlOverrides(
    self,
    ref_schema: dict,
    descendantControlOverrides: dict,
    container: type,
    base_scope: str,
):
    # test fields in fieldset
    create_and_test_children(
        self,
        ref_schema,
        descendantControlOverrides,
        container,
        "Field",
        Answer_types,
        base_scope,
    )

    # test selectionfields in fieldset
    create_and_test_children(
        self,
        ref_schema,
        descendantControlOverrides,
        container,
        "SelectionField",
        Selection_answer_types,
        base_scope,
    )

    # test uploadfields in fieldset
    create_and_test_children(
        self,
        ref_schema,
        descendantControlOverrides,
        container,
        "UploadField",
        ["file"],
        base_scope,
    )


"""
descendantControlOverrides: part of ref_schema in which to insert nested_schema of nested container
nested_scope: scope of nested container
base_scope: scope of container
part_of_scope: "/properties/" for complex or "/properties/items/"
"""
# def create_children_test_container_in_container(self, ref_schema, descendantControlOverrides: dict, nested_schema: dict, nested_scope: str, base_scope: str, part_of_scope: str):
#     # insert schema into descendantControlOverrides of container (flattened)
#     reference_schemata.insert_schema_into_descConOv(descendantControlOverrides, nested_schema, nested_scope)

#     # test schema
#     computed_schema = json.loads(self.view())
#     self.assertEqual(dict(computed_schema), dict(ref_schema))

#     # test filled container in container
#     base_nested_scope = nested_scope + "/properties/"
#     # insert children of nested_complex into descendantControlOverrides of self.complex (is flattened) using base_nested_scope
#     create_content_ui.create_and_test_all_children_descendantControlOverrides(self, self.ref_schema, self.complex['options']['descendantControlOverrides'], nested_complex, base_nested_scope)

#     # test filled complex in filled complex
#     # insert children of self.complex into descendantControlOverrides of self.complex (is flattened) using base_scope
#     create_content_ui.create_and_test_all_children_descendantControlOverrides(self, self.ref_schema, self.complex['options']['descendantControlOverrides'], self.complex, base_scope)
