# -*- coding: utf-8 -*-
import re
from plone.dexterity.content import Item
from plone.supermodel.directives import fieldset
from zope import schema
from zope.interface import implementer, Invalid, invariant
from zope.schema.vocabulary import SimpleTerm, SimpleVocabulary

from edi.jsonforms.content.common import IDependentExtended  # , check_dependencies
from edi.jsonforms import _


answer_types = [
    SimpleTerm("text", "text", _("Textline")),  # input
    SimpleTerm("textarea", "textarea", _("Textarea")),  # textarea
    SimpleTerm("password", "password", _("Password")),  # input
    SimpleTerm("tel", "tel", _("Telephone")),  # input
    SimpleTerm("url", "url", _("URL")),  # input
    SimpleTerm("email", "email", _("Email")),  # input
    SimpleTerm("date", "date", _("Date")),  # input
    SimpleTerm("datetime-local", "datetime-local", _("Date and time")),  # input
    SimpleTerm("time", "time", _("Time")),
    SimpleTerm("number", "number", _("Decimal number")),  # input
    SimpleTerm("integer", "integer", _("Whole number")),
    SimpleTerm(
        "boolean", "boolean", _("Checkbox (yes/no)")
    ),  # input (checkbox with one option)
]
Answer_types = SimpleVocabulary(answer_types)


def check_regex(value):
    try:
        re.compile(value)
        return True
    except re.error:
        raise Invalid(_("The provided regular expression isn't valid."))


class IField(IDependentExtended):
    # class IField(model.Schema):
    """Marker interface and Dexterity Python Schema for Field"""

    answer_type = schema.Choice(
        title=_("Choose the answer type"),
        source=Answer_types,
        default="text",
        required=True,
    )

    fieldset(
        "advanced-options",
        label=_("Advanced Options"),
        fields=["minimum", "maximum", "placeholder", "unit", "pattern"],
    )

    minimum = schema.Int(
        title=_("Minimum"),
        description=_(
            "For a number/integer this is the minimal value it must have. \
                                       For a Textline/-area/Password this is the minimal length the \
                                       text must have. (>=)"
        ),
        required=False,
    )

    maximum = schema.Int(
        title=_("Maximum"),
        description=_(
            "For a number/integer this is the maximal value it can have.\
                                       For a Textline/-area/Password this is the maximal length the \
                                       text can have."
        ),
        required=False,
    )

    unit = schema.TextLine(
        title=_("Unit of the answer"),
        description=_(
            "Only use this for the answer types Decimal and Whole number (e.g. km, kg)."
        ),
        required=False,
    )

    placeholder = schema.TextLine(
        title=_("Placeholder"),
        description=_(
            "Only use this for the answer types Textline/-area, Password, Telephone, URL, Email."
        ),
        required=False,
    )

    pattern = schema.TextLine(
        title=_("Regular expression to validate a Textline/-area field."),
        description=_("Only use this for the answer types Textline and Textarea."),
        constraint=check_regex,
        required=False,
    )

    @invariant
    def min_max_invariant(data):
        if data.minimum or data.maximum:
            if data.answer_type not in [
                "text",
                "textarea",
                "number",
                "integer",
                "password",
            ]:
                raise Invalid(
                    _(
                        "Minimum/Maximum are only valid options for the following answer types: Textline, Textarea, Password, Decimal number, Whole number."
                    )
                )
        if data.minimum and data.maximum:
            if data.maximum < data.minimum:
                # TODO translate this string
                raise Invalid(_("Maximum cannot be smaller than Minimum."))
        if data.maximum:
            if data.maximum <= 0:
                # TODO translate this string
                raise Invalid(_("Maximum cannot be smaller or equal to zero."))

    @invariant
    def placeholder_invariant(data):
        if data.placeholder:
            if data.answer_type not in [
                "text",
                "textarea",
                "password",
                "tel",
                "url",
                "email",
            ]:
                raise Invalid(
                    _(
                        "A Placeholder is only possible if the answer type is one of the following: Textline, Textarea, Password, Telephone, URL, Email."
                    )
                )

    @invariant
    def unit_invariant(data):
        if data.unit:
            if data.answer_type not in ["number", "integer"]:
                raise Invalid(
                    _(
                        "Unit is only a valid option for the following answer types: Decimal Number, Whole Number."
                    )
                )


@implementer(IField)
class Field(Item):
    """ """
