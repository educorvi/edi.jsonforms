from plone.dexterity.content import Container
from zope import schema
from zope.interface import implementer
from zope.schema.vocabulary import SimpleVocabulary, SimpleTerm

from edi.jsonforms import _
from edi.jsonforms.content.common import IDependent


modal_size = [
    SimpleTerm("small", "small", _("Small")),
    SimpleTerm("medium", "medium", _("Medium")),
    SimpleTerm("large", "large", _("Large")),
    SimpleTerm("x-large", "x-large", _("Extra Large")),
]
Modal_size = SimpleVocabulary(modal_size)


class IHelptextModal(IDependent):
    """Marker interface and Dexterity Python Schema for HelptextModal"""

    title = schema.TextLine(
        title=_("Modal Title"),
        description=_("This title is displayed inside the Modal."),
        required=True,
    )

    content = schema.Text(
        title=_("Modal Content"),
        description=_("This content is displayed inside the Modal."),
        required=True,
    )

    size = schema.Choice(
        title=_("Width of the Modal"),
        source=Modal_size,
        default="medium",
        required=True,
    )

    button_label = schema.TextLine(
        title=_("Button Label"),
        description=_("This label is displayed on the button that opens the Modal."),
        required=True,
    )

    button_variant = schema.Choice(
        title=_("Color variant of the button"),
        description=_("Choose the variant of the button that opens the Modal."),
        required=True,
        default="primary",
        vocabulary="plone.app.widgets.buttons:BUTTON_VARIANTS",
    )


@implementer(IHelptextModal)
class HelptextModal(Container):
    """Content-type class for IHelptextModal"""
