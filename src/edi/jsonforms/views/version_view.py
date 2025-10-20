# -*- coding: utf-8 -*-
import json
from Products.Five.browser import BrowserView
from zope.interface import implementer
from zope.interface import Interface
from plone import api

class IVersionView(Interface):
    """ Marker Interface for IVersionView"""


@implementer(IVersionView)
class VersionView(BrowserView):
    def __call__(self):
        repo_tool = api.portal.get_tool(name='portal_repository')
        if self.request.get('version') and self.request.get('schema'):
            version = self.request.get('version')
            schema = self.request.get('schema')
            obj = repo_tool.retrieve(self.context, int(version)).object
            if schema == 'json':
                objschema = obj.json_schema_rev
            elif schema == 'ui':
                objschema = obj.ui_schema_rev
            return json.dumps(objschema, indent=4)
        return self.request.response.redirect(self.context.absolute_url())
