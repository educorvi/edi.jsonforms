# from plone.app.textfield import RichText
# from plone.autoform import directives
from edi.jsonforms.content.common import IObjectWithSchemata
from plone.dexterity.content import Container

# from plone.namedfile import field as namedfile
# from plone.supermodel import model
# from z3c.form.browser.radio import RadioFieldWidget
from zope.interface import implementer


class IWizard(IObjectWithSchemata):
    """Marker interface and Dexterity Python Schema for Wizard"""


@implementer(IWizard)
class Wizard(Container):
    """Content-type class for IWizard"""
