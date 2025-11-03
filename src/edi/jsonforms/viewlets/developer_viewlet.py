# -*- coding: utf-8 -*-

from plone.app.layout.viewlets import ViewletBase
from plone.protect.interfaces import IDisableCSRFProtection
from zope.interface import Interface, implementer, alsoProvides
from plone.app.layout.viewlets.content import ContentHistoryView
from edi.jsonforms.views.form_view import IFormToolsView
from plone import api


class DeveloperViewlet(ViewletBase):
    def render(self):
        if self.request.get("URL", "").endswith("form-tools-view"):
            return super().render()
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
