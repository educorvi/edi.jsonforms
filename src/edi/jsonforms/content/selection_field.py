# -*- coding: utf-8 -*-
# from plone.app.textfield import RichText
# from plone.autoform import directives
from plone.dexterity.content import Container
# from plone.namedfile import field as namedfile
from plone.supermodel import model
# from plone.supermodel.directives import fieldset
# from z3c.form.browser.radio import RadioFieldWidget
# from zope import schema
from zope.interface import implementer
from zope.schema.vocabulary import SimpleVocabulary, SimpleTerm
from zope import schema




from edi.jsonforms import _
from edi.jsonforms.content.field import IField


selection_answer_types = [
    SimpleTerm('radio', 'radio', _('Radiobuttons (single selection)')),             # input
    SimpleTerm('checkbox', 'checkbox', _('Checkboxes (multi-selection)')),        # input
    SimpleTerm('boolean', 'boolean', _('Checkbox (yes/no)')),                       # input (checkbox with one option)
    SimpleTerm('select', 'select', _('Selection (single selection)')),             # select
    SimpleTerm('selectmultiple', 'selectmultiple', _('Selection (multi-selection)')),  # select (with attribute multiple)
    SimpleTerm('file', 'file', _('File upload (single upload)')),                   # input
    SimpleTerm('file-multi', 'file-multi', _('File upload (multi-upload)')),        # <input name="datei[]" type="file" multiple>
]
Selection_answer_types = SimpleVocabulary(selection_answer_types)


class ISelectionField(IField):
    """ Marker interface and Dexterity Python Schema for SelectionField
    """
    answer_type = schema.Choice(title=_("Choose the answer type"),
                               source=Selection_answer_types,
                               default='radio',
                               required=True)


@implementer(ISelectionField)
class SelectionField(Container):
    """
    """
