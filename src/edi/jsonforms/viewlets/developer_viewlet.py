# -*- coding: utf-8 -*-

from edi.jsonforms.views.json_schema_view import JsonSchemaView
from edi.jsonforms.views.ui_schema_view import UiSchemaView
from edi.jsonforms.views.wizard_view import WizardJsonSchemaView
from edi.jsonforms.views.wizard_view import WizardUiSchemaView
from plone import api
from plone.app.layout.viewlets import ViewletBase
from plone.app.layout.viewlets.content import ContentHistoryView
from typing import Dict
from typing import List
from urllib.parse import quote_plus


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

    def get_versions(self) -> List[Dict]:
        """
        returns a list of the versions in the following format:
        [
            {
                "version_id": "1",
                "comment": "Initial release",
                "json_schema_url": "http://example.com/form/@@version-view?version=1&schema=json",
                "ui_schema_url": "http://example.com/form/@@version-view?version=1&schema=ui",
                "forks_schema_url": "http://example.com/form/@@version-view?version=1&schema=forks", # the schema that only contains the differences of the forks
                "forks": [
                    {
                        "json_schema_url": "http://example.com/@@version-view?version=1&schema=json&fork=fork1", # full json schema of the fork
                        "ui_schema_url": "http://example.com/@@version-view?version=1&schema=ui&fork=fork1", # full ui schema of the fork
                        "name": "fork1",
                    },
                    ...
                ]
            }
        ]
        """
        repo_tool = api.portal.get_tool(name="portal_repository")
        historylist = []
        fullhistory = ContentHistoryView(self.context, self.request).fullHistory()
        if not fullhistory:
            return historylist
        for release in fullhistory:
            if release.get("version_id"):
                version = release.get("version_id")
                obj = repo_tool.retrieve(self.context, int(version)).object
                json_schema_url = (
                    self.context.absolute_url()
                    + f"/@@version-view?version={version}&schema=json"
                )
                ui_schema_url = (
                    self.context.absolute_url()
                    + f"/@@version-view?version={version}&schema=ui"
                )
                forks_schema_url = (
                    self.context.absolute_url()
                    + f"/@@version-view?version={version}&schema=forks"
                )

                forked_json_schemata = getattr(obj, "forked_json_schema_rev", {}) or {}
                forked_ui_schemata = getattr(obj, "forked_ui_schema_rev", {}) or {}
                forks = [fork for fork in forked_json_schemata.keys()] + [
                    fork for fork in forked_ui_schemata.keys()
                ]
                forks = sorted(list(set(forks)))  # remove duplicates

                fork_urls = []
                for fork in forks:
                    fork_json_schema_url = (
                        self.context.absolute_url()
                        + f"/@@version-view?version={version}&schema=json&fork={quote_plus(fork)}"
                    )
                    fork_ui_schema_url = (
                        self.context.absolute_url()
                        + f"/@@version-view?version={version}&schema=ui&fork={quote_plus(fork)}"
                    )
                    fork_urls.append({
                        "json_schema_url": fork_json_schema_url,
                        "ui_schema_url": fork_ui_schema_url,
                        "name": fork,
                    })

                historylist.append({
                    "version_id": version,
                    "comment": release.get("comments"),
                    "json_schema_url": json_schema_url,
                    "ui_schema_url": ui_schema_url,
                    "forks_schema_url": forks_schema_url,
                    "forks": fork_urls,
                })
        return historylist
