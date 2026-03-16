# -*- coding: utf-8 -*-
from edi.jsonforms import _
from plone import api
from plone.app.layout.viewlets.content import ContentHistoryView
from plone.protect.interfaces import IDisableCSRFProtection
from Products.Five.browser import BrowserView
from typing import Callable
from zope.interface import alsoProvides
from zope.interface import implementer
from zope.interface import Interface


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
