from plone import api

import json

from edi.jsonforms.views.common import create_id
import edi.jsonforms.tests.utils.reference_schemata as reference_schemata
from edi.jsonforms.content.field import Answer_types
from edi.jsonforms.content.selection_field import Selection_answer_types
from edi.jsonforms.content.upload_field import Upload_answer_types

"""
ref_schema (dict): whole ui-schema
elements (list of dict elements (part of ui-schema)): the elements where to add the children
container (string): to which container to add the children
content_type (string): of the children to add
answer_types (list of strings): of the children
base_scope (string): of the children
"""
def create_and_test_children(self, ref_schema, elements, container, content_type, answer_types, base_scope):
    has_buttons_element = container.portal_type == "Form"
    for t in answer_types:
        t = t.value
        field = api.content.create(type=content_type, title=t + "_" + content_type, container=container)
        field.answer_type = t

        scope = base_scope + create_id(field)
        child_schema = reference_schemata.get_child_ref_schema_ui(t, scope)
        elements = reference_schemata.insert_into_elements(elements, child_schema, has_buttons_element)

        # test schema
        computed_schema = json.loads(self.view())
        self.assertEqual(dict(computed_schema), dict(ref_schema))

def create_and_test_all_children(self, ref_schema, elements, container, base_scope):
    # test fields in fieldset
        create_and_test_children(self, ref_schema, elements, container, "Field", Answer_types, base_scope)

        # test selectionfields in fieldset
        create_and_test_children(self, ref_schema, elements, container, "SelectionField", Selection_answer_types, base_scope)

        # test uploadfields in fieldset
        create_and_test_children(self, ref_schema, elements, container, "UploadField", Upload_answer_types, base_scope)