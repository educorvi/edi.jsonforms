from edi.jsonforms import _
from edi.jsonforms.content.common import IDependent
from plone.app.textfield import RichText

# from plone.autoform import directives
from plone.dexterity.content import Item

# from plone.namedfile import field as namedfile
# from plone.supermodel.directives import fieldset
# from z3c.form.browser.radio import RadioFieldWidget
from zope.interface import implementer


class IHelptext(IDependent):
    """Marker interface and Dexterity Python Schema for Helptext"""

    helptext = RichText(title=_("Helptext"), required=True)


@implementer(IHelptext)
class Helptext(Item):
    """Content-type class for IHelptext"""
