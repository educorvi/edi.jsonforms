# -*- coding: utf-8 -*-
from plone.app.textfield import RichText

# from plone.autoform import directives
from plone.dexterity.content import Item

# from plone.namedfile import field as namedfile
from plone.supermodel import model

# from z3c.form.browser.radio import RadioFieldWidget
from zope import schema
from zope.interface import implementer
from plone.supermodel.directives import fieldset
from zope.interface import Invalid, invariant


from edi.jsonforms import _
from edi.jsonforms.content.common import IDependent


class IHelptext(IDependent):
    """Marker interface and Dexterity Python Schema for Helptext"""

    helptext = RichText(title=_("Helptext"), required=True)

    fieldset(
        "modal",
        label=_("Modal Settings"),
        fields=[
            "modal_enabled",
            "modal_title",
            "modal_button_label",
            # "modal_button_variant",
        ],
    )

    # switch to change helptext to modal
    modal_enabled = schema.Bool(
        title=_("Enable Modal"),
        description=_("Display the helptext in a modal instead of inline."),
        required=False,
    )

    modal_title = schema.TextLine(
        title=_("Modal Title"),
        description=_("This title is displayed inside the Modal."),
        required=False,
    )

    modal_button_label = schema.TextLine(
        title=_("Button Label"),
        description=_("This label is displayed on the button that opens the Modal."),
        required=False,
    )

    # modal_button_variant = schema.Choice(
    #     title=_("Color variant of the button"),
    #     description=_("Choose the variant of the button that opens the Modal."),
    #     required=False,
    #     default="primary",
    #     vocabulary="plone.app.widgets.buttons:BUTTON_VARIANTS",
    # )

    @invariant
    def check_modal(data):
        if data.modal_enabled:
            if not all(
                [
                    data.modal_title,
                    data.modal_button_label,
                    # data.modal_button_variant,
                ]
            ):
                raise Invalid(
                    _("If modal is enabled, you must provide a title and button label.")
                )


@implementer(IHelptext)
class Helptext(Item):
    """Content-type class for IHelptext"""
