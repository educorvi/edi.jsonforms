from edi.jsonforms import _
from edi.jsonforms.content.common import IDependent

# from plone.autoform import directives
from plone.dexterity.content import Container

# from plone.namedfile import field as namedfile
# from plone.supermodel.directives import fieldset
# from z3c.form.browser.radio import RadioFieldWidget
from zope import schema
from zope.interface import implementer


class IFieldset(IDependent):
    """Marker interface and Dexterity Python Schema for Fieldset"""

    show_title = schema.Bool(
        title=_("Show title in form"), default=True, required=False
    )


@implementer(IFieldset)
class Fieldset(Container):
    """ """
