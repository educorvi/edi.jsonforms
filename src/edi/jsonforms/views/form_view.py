# -*- coding: utf-8 -*-

from edi.jsonforms import _
from Products.Five.browser import BrowserView
from typing import Callable
from plone import api
#from Products.CMFPlone.resources import add_resource_on_request


class FormView(BrowserView):

    def __call__(self):
        return self.index()

