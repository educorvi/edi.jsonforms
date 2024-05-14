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


# from edi.jsonforms import _


class IArray(IComplex):
    """ Marker interface and Dexterity Python Schema for Array
    """



@implementer(IArray)
class Array(Container):
    """
    """
