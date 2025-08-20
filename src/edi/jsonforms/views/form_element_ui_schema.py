# -*- coding: utf-8 -*-

# from edi.jsonforms import _
import json
from zope.interface import implementer
from zope.interface import Interface

from edi.jsonforms.views.ui_schema_view import UiSchemaView

class IFormElementView(Interface):
    """ Marker Interface for IFormElementView"""


@implementer(IFormElementView)
# class FormElementUiSchemaView(UiSchemaView):
class FormElementUiSchema(UiSchemaView):

    def __init__(self, context, request):
        super().__init__(context, request)

    def __call__(self):
        uischema = self.ui_schema_without_showon()
        return json.dumps(uischema, ensure_ascii=False, indent=4)

    def ui_schema_without_showon(self):
        self.set_ui_base_schema()

        object = self.context
        self.add_child_to_schema(object)

        def remove_showon(dictionary):
            if isinstance(dictionary, dict):
                if 'showOn' in dictionary:
                    del dictionary['showOn']
                for key, value in dictionary.items():
                    remove_showon(value)
            elif isinstance(dictionary, list):
                for item in dictionary:
                    remove_showon(item)

        remove_showon(self.uischema)

        return self.uischema
