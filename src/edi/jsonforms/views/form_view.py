# -*- coding: utf-8 -*-

from edi.jsonforms import _
from Products.Five.browser import BrowserView
#from Products.CMFPlone.resources import add_resource_on_request



# from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile


class FormView(BrowserView):
    # If you want to define a template here, please remove the template from
    # the configure.zcml registration of this view.
    # template = ViewPageTemplateFile('form_view.pt')

    def __call__(self):
        # Implement your own actions:
        #add_resource_on_request(self.request, 'edi.jsonforms')
        return self.index()

    def json_schema_view(self):
        import pdb; pdb.set_trace()
        context = self.context
        request = self.request

        #json_schema = getMultiAdapter((context, request), name="json-schema-view")

        #return json_schema()
