# -*- coding: utf-8 -*-

# from edi.jsonforms import _
from Products.Five.browser import BrowserView
from zope.interface import implementer
from zope.interface import Interface

# from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

class IWizardView(Interface):
    """ Marker Interface for IWizardView"""


@implementer(IWizardView)
class WizardView(BrowserView):
    # If you want to define a template here, please remove the template from
    # the configure.zcml registration of this view.
    # template = ViewPageTemplateFile('wizard_view.pt')

    def __call__(self):
        # Implement your own actions:
        return self.index()
