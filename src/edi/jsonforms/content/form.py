# from plone.app.textfield import RichText
# from plone.autoform import directives

# from edi.jsonforms import _
from edi.jsonforms.content.common import IObjectWithSchemata
from plone.dexterity.content import Container

# from plone.namedfile import field as namedfile

# from z3c.form.browser.radio import RadioFieldWidget
# from zope import schema
from zope.interface import implementer


class IForm(IObjectWithSchemata):
    """Marker interface and Dexterity Python Schema for Form"""


@implementer(IForm)
class Form(Container):
    """ """
