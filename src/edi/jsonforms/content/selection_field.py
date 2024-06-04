# -*- coding: utf-8 -*-
# from plone.app.textfield import RichText
# from plone.autoform import directives
from plone.dexterity.content import Container
# from plone.namedfile import field as namedfile
from plone.supermodel import model
from plone.supermodel.directives import fieldset
# from plone.supermodel.directives import fieldset
# from z3c.form.browser.radio import RadioFieldWidget
# from zope import schema
from zope.interface import implementer
from zope.schema.vocabulary import SimpleVocabulary, SimpleTerm
from zope import schema




from edi.jsonforms import _
from edi.jsonforms.content.common import IDependentBase


selection_answer_types = [
    SimpleTerm('radio', 'radio', _('Radiobuttons (single selection)')),             # input
    SimpleTerm('checkbox', 'checkbox', _('Checkboxes (multi-selection)')),        # input
    SimpleTerm('select', 'select', _('Selection (single selection)')),             # select
    SimpleTerm('selectmultiple', 'selectmultiple', _('Selection (multi-selection)')),  # select (with attribute multiple)
    SimpleTerm('file', 'file', _('File upload (single upload)')),                   # input
    SimpleTerm('file-multi', 'file-multi', _('File upload (multi-upload)')),        # <input name='datei[]' type='file' multiple>
]
Selection_answer_types = SimpleVocabulary(selection_answer_types)

possible_file_types = [
    SimpleTerm('jpg', 'jpg', _('.jpg')),
    SimpleTerm('png', 'png', _('.png')),
    SimpleTerm('pdf', 'pdf', _('.pdf')),
    SimpleTerm('gif', 'gif', _('.gif')),
    SimpleTerm('docx', 'docx', _('.docx'))
]
Possible_file_types = SimpleVocabulary(possible_file_types)


class ISelectionField(IDependentBase):
    """ Marker interface and Dexterity Python Schema for SelectionField
    """
    # title = schema.TextLine(title=_('Title of the field/question'), required=True)
    #
    # description = schema.Text(title=_('Description of the field/question'), required=False)

    answer_type = schema.Choice(title=_('Choose the answer type'),
                               source=Selection_answer_types,
                               default='radio',
                               required=True)

    fieldset(
        'advanced-options',
        label=_('Advanced Options'),
        fields=['accepted_file_types']
    )

    accepted_file_types = schema.List(title=_('Accepted file types for file upload.'),
                                      description=_('Only choose file types for answer types File upload (single and multi upload)'),
                                      value_type=schema.Choice(
                                          source=Possible_file_types
                                      ),
                                      required=False)


@implementer(ISelectionField)
class SelectionField(Container):
    """
    """
