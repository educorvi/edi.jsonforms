# -*- coding: utf-8 -*-

import json
import logging

from AccessControl import getSecurityManager, Unauthorized
from plone import api
from plone.protect import CheckAuthenticator, createToken
from Products.CMFCore.permissions import ModifyPortalContent
from Products.Five.browser import BrowserView
from zope.interface import implementer
from zope.interface import Interface

from edi.jsonforms import _
from edi.jsonforms.content.option_list import get_keys_and_values_for_options_list


logger = logging.getLogger("edi.jsonforms")

# for usage of plone.protect see: https://pypi.org/project/plone.protect/


class OptionListView(BrowserView):
    def __call__(self):
        self.request.set("_authenticator", createToken())
        return self.index()


class ConvertOptionListView(BrowserView):
    def __call__(self):
        logger.info("Convert OptionList to Options called")
        CheckAuthenticator(self.request)
        if not getSecurityManager().checkPermission(ModifyPortalContent, self.context):
            raise Unauthorized(_("You do not have permission to modify this content."))

        optionlist = self.context
        parent_selectionfield = optionlist.aq_parent
        options = get_keys_and_values_for_options_list(optionlist)
        for key, value in zip(options[0], options[1]):
            try:
                api.content.create(
                    container=parent_selectionfield, type="Option", id=key, title=value
                )
            except Exception as e:
                logger.error(
                    f"Error creating Option with id '{key}' and title '{value}': {e}. Trying without id."
                )
                api.content.create(
                    container=parent_selectionfield,
                    type="Option",
                    title=value,
                )
        api.content.delete(optionlist)
        self.request.response.redirect(self.context.aq_parent.absolute_url())
