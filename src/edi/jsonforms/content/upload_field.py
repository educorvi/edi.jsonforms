# -*- coding: utf-8 -*-
from plone.dexterity.content import Item
from plone.supermodel import model
from plone.supermodel.directives import fieldset
from zope import schema
from zope.interface import implementer, Invalid, invariant
from zope.schema.vocabulary import SimpleVocabulary, SimpleTerm

from edi.jsonforms import _
from edi.jsonforms.content.common import IDependentExtended


# upload_answer_types = [
#     SimpleTerm('file', 'file', _('File upload (single upload)')),                   # input
#     SimpleTerm('file-multi', 'file-multi', _('File upload (multi-upload)')),        # <input name='datei[]' type='file' multiple>
# ]
# Upload_answer_types = SimpleVocabulary(upload_answer_types)

possible_file_types = [
    SimpleTerm('application/pdf', 'application/pdf', '.pdf'),

    SimpleTerm('image/jpeg', 'image/jpeg', '.jpg/.jpeg'),
    SimpleTerm('image/png', 'image/png', '.png'),
    SimpleTerm('image/tiff', 'image/tiff', '.tif/.tiff'),
    SimpleTerm('image/gif', 'image/gif', '.gif'),

    # HEIC
    SimpleTerm('image/heic', 'image/heic', '.heic'),
    SimpleTerm('image/heif', 'image/heif', '.heif'),

    # Microsoft Office
    SimpleTerm('application/msword', 'application/msword', '.doc'),
    SimpleTerm('application/vnd.openxmlformats-officedocument.wordprocessingml.document', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document', '.docx'),

    SimpleTerm('application/vnd.ms-excel', 'application/vnd.ms-excel', '.xls'),
    SimpleTerm('application/vnd.openxmlformats-officedocument.spreadsheetml.sheet', 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet', '.xlsx'),

    SimpleTerm('application/vnd.ms-powerpoint', 'application/vnd.ms-powerpoint', '.ppt'),
    SimpleTerm('application/vnd.openxmlformats-officedocument.presentationml.presentation', 'application/vnd.openxmlformats-officedocument.presentationml.presentation', '.pptx'),

    # LibreOffice (ODF)
    SimpleTerm('application/vnd.oasis.opendocument.text', 'application/vnd.oasis.opendocument.text', '.odt'),
    SimpleTerm('application/vnd.oasis.opendocument.spreadsheet', 'application/vnd.oasis.opendocument.spreadsheet', '.ods'),
    SimpleTerm('application/vnd.oasis.opendocument.presentation', 'application/vnd.oasis.opendocument.presentation', '.odp'),
    SimpleTerm('application/vnd.oasis.opendocument.graphics', 'application/vnd.oasis.opendocument.graphics', '.odg'),

    # Apple iWork
    SimpleTerm('application/vnd.apple.pages', 'application/vnd.apple.pages', '.pages'),
    SimpleTerm('application/vnd.apple.numbers', 'application/vnd.apple.numbers', '.numbers'),
    SimpleTerm('application/vnd.apple.keynote', 'application/vnd.apple.keynote', '.key'),

]
Possible_file_types = SimpleVocabulary(possible_file_types)


class IUploadField(IDependentExtended):
    """ Marker interface and Dexterity Python Schema for UploadField
    """
    # answer_type = schema.Choice(title=_('Choose the answer type'),
    #                             source=Upload_answer_types,
    #                             default='file-multi',
    #                             required=True)

    

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
    
    max_file_size = schema.Int(title=_('Maximum file size (in MB)'),
                               description=_('Maximum file size for each uploaded file. If empty, there is no limit.'),
                               required=False,
                               default=5)
    
    max_number_of_files = schema.Int(title=_('Maximum number of files'),
                                     description=_('Maximum number of files that can be uploaded. If empty, there is no limit.'),
                                     required=False,
                                     min=1,
                                     default=1)
    
    min_number_of_files = schema.Int(title=_('Minimum number of files'),
                                     description=_('Minimum number of files that must be uploaded.'),
                                     required=False,
                                     min=1)
    

    @invariant
    def min_max_invariant(data):
        if data.max_number_of_files and data.min_number_of_files:
            if data.max_number_of_files < data.min_number_of_files:
                raise Invalid(_('Maximum cannot be smaller than Minimum.'))
    
    
    


@implementer(IUploadField)
class UploadField(Item):
    """
    """
