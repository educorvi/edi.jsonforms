from plone import api
from Products.Five.browser import BrowserView
from zope.interface import implementer
from zope.interface import Interface

import json


class IVersionView(Interface):
    """Marker Interface for IVersionView"""


@implementer(IVersionView)
class VersionView(BrowserView):
    def __call__(self):
        repo_tool = api.portal.get_tool(name="portal_repository")
        version = self.request.get("version")
        schema = self.request.get("schema")
        fork = self.request.get("fork")

        objschema = None
        if version and schema and fork:
            obj = repo_tool.retrieve(self.context, int(version)).object
            if schema == "json":
                forked_json_schemata = (
                    getattr(obj, "forked_json_schema_rev", None) or {}
                )
                if fork in forked_json_schemata:
                    objschema = forked_json_schemata[fork]

                if not objschema:
                    objschema = getattr(obj, "json_schema_rev", None) or {}
            elif schema == "ui":
                forked_ui_schemata = getattr(obj, "forked_ui_schema_rev", None) or {}
                if fork in forked_ui_schemata:
                    objschema = forked_ui_schemata[fork]

                if not objschema:
                    objschema = getattr(obj, "ui_schema_rev", None) or {}
        elif version and schema:
            obj = repo_tool.retrieve(self.context, int(version)).object
            if schema == "json":
                objschema = getattr(obj, "json_schema_rev", None) or {}
            elif schema == "ui":
                objschema = getattr(obj, "ui_schema_rev", None) or {}
            elif schema == "forks":
                objschema = getattr(obj, "forks_rev", None) or {}

        if objschema:
            return json.dumps(objschema, indent=4)
        return self.request.response.redirect(self.context.absolute_url())
