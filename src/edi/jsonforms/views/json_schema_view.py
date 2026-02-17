# -*- coding: utf-8 -*-

from Products.Five.browser import BrowserView
import json
import logging

from edi.jsonforms.views.pydantic_models.GeneratorArguments import GeneratorArguments
from edi.jsonforms.views.pydantic_models.ObjectModel import ObjectModel

logger = logging.getLogger("edi.jsonforms")


class JsonSchemaView(BrowserView):
    is_extended_schema = False  # True if schema is generated for an api call and not for the usual form view
    content_types_without_schema = ["Helptext", "Button Handler"]
    is_single_view = False

    def __init__(self, context, request):
        super().__init__(context, request)
        self.jsonschema = {}
        self.ids = set()

    def __call__(self):
        self.get_schema()
        return json.dumps(self.jsonschema, ensure_ascii=False, indent=4)

    def set_is_extended_schema(self, value=True):
        self.is_extended_schema = value

    def get_schema(self):
        form = self.context

        form_model = ObjectModel(form, None, self.request)
        generatorArguments = GeneratorArguments(
            self.request, self.is_single_view, self.is_extended_schema
        )
        form_model.set_children(generatorArguments)
        self.jsonschema = form_model.get_json_schema()

        return self.jsonschema
