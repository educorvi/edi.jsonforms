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
        # TODO add tools functionality
        self.jsonschema = WizardJsonSchemaView(self.context, self.request)()
        self.uischema = WizardUiSchemaView(self.context, self.request)()
        return self.index()


buttons = {
    "type": "Buttongroup",
    "buttons": [
        {
            "type": "Button",
            "buttonType": "previousWizardPage",
            "text": "Vorherige Seite",
            "options": {
                "variant": "outline-primary"
            }
        },
        {
            "type": "Button",
            "buttonType": "nextWizardPage",
            "text": "Nächste Seite",
            "options": {
                "variant": "outline-primary"
            }
        }
    ]
}

submit_button = {
    "type": "Button",
    "buttonType": "submit",
    "text": "Absenden",
    "options": {
        "variant": "primary"
    }
}

class WizardUiSchemaView(UiSchemaView):
    def __init__(self, context, request):
        super().__init__(context, request)

    def __call__(self):
        uischema = self.combined_ui_schema()
        return json.dumps(uischema, ensure_ascii=False, indent=4)

    def combined_ui_schema(self):
        self.set_ui_base_schema()
        VERTICAL_LAYOUT = copy.deepcopy(self.uischema)

        self.uischema["layout"]["type"] = "Wizard"
        page_titles = []
        object = self.context
        for form in object.listFolderContents():
            if form.portal_type == "Form":
                page_titles.append(form.title)
                vertical_layout = copy.deepcopy(VERTICAL_LAYOUT)
                form_id = create_id(form)
                for child in form.getFolderContents():
                    self.add_child_to_schema(
                        child.getObject(),
                        vertical_layout,
                        f"/properties/{form_id}/properties/"
                    )
                vertical_layout["layout"]["elements"].append(copy.deepcopy(buttons))
                self.uischema["layout"]["elements"].append(vertical_layout["layout"])

        if self.uischema["layout"]["elements"]:
            del self.uischema["layout"]["elements"][0]["elements"][-1]["buttons"][0]
        if len(self.uischema["layout"]["elements"]) == 1:
            self.uischema["layout"]["elements"][-1]["elements"][-1]["buttons"][0] = submit_button
        elif len(self.uischema["layout"]["elements"]) >1:
            self.uischema["layout"]["elements"][-1]["elements"][-1]["buttons"][1] = submit_button

        self.uischema["layout"]["pages"] = self.uischema["layout"].pop("elements")
        self.uischema["layout"]["options"] = {}
        self.uischema["layout"]["options"]["pageTitles"] = page_titles
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
            if child.portal_type == "Form":
                object_schema = self.get_schema_for_object(
                    child
                )  # create schema for form as if it were an object
                child_id = self.create_and_check_id(child)
                self.jsonschema["properties"][child_id] = object_schema

        return self.jsonschema
