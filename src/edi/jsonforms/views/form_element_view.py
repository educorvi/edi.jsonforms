# -*- coding: utf-8 -*-

from edi.jsonforms import _
import json
from zope.interface import implementer
from zope.interface import Interface

from edi.jsonforms.views.form_view import FormView
from edi.jsonforms.views.ui_schema_view import UiSchemaView
from edi.jsonforms.views.json_schema_view import JsonSchemaView


class FormElementView(FormView):
    def __call__(self):
        return self.index()

    def empty_selection_field(self) -> bool:
        """Check if a field is a selection field and if it has options."""
        context = self.context
        if context.portal_type == "SelectionField":
            options = context.getFolderContents()
            if len(options) == 0:
                return True
        return False

    def form_element_uischema(self) -> str:
        form_element_uischema = FormElementUiSchema(self.context, self.request)()
        return form_element_uischema

    def form_element_jsonschema(self) -> str:
        form_element_jsonschema = FormElementJsonSchema(self.context, self.request)()
        return form_element_jsonschema


class IFormElementView(Interface):
    """Marker Interface for IFormElementView"""


@implementer(IFormElementView)
class FormElementUiSchema(UiSchemaView):
    def __init__(self, context, request):
        super().__init__(context, request)

    def __call__(self):
        uischema = self.ui_schema_without_showon()
        return json.dumps(uischema, ensure_ascii=False, indent=4)

    def ui_schema_without_showon(self):
        self.set_ui_base_schema()

        object = self.context
        self.add_child_to_schema(object, self.uischema)

        # TODO refactor in the same way as in FormElementJsonSchema (use is_single_view=True to ignore all dependencies instead of removing showOn)
        def remove_showon(dictionary):
            if isinstance(dictionary, dict):
                if "showOn" in dictionary:
                    del dictionary["showOn"]
                for key, value in dictionary.items():
                    remove_showon(value)
            elif isinstance(dictionary, list):
                for item in dictionary:
                    remove_showon(item)

        remove_showon(self.uischema)

        return self.uischema


@implementer(IFormElementView)
class FormElementJsonSchema(JsonSchemaView):
    def __init__(self, context, request):
        super().__init__(context, request)
        self.is_single_view = True

    def __call__(self):
        jsonschema = self.json_schema()
        return json.dumps(jsonschema, ensure_ascii=False, indent=4)

    def json_schema(self):
        self.set_json_base_schema()

        object = self.context
        self.add_child_to_schema(object, self.jsonschema)
        return self.jsonschema
