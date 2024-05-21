# -*- coding: utf-8 -*-
# from plone.app.textfield import RichText
# from plone.autoform import directives
from plone.dexterity.content import Item
# from plone.namedfile import field as namedfile
from plone.supermodel import model
# from plone.supermodel.directives import fieldset
# from z3c.form.browser.radio import RadioFieldWidget
from zope import schema
from zope.interface import implementer
from zope.schema.vocabulary import SimpleVocabulary, SimpleTerm
from plone.autoform import directives
from z3c.form.browser.radio import RadioFieldWidget


from edi.jsonforms.content.common import Required_categories, IDependent
from edi.jsonforms import _

answer_types = [
    SimpleTerm('text', 'text', _('Textline')),                      # input
    SimpleTerm('textarea', 'textarea', _('Textarea')),              # textarea
    SimpleTerm('password', 'password', _('Password')),              # input
    SimpleTerm('tel', 'tel', _('Telephone')),                       # input
    SimpleTerm('url', 'url', _('URL')),                             # input
    SimpleTerm('email', 'email', _('Email')),                       # input
    SimpleTerm('date', 'date', _('Date')),                          # input
    SimpleTerm('datetime-local', 'datetime-local', _('Date and time')),# input
    SimpleTerm('time', 'time', _('Time')),
    SimpleTerm('number', 'number', _('Decimal number')),            # input
    SimpleTerm('integer', 'integer', _('Whole number')),
    SimpleTerm('boolean', 'boolean', _('Checkbox (yes/no)')),  # input (checkbox with one option)
]
Answer_types = SimpleVocabulary(answer_types)


class IField(IDependent):
#class IField(model.Schema):
    """ Marker interface and Dexterity Python Schema for Field
    """
    title = schema.TextLine(title=_('Title of the field/question'), required=True)

    description = schema.Text(title=_('Description of the field/question'), required=False)

    answer_type = schema.Choice(title=_("Choose the answer type"),
                               source=Answer_types,
                               default='text',
                               required=True)

    directives.widget(required_choice=RadioFieldWidget)
    required_choice = schema.Choice(title=_('Selection of Field Requirement'),
                                    source=Required_categories,
                                    default='optional',
                                    required=True)


    # helptext = schema.Text(title="Unformatierte Hilfestellung zur Übergabe ans JSON-Schema", required=False)

    # tipp = RichText(title=u"Hinweis oder Hilfe zur Fragestellung",
    #                      required=False)

    # fieldset(
    #         'validations',
    #         label=u'Validierungen',
    #         fields=('pattern_choice', 'pattern', 'patternlist', 'minLength', 'maxLength', 'minimum', 'exclusiveMinimum', 'maximum', 'exclusiveMaximum'),
    #     )
    # pattern_choice = schema.Choice(title=u"Auswahl eines Validators für ein Textfeld (Text oder Textzeile)",
#                               source=Validatoren,
#                               required=False)
#
#     pattern = schema.TextLine(title="Regulärer Ausdruck für die Validierung eines Textfeldes (Text oder Textzeile).",
#                               description="Eine Eingabe in diesem Feld überschreibt eine vorher getroffene Auswahl",
#                               constraint=check_regex, required=False)
#
#     patternlist = schema.List(title="Weitere reguläre Ausdrücke für die Validierung des Textfeldes (Text oder Textzeile) - ODER verknüpft.",
#                               value_type = schema.TextLine(),
#                               constraint=check_regexlist, required=False)
#
#     minLength = schema.Int(title="Minimale Länge (minLength) eines Textfeldes (Text oder Textzeile)",
#                               required = False)
#
#     maxLength = schema.Int(title="Maximale Länge (maxLength) eines Textfeldes (Text oder Textzeile)",
#                               required = False)
#
#     minimum = schema.Int(title="Minimum eines Zahlenwertes (Zahlenwert oder Ganzzahl), entspricht: >=",
#                               required = False)
#
#     exclusiveMinimum = schema.Bool(title="Wenn ausgewählt wird das Minimum als > interpretiert",
#                               required = False)
#
#     maximum = schema.Int(title="Maximum eines Zahlenwertes (Zahlenwert oder Ganzzahl), entspricht: <=",
#                               required = False)
#
#     exclusiveMaximum = schema.Bool(title="Wenn ausgewählt wird das Maximum als < interpretiert",
#                               required = False)

    # placeholder = schema.TextLine(title=u'Platzhalter (nur bei Antworttypen "Textzeile" oder "Text")', required=False)

    # einheit = schema.TextLine(title=u"Einheit der Antwort (nur bei Antworttyp Zahlenwert möglich)",
    #                      description = u"Sie können hier eine Einheit für die Antwort angeben (z.B.: Ohm, Ampere, Volt)",
    #                      required=False)

    # @invariant
    # def einheit_invariant(data):
    #     if data.einheit:
    #         if data.antworttyp not in ['number', 'integer']:
    #             raise Invalid(u"Bei Angabe von Einheiten muss der Antworttyp Zahlenwert ausgewählt werden.")
    #
    # @invariant
    # def pattern_invariant(data):
    #     if data.pattern or data.pattern_choice:
    #         if data.antworttyp not in ['text', 'textarea']:
    #             raise Invalid(u"Für den ausgewählten Antworttyp kann keine Validierung mittels regulärem Ausdruck durchgeführt werden.")
    #
    # @invariant
    # def length_invariant(data):
    #     if data.minLength or data.maxLength:
    #         if data.antworttyp not in ['text', 'textarea']:
    #             raise Invalid(u"Für den ausgewählten Antworttyp kann keine Längenvalidierung durchgeführt werden.")
    #
    # @invariant
    # def numrange_invariant(data):
    #     if data.minimum or data.maximum:
    #         if data.antworttyp not in ['number', 'integer']:
    #             raise Invalid(u"Für den ausgewählten Antworttyp kann keine Minimum/Maximum Validierung durchgeführt werden.")
    #
    # @invariant
    # def antworttyp_relation(data):
    #     if data.antworttyp == 'custom':
    #         if not data.rel_antworttyp:
    #             raise Invalid(u"Es muss ein Verweis auf einen XUV/JUV Datentypen angegeben werden.")
    #
    # @invariant
    # def placeholder_invariant(data):
    #     if data.placeholder:
    #         if data.answer_type not in ['text', 'textarea']:
    #             raise Invalid(_('A Placeholder is only possible if the answer type is "text" or "textarea".'))

@implementer(IField)
class Field(Item):
    """
    """
