# -*- coding: utf-8 -*-
from edi.jsonforms import _
from Products.Five.browser import BrowserView
from typing import Callable
from plone import api
from plone.app.layout.viewlets.content import ContentHistoryView
from plone.protect.interfaces import IDisableCSRFProtection
from zope.interface import Interface, implementer, alsoProvides

class IFormToolsView(Interface):
    """Marker Interface"""

class FormView(BrowserView):

    def __call__(self):
        return self.index()

@implementer(IFormToolsView)
class FormToolsView(BrowserView):

    def __call__(self):
        alsoProvides(self.request, IDisableCSRFProtection)
        return self.index()

    def get_versions(self):
        repo_tool = api.portal.get_tool(name='portal_repository')
        historylist = []
        fullhistory = ContentHistoryView(self.context, self.request).fullHistory()
        if not fullhistory:
            return historylist
        for release in fullhistory:
            if release.get('version_id'):
                version = release.get('version_id')
                obj = repo_tool.retrieve(self.context, int(version)).object
                schema_url = self.context.absolute_url() + f'/@@version-view?version={version}&schema=json'
                ui_url = self.context.absolute_url() + f'/@@version-view?version={version}&schema=ui'
                historylist.append((release.get('version_id'), release.get('comments'), schema_url, ui_url))
        return historylist
