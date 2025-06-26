# -*- coding: utf-8 -*-
from plone.app.textfield import RichText
# from plone.autoform import directives
from plone.dexterity.content import Item
# from plone.namedfile import field as namedfile
from plone.supermodel import model
# from plone.supermodel.directives import fieldset
# from z3c.form.browser.radio import RadioFieldWidget
from zope import schema
from zope.interface import implementer


from edi.jsonforms import _
from edi.jsonforms.content.common import IFormElement


class IHelptext(IFormElement):
    """ Marker interface and Dexterity Python Schema for Helptext
    """
    # TODO translate these three
    title = schema.TextLine(title=_("Title"),
                            description=_("The title won't be shown in the form."))
    description = schema.Text(title=_("Description"),
                              required=False,
                              description=_("The description won't be shown in the form."))
    helptext = RichText(title=_("Helptext"),
                             required=False)


@implementer(IHelptext)
class Helptext(Item):
    """ Content-type class for IHelptext
    """
