# -*- coding: utf-8 -*-
# from plone.app.textfield import RichText
# from plone.autoform import directives
from plone.dexterity.content import Item
# from plone.namedfile import field as namedfile
from plone.supermodel import model
# from plone.supermodel.directives import fieldset
# from z3c.form.browser.radio import RadioFieldWidget
from zope import schema
from zope.interface import implementer
from zope.schema.vocabulary import SimpleVocabulary, SimpleTerm


from edi.jsonforms import _
from edi.jsonforms.content.common import IFormElement


class IOption(IFormElement):
    """ Marker interface and Dexterity Python Schema for Option
    """
    title = schema.TextLine(title=_('Label of the answer option'))





@implementer(IOption)
class Option(Item):
    """
    """
