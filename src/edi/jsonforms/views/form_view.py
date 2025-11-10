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
