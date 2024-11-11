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


from edi.jsonforms import _
from edi.jsonforms.content.common import IDependent


class IFieldset(IDependent):
    """ Marker interface and Dexterity Python Schema for Fieldset
    """
    # TODO translate these three
    title = schema.TextLine(title=_("Title"))
    description = schema.Text(title=_("Description"),
                           description=_("This is description is only for intern use and won't be shown in the form."),
                             required=False)



@implementer(IFieldset)
class Fieldset(Container):
    """
    """
