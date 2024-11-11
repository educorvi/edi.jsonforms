from plone import api

import json

from edi.jsonforms.views.common import create_id
import edi.jsonforms.tests.utils.reference_schemata as reference_schemata

"""
ref_schema: whole ui-schema
elements: the elements where to add the children
container: to which container to add the children
content_type: of the children to add
answer_types: of the children
base_scope: of the children
"""
def create_and_test_children(self, ref_schema, elements, container, content_type, answer_types, base_scope):
        for t in answer_types:
            t = t.value
            field = api.content.create(type=content_type, title=t + "_field", container=container)
            field.answer_type = t

            scope = base_scope + create_id(field)
            child_schema = reference_schemata.get_child_ref_schema_ui(t, scope)
            elements = reference_schemata.insert_into_elements(elements, child_schema)

            # test schema
            computed_schema = json.loads(self.view())
            self.assertEqual(dict(computed_schema), dict(ref_schema))