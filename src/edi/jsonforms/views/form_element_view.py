# -*- coding: utf-8 -*-

from edi.jsonforms import _
from Products.Five.browser import BrowserView
from typing import Callable
from plone import api
#from Products.CMFPlone.resources import add_resource_on_request

from edi.jsonforms.views.form_view import FormView


class FormElementView(FormView):

    def __call__(self):
        return self.index()
    
    def empty_selection_field(self) -> bool:
        """ Check if a field is a selection field and if it has options.
        """
        context = self.context
        if context.portal_type == "SelectionField":
            options = context.getFolderContents()
            if len(options) == 0:
                return True
        return False

