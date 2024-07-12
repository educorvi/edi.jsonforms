# -*- coding: utf-8 -*-
from plone.dexterity.content import Item
from plone.supermodel import model
from plone.supermodel.directives import fieldset
from zope import schema
from zope.interface import implementer
from zope.schema.vocabulary import SimpleVocabulary, SimpleTerm

from edi.jsonforms import _
from edi.jsonforms.content.common import IDependentExtended


upload_answer_types = [
    SimpleTerm('file', 'file', _('File upload (single upload)')),                   # input
    SimpleTerm('file-multi', 'file-multi', _('File upload (multi-upload)')),        # <input name='datei[]' type='file' multiple>
]
Upload_answer_types = SimpleVocabulary(upload_answer_types)

possible_file_types = [
    SimpleTerm('jpg', 'jpg', '.jpg'),
    SimpleTerm('png', 'png', '.png'),
    SimpleTerm('pdf', 'pdf', '.pdf'),
    SimpleTerm('gif', 'gif', '.gif'),
    SimpleTerm('docx', 'docx', '.docx')
]
Possible_file_types = SimpleVocabulary(possible_file_types)


class IUploadField(IDependentExtended):
    """ Marker interface and Dexterity Python Schema for UploadField
    """
    answer_type = schema.Choice(title=_('Choose the answer type'),
                                source=Upload_answer_types,
                                default='file',
                                required=True)

    fieldset(
        'advanced-options',
        label=_('Advanced Options'),
        fields=['accepted_file_types']
    )

    accepted_file_types = schema.List(title=_('Accepted file types for file upload'),
                                      description=_(
                                          'If no file type is selected, the default is * (all file types are accepted).'),
                                      value_type=schema.Choice(
                                          source=Possible_file_types
                                      ),
                                      required=False)


@implementer(IUploadField)
class UploadField(Item):
    """
    """
