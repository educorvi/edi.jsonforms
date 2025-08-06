# -*- coding: utf-8 -*-

# from edi.jsonforms import _
import json
from Products.Five.browser import BrowserView
from zope.interface import implementer
from zope.interface import Interface

from edi.jsonforms.views.ui_schema_view import UiSchemaView

# from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

class IFormElementView(Interface):
    """ Marker Interface for IFormElementView"""


@implementer(IFormElementView)
# class FormElementUiSchemaView(UiSchemaView):
class FormElementUiSchema(UiSchemaView):

    def __init__(self, context, request):
        super().__init__(context, request)

    def __call__(self):
        uischema = self.ui_schema()
        return json.dumps(uischema, ensure_ascii=False, indent=4)

    def ui_schema(self):
        self.set_ui_base_schema()

        object = self.context
        self.add_child_to_schema(object)
        return self.uischema
