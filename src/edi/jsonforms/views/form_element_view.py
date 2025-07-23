# -*- coding: utf-8 -*-

# from edi.jsonforms import _
import json
from Products.Five.browser import BrowserView
from zope.interface import implementer
from zope.interface import Interface

from edi.jsonforms import _

# from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

class IFormElementView(Interface):
    """ Marker Interface for IFormElementView"""


@implementer(IFormElementView)
class FormElementView(BrowserView):

    def __call__(self):
        return self.index()
    
    def get_view_url(self):
        return self.context.absolute_url()
    
    def get_edit_url(self):
        return self.context.absolute_url() + '/edit'
    
    def has_content(self):
        return self.context.portal_type in ['Array', 'Selection Field', 'Button Handler', 'Fieldset', 'Complex']
    
    def get_content_url(self):
        return self.context.absolute_url() + '/folder_contents'
    
    def get_delete_url(self):
        return self.context.absolute_url() + '/delete_confirmation'