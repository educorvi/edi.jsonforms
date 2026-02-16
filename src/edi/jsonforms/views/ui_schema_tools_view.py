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
class UiSchemaToolsView(UiSchemaView):

    def __init__(self, context, request):
        super().__init__(context, request)

    def __call__(self):
        self.set_tools(True)
        return super().__call__()
