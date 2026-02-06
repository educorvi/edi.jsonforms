# -*- coding: utf-8 -*-

from Products.Five.browser import BrowserView
from zope.interface import implementer
from zope.interface import Interface

class IConvertAllOptionlists(Interface):
    """ Marker Interface for IConvertAllOptionlists"""


@implementer(IConvertAllOptionlists)
class ConvertAllOptionlists(BrowserView):
    def __call__(self):
        template = '''<li class="heading" i18n:translate="">
          Sample View
        </li>'''
        return template
