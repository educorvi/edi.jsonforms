# -*- coding: utf-8 -*-
from plone.dexterity.content import Item
from plone.supermodel import model
from zope import schema
from zope.interface import implementer
from zope.schema.vocabulary import SimpleVocabulary, SimpleTerm
from edi.jsonforms import _
from edi.jsonforms.content.common import IFormElement


class IOptionList(IFormElement):
    """ Marker interface and Dexterity Python Schema for Option
    """
    options = schema.List(title=_('Options'),
                          description=_('List of options. Every line contains one option. Options can either be values only or have an id in the format "id:value". IDs are only used if "Use id of options in schema" is checked in the parent field.'),
                          required=True,
                          value_type=schema.TextLine(title=_('Option'), required=True),
                          default=[])





@implementer(IOptionList)
class OptionList(Item):
    """
    """


def get_keys_and_values_for_options_list(ol):
    keys = [to.split(':')[0] for to in ol.options]
    split_arrays = [to.split(':') for to in ol.options]
    values = []
    for split_array in split_arrays:
        if len(split_array) == 1:
            values.append(split_array[0])
        elif len(split_array) == 2:
            values.append(split_array[1])
        else:
            values.append(':'.join(split_array[1:]))
    return keys, values
