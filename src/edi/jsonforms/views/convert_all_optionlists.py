# -*- coding: utf-8 -*-
import json
import logging

from AccessControl import getSecurityManager, Unauthorized
from plone import api
from plone.protect.interfaces import IDisableCSRFProtection
from zope.interface import alsoProvides

from Products.Five.browser import BrowserView
from zope.interface import implementer
from zope.interface import Interface

from edi.jsonforms import _
from edi.jsonforms.content.option_list import get_keys_and_values_for_options_list


logger = logging.getLogger("edi.jsonforms")

class IConvertAllOptionlists(Interface):
    """ Marker Interface for IConvertAllOptionlists"""

@implementer(IConvertAllOptionlists)
class ConvertAllOptionlists(BrowserView):
    def __call__(self):
        alsoProvides(self.request, IDisableCSRFProtection)
        option_lists = api.content.find(context=self.context, portal_type='OptionList')
        for optlst in option_lists:
            logger.info("Convert OptionList to Options called")
            optionlist = optlst.getObject()
            parent_selectionfield = optionlist.aq_parent
            options = get_keys_and_values_for_options_list(optionlist)
            for key, value in zip(options[0], options[1]):
                try:
                    api.content.create(
                        container=parent_selectionfield, type="Option", id=key.replace('/','_'), title=value
                    )
                except:
                    api.content.create(
                        container=parent_selectionfield, type="Option", title=value
                    )
            api.content.delete(optionlist)
        return "All OptionLists are converted to options" 
