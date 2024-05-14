# -*- coding: utf-8 -*-
# from plone.app.textfield import RichText
# from plone.autoform import directives
from plone.dexterity.content import Container
# from plone.namedfile import field as namedfile
from plone.supermodel import model
# from plone.supermodel.directives import fieldset
# from z3c.form.browser.radio import RadioFieldWidget
# from zope import schema
from zope.interface import implementer


from edi.jsonforms import _
from edi.jsonforms.content.common import Required_categories


class IComplex(IFieldset):
    """ Marker interface and Dexterity Python Schema for Complex
    """
    directives.widget(required_choice=RadioFieldWidget)
    required_choice = schema.Choice(title=_('Selection of Field Requirement'),
                                    source=Required_categories,
                                    default='optional',
                                    required=True)



@implementer(IComplex)
class Complex(Container):
    """
    """
