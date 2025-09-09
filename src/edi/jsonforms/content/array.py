# -*- coding: utf-8 -*-
# from plone.app.textfield import RichText
# from plone.autoform import directives
from plone.dexterity.content import Container
# from plone.namedfile import field as namedfile
from plone.supermodel import model
# from plone.supermodel.directives import fieldset
# from z3c.form.browser.radio import RadioFieldWidget
from zope import schema
from zope.interface import implementer
from plone.autoform import directives
from z3c.form.browser.radio import RadioFieldWidget


from edi.jsonforms.content.complex import IComplex
from edi.jsonforms.content.common import Required_categories
from edi.jsonforms import _


class IArray(IComplex):
    """ Marker interface and Dexterity Python Schema for Array
    """
    directives.widget(required_choice=RadioFieldWidget)
    required_choice = schema.Choice(title=_('Selection of Field Requirement'),
                                    source=Required_categories,
                                    default='optional',
                                    required=True)
    
    show_title = schema.Bool(title=_("Show title in form"),
                             default=True,
                             required=False)
    
    button_label = schema.TextLine(title=_("Add button label"),
                                   description=_("Label of the button to add new elements. Default: +"),
                                   required=False)



@implementer(IArray)
class Array(Container):
    """
    """
