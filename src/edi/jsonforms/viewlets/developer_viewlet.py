# -*- coding: utf-8 -*-

from plone.app.layout.viewlets import ViewletBase
from plone.app.layout.viewlets.content import ContentHistoryView
from edi.jsonforms.views.json_schema_view import JsonSchemaView
from edi.jsonforms.views.ui_schema_view import UiSchemaView
from edi.jsonforms.views.wizard_view import WizardJsonSchemaView, WizardUiSchemaView
from plone import api


class DeveloperViewlet(ViewletBase):
    def render(self):
        url = self.request.get("URL", "")
        if url.endswith("form-tools-view") or url.endswith("wizard-tools-view"):
            return super().render()
        return ""

    def get_json_schema(self):
        if self.context.portal_type == "Form":
            json_schema = JsonSchemaView(self.context, self.request)
            return json_schema()
        elif self.context.portal_type == "Wizard":
            json_schema = WizardJsonSchemaView(self.context, self.request)
            return json_schema()
        return ""

    def get_ui_schema(self):
        if self.context.portal_type == "Form":
            ui_schema = UiSchemaView(self.context, self.request)
            return ui_schema()
        elif self.context.portal_type == "Wizard":
            ui_schema = WizardUiSchemaView(self.context, self.request)
            return ui_schema()
        return ""

    def get_versions(self):
        repo_tool = api.portal.get_tool(name="portal_repository")
        historylist = []
        fullhistory = ContentHistoryView(self.context, self.request).fullHistory()
        if not fullhistory:
            return historylist
        for release in fullhistory:
            if release.get("version_id"):
                version = release.get("version_id")
                obj = repo_tool.retrieve(self.context, int(version)).object
                schema_url = (
                    self.context.absolute_url()
                    + f"/@@version-view?version={version}&schema=json"
                )
                ui_url = (
                    self.context.absolute_url()
                    + f"/@@version-view?version={version}&schema=ui"
                )
                historylist.append(
                    (
                        release.get("version_id"),
                        release.get("comments"),
                        schema_url,
                        ui_url,
                    )
                )
        return historylist
