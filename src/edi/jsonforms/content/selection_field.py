# -*- coding: utf-8 -*-
from plone.dexterity.content import Container
from plone.supermodel import model
from zope import schema
from zope.interface import implementer
from zope.schema.vocabulary import SimpleVocabulary, SimpleTerm

from edi.jsonforms import _
from edi.jsonforms.content.common import IDependentExtended



selection_answer_types = [
    SimpleTerm('radio', 'radio', _('Radiobuttons (single selection)')),             # input
    SimpleTerm('checkbox', 'checkbox', _('Checkboxes (multi-selection)')),        # input
    SimpleTerm('select', 'select', _('Selection (single selection)')),             # select
    SimpleTerm('selectmultiple', 'selectmultiple', _('Selection (multi-selection)')),  # select (with attribute multiple)
]
Selection_answer_types = SimpleVocabulary(selection_answer_types)


class ISelectionField(IDependentExtended):
    """ Marker interface and Dexterity Python Schema for SelectionField
    """
    # title = schema.TextLine(title=_('Title of the field/question'), required=True)
    #
    # description = schema.Text(title=_('Description of the field/question'), required=False)

    answer_type = schema.Choice(title=_('Choose the answer type'),
                               source=Selection_answer_types,
                               default='radio',
                               required=True)
    
    use_id_in_schema = schema.Bool(
        title=_('Use id of options in schema'),
        description=_('Check if you want to use the id of the options instead of the label/title in the schema'),
        default=False,
        required=False,
    )


@implementer(ISelectionField)
class SelectionField(Container):
    """
    """
