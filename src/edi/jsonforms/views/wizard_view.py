# -*- coding: utf-8 -*-

# from edi.jsonforms import _
import copy
import json
from Products.Five.browser import BrowserView
from zope.interface import implementer
from zope.interface import Interface

from edi.jsonforms.views.json_schema_view import JsonSchemaView
from edi.jsonforms.views.ui_schema_view import UiSchemaView
from edi.jsonforms.views.common import create_id

class IWizardView(Interface):
    """ Marker Interface for IWizardView"""

@implementer(IWizardView)
class WizardView(BrowserView):
    def __call__(self):
        self.jsonschema = WizardJsonSchemaView(self.context, self.request)()
        self.uischema = WizardUiSchemaView(self.context, self.request)()
        return self.index()


class WizardUiSchemaView(UiSchemaView):

    def __init__(self, context, request):
        super().__init__(context, request)

    def __call__(self):
        uischema = self.combined_ui_schema()
        return json.dumps(uischema, ensure_ascii=False, indent=4)

    def combined_ui_schema(self):
        self.set_ui_base_schema()
        VERTICAL_LAYOUT = copy.deepcopy(self.uischema)

        object = self.context
        for form in object.listFolderContents():
            if form.portal_type == 'Form':
                title_schema = self.helptext_schema(f'<h2>{form.title}</h1>')
                self.uischema['layout']['elements'].append(title_schema)
                vertical_layout = copy.deepcopy(VERTICAL_LAYOUT)
                form_id = create_id(form)
                for child in form.getFolderContents():
                    self.add_child_to_schema(child.getObject(), vertical_layout, f'/properties/{form_id}/properties/')
                self.uischema['layout']['elements'].append(vertical_layout['layout'])

        return self.uischema
    

class WizardJsonSchemaView(JsonSchemaView):
    def __init__(self, context, request):
        super().__init__(context, request)

    def __call__(self):
        jsonschema = self.combined_json_schema()
        return json.dumps(jsonschema, ensure_ascii=False, indent=4)

    def combined_json_schema(self):
        self.set_json_base_schema()

        object = self.context
        for child in object.listFolderContents():
            if child.portal_type == 'Form':
                object_schema = self.get_schema_for_object(child)       # create schema for form as if it were an object
                child_id = self.create_and_check_id(child)
                self.jsonschema['properties'][child_id] = object_schema

        return self.jsonschema
