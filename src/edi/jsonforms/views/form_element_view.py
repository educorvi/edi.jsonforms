# -*- coding: utf-8 -*-

from edi.jsonforms import _
import json
from edi.jsonforms.views.pydantic_models.GeneratorArguments import GeneratorArguments
from edi.jsonforms.views.pydantic_models.ObjectModel import (
    ObjectModel,
)
from edi.jsonforms.views.pydantic_models.SelectionFieldModel import (
    OptionListModel,
    OptionModel,
)
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
        self.is_single_view = True

    def __call__(self):
        uischema = self.ui_schema_without_showon()
        return json.dumps(uischema, ensure_ascii=False, indent=4)

    def ui_schema_without_showon(self):
        self.set_ui_base_schema()

        object = self.context
        option = None
        if object.portal_type in ["Option", "OptionList"]:
            option = object
            object = object.aq_parent
        self.add_child_to_schema(object, self.uischema)

        if option:
            if "layout" in self.uischema:
                if "elements" in self.uischema["layout"]:
                    if len(self.uischema["layout"]["elements"]) > 0:
                        if "options" in self.uischema["layout"]["elements"][0]:
                            self.uischema["layout"]["elements"][0]["options"][
                                "label"
                            ] = False

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
        # self.set_json_base_schema()

        object = self.context
        option = None
        parent = object.aq_parent
        if object.portal_type in ["Option", "OptionList"]:
            option = object
            object = object.aq_parent
            parent = parent.aq_parent

        generatorArguments = GeneratorArguments(
            self.request, self.is_single_view, self.is_extended_schema
        )
        form_model = ObjectModel(parent, None, self.request)
        model = form_model.create_and_add_model_without_dependencies(
            object, generatorArguments
        )

        if model:
            if option:
                model.unset_options()
                if option.portal_type == "Option":
                    o = OptionModel.from_option(option)
                    model.set_option(o)
                elif option.portal_type == "OptionList":
                    ol = OptionListModel(option)
                    model.set_option(ol)
            # if object.portal_type != "Fieldset":

        self.jsonschema = form_model.get_json_schema()

        return self.jsonschema
