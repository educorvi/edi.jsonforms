# -*- coding: utf-8 -*-

# from edi.jsonforms import _
import copy
import json
from Products.Five.browser import BrowserView
from edi.jsonforms.views.pydantic_models.GeneratorArguments import GeneratorArguments
from edi.jsonforms.views.pydantic_models.ObjectModel import (
    ObjectModel,
)
from zope.interface import implementer
from zope.interface import Interface

from edi.jsonforms.views.json_schema_view import JsonSchemaView
from edi.jsonforms.views.ui_schema_view import UiSchemaView
from edi.jsonforms.views.common import create_id


class IWizardView(Interface):
    """Marker Interface for IWizardView"""


@implementer(IWizardView)
class WizardView(BrowserView):
    def __call__(self):
        self.jsonschema = WizardJsonSchemaView(self.context, self.request)()
        self.uischema = WizardUiSchemaView(self.context, self.request)()
        return self.index()


class IWizardToolsView(Interface):
    """Marker Interface for IWizardView"""


@implementer(IWizardToolsView)
class WizardToolsView(BrowserView):
    def __call__(self):
        self.jsonschema = WizardJsonSchemaView(self.context, self.request)()
        self.uischema = WizardUiSchemaView(self.context, self.request, tools_on=True)()
        return self.index()


buttons = {
    "type": "Buttongroup",
    "buttons": [
        {
            "type": "Button",
            "buttonType": "previousWizardPage",
            "text": "Vorherige Seite",
            "options": {"variant": "outline-primary"},
        },
        {
            "type": "Button",
            "buttonType": "nextWizardPage",
            "text": "Nächste Seite",
            "options": {"variant": "outline-primary"},
        },
    ],
}

submit_button = {
    "type": "Button",
    "buttonType": "submit",
    "text": "Absenden",
    "options": {"variant": "primary"},
}


class WizardUiSchemaView(UiSchemaView):
    def __init__(self, context, request, tools_on=False):
        super().__init__(context, request)
        self.set_tools(tools_on)

    # overwrite get_schema from UiSchemaView
    def get_schema(self):
        return self.combined_ui_schema()

    def combined_ui_schema(self):
        self.set_ui_base_schema()

        self.uischema["layout"]["type"] = "Wizard"
        page_titles = []
        object = self.context
        for form in object.listFolderContents():
            if form.portal_type == "Form":
                page_titles.append(form.title)
                form_id = create_id(form)
                uischemaview = UiSchemaView(
                    form, self.request, scope=f"/properties/{form_id}/properties/"
                )
                uischemaview.set_tools(self.tools_on)
                vertical_layout = uischemaview.get_schema()["layout"]
                vertical_layout["elements"].append(copy.deepcopy(buttons))
                self.uischema["layout"]["elements"].append(vertical_layout)

        if self.uischema["layout"][
            "elements"
        ]:  # delete "previous" button from first page
            del self.uischema["layout"]["elements"][0]["elements"][-1]["buttons"][0]
        if (
            len(self.uischema["layout"]["elements"]) == 1
        ):  # replace "next" button with "submit" button from first page if only one page exists
            self.uischema["layout"]["elements"][-1]["elements"][-1]["buttons"][0] = (
                submit_button
            )
        elif (
            len(self.uischema["layout"]["elements"]) > 1
        ):  # replace "next" button with "submit" button from last page
            self.uischema["layout"]["elements"][-1]["elements"][-1]["buttons"][1] = (
                submit_button
            )

        self.uischema["layout"]["pages"] = self.uischema["layout"].pop("elements")
        self.uischema["layout"]["options"] = {"pageTitles": page_titles}
        return self.uischema


class WizardJsonSchemaView(JsonSchemaView):
    def __init__(self, context, request):
        super().__init__(context, request)

    # overwrite get_schema from JsonSchemaView
    def get_schema(self):
        return self.combined_json_schema()

    def combined_json_schema(self):
        # self.set_json_base_schema()

        object = self.context

        generatorArguments = GeneratorArguments(
            self.request, self.is_single_view, self.is_extended_schema
        )
        wizard_model = ObjectModel(object, None, self.request)
        wizard_model.set_children(generatorArguments)
        self.jsonschema = wizard_model.get_json_schema()
        # for child in object.listFolderContents():
        #     if child.portal_type == "Form":
        #         object_schema = self.get_schema_for_object(
        #             child
        #         )  # create schema for form as if it were an object
        #         child_id = self.create_and_check_id(child)
        #         self.jsonschema["properties"][child_id] = object_schema

        return self.jsonschema
