# -*- coding: utf-8 -*-

# from edi.jsonforms import _
import json
from Products.Five.browser import BrowserView
from zope.interface import implementer
from zope.interface import Interface

from edi.jsonforms.content.form import Form
from edi.jsonforms.views.json_schema_view import JsonSchemaView
from edi.jsonforms.views.common import check_show_condition_in_request

from edi.jsonforms import _

# from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

class IFormElementView(Interface):
    """ Marker Interface for IFormElementView"""


@implementer(IFormElementView)
# class FormElementUiSchemaView(UiSchemaView):
class FormElementJsonSchema(JsonSchemaView):

    def __init__(self, context, request):
        super().__init__(context, request)

    def __call__(self):
        jsonschema = self.json_schema()
        return json.dumps(jsonschema, ensure_ascii=False, indent=4)
    
    def json_schema(self):
        self.set_json_base_schema(Form(title=_("Single View")))

        object = self.context
        self.add_child_to_schema(object)
        self.check_duplicates()
        return self.jsonschema
