from edi.jsonforms.views.form_view import FormView
from edi.jsonforms.views.json_schema_view import JsonSchemaView
from edi.jsonforms.views.pydantic_models.GeneratorArguments import GeneratorArguments
from edi.jsonforms.views.pydantic_models.ObjectModel import ObjectModel
from edi.jsonforms.views.pydantic_models.SelectionFieldModel import OptionListModel
from edi.jsonforms.views.pydantic_models.SelectionFieldModel import OptionModel
from edi.jsonforms.views.ui_schema_view import UiSchemaView
from zope.interface import implementer
from zope.interface import Interface

import json


class IFormElementView(Interface):
    """Marker Interface for IFormElementView"""


class IFormElementToolsView(Interface):
    """Marker Interface for IFormElementToolsView"""


@implementer(IFormElementView)
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


class FormElementUiSchema(UiSchemaView):
    def __init__(self, context, request):
        super().__init__(context, request)
        self.is_single_view = True

    def __call__(self):
        uischema = self.ui_schema_without_showon()
        return json.dumps(uischema, ensure_ascii=False, indent=4)

    def ui_schema_without_showon(self):
        self.set_ui_base_schema()

        obj = self.context
        option = None
        if obj.portal_type in ["Option", "OptionList"]:
            option = obj
            obj = obj.aq_parent
        self.add_child_to_schema(obj, self.uischema)

        if (
            option
            and "layout" in self.uischema
            and "elements" in self.uischema["layout"]
            and len(self.uischema["layout"]["elements"]) > 0
            and "options" in self.uischema["layout"]["elements"][0]
        ):
            self.uischema["layout"]["elements"][0]["options"]["label"] = False

        return self.uischema


class FormElementJsonSchema(JsonSchemaView):
    def __init__(self, context, request):
        super().__init__(context, request)
        self.is_single_view = True

    def __call__(self):
        jsonschema = self.json_schema()
        return json.dumps(jsonschema, ensure_ascii=False, indent=4)

    def json_schema(self):
        # self.set_json_base_schema()

        obj = self.context
        option = None
        parent = obj.aq_parent
        if obj.portal_type in ["Option", "OptionList"]:
            option = obj
            obj = obj.aq_parent
            parent = parent.aq_parent

        generatorArguments = GeneratorArguments(
            self.request, self.is_single_view, self.is_extended_schema
        )
        form_model = ObjectModel(parent, None, self.request)
        model = form_model.create_and_add_model_without_dependencies(
            obj, generatorArguments
        )

        if model and option:
            model.unset_options()
            if option.portal_type == "Option":
                o = OptionModel.from_option(option)
                model.set_option(o)
            elif option.portal_type == "OptionList":
                ol = OptionListModel(option)
                model.set_option(ol)

        self.jsonschema = form_model.get_json_schema()

        return self.jsonschema


@implementer(IFormElementToolsView)
class FormElementToolsView(FormElementView):
    def form_element_uischema(self) -> str:
        form_element_uischema = ToolsFormElementUiSchema(self.context, self.request)()
        return form_element_uischema


class ToolsFormElementUiSchema(FormElementUiSchema):
    def __init__(self, context, request):
        super().__init__(context, request)
        self.set_tools(True)
