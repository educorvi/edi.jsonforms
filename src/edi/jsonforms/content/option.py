# -*- coding: utf-8 -*-
# from plone.app.textfield import RichText
# from plone.autoform import directives
from plone.dexterity.content import Item
# from plone.namedfile import field as namedfile
from plone.supermodel import model
# from plone.supermodel.directives import fieldset
# from z3c.form.browser.radio import RadioFieldWidget
# from zope import schema
from zope.interface import implementer
from zope.schema.vocabulary import SimpleVocabulary, SimpleTerm


from edi.jsonforms import _


field_types = [
    SimpleTerm('text', 'text', _('Textline')),
    SimpleTerm('textarea', 'textarea', _('Textarea')),
    SimpleTerm('number', 'number', _('Number'))
]
Field_types = SimpleVocabulary(field_types)

class IOption(model.Schema):
    """ Marker interface and Dexterity Python Schema for Option
    """
    title = schema.TextLine(title=_('Label of the answer option'))





@implementer(IOption)
class Option(Item):
    """
    """
