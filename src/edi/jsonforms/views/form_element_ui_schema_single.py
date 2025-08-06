# -*- coding: utf-8 -*-

# from edi.jsonforms import _
import json
from Products.Five.browser import BrowserView
from zope.interface import implementer
from zope.interface import Interface

from edi.jsonforms.views.form_element_ui_schema import FormElementUiSchema

# from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

class IFormElementView(Interface):
    """ Marker Interface for IFormElementView"""


@implementer(IFormElementView)
class FormElementUiSchemaSingle(FormElementUiSchema):

    def __call__(self):
        uischema = self.ui_schema_without_showon()
        return json.dumps(uischema, ensure_ascii=False, indent=4)
    
    def ui_schema_without_showon(self):
        uischema = self.ui_schema()
        
        def remove_showon(dictionary):
            if isinstance(dictionary, dict):
                if 'showOn' in dictionary:
                    del dictionary['showOn']
                for key, value in dictionary.items():
                    remove_showon(value)
            elif isinstance(dictionary, list):
                for item in dictionary:
                    remove_showon(item)

        remove_showon(uischema)
        return uischema
