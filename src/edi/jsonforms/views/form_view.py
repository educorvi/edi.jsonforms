# -*- coding: utf-8 -*-

from edi.jsonforms import _
from Products.Five.browser import BrowserView
from typing import Callable
from plone import api
from plone.app.layout.viewlets.content import ContentHistoryView
#from Products.CMFPlone.resources import add_resource_on_request


class FormView(BrowserView):

    def __call__(self):
        return self.index()

    def get_versions(self):
        historylist = []
        fullhistory = ContentHistoryView(self.context, self.request).fullHistory()
        if not fullhistory:
            return historylist
        for release in fullhistory:
            import pdb;pdb.set_trace()
            if release.get('version_id'):
                versionmarker = release.get('version_id')
                url = self.context.absolute_url() + f'/@@schema-view?version={versionmarker}'
                deptree_url = self.context.absolute_url() + f'/@@deptree-view?version={versionmarker}'
                deform_url = self.context.absolute_url() + f'/@@deform-view?version={versionmarker}'
                historylist.append((release.get('version_id'), release.get('comments'), url, deptree_url, deform_url))
        return historylist

