# from plone.app.textfield import RichText
# from plone.autoform import directives
from edi.jsonforms.content.common import IDependentElements
from plone.dexterity.content import Container

# from plone.namedfile import field as namedfile

# from plone.supermodel.directives import fieldset
# from z3c.form.browser.radio import RadioFieldWidget
# from zope import schema
from zope.interface import implementer


class IComplex(IDependentElements):
    # class IComplex(model.Schema):
    """Marker interface and Dexterity Python Schema for Complex"""


@implementer(IComplex)
class Complex(Container):
    """ """
