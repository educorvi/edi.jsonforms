from plone.app.vocabularies.catalog import CatalogSource
from plone.app.z3cform.widget import RelatedItemsFieldWidget
from plone.supermodel import model
from plone.supermodel.directives import fieldset
from plone.autoform import directives
from zope import schema
from zope.interface import provider
from zope.schema.interfaces import IContextSourceBinder
from zope.schema.vocabulary import SimpleVocabulary, SimpleTerm
from z3c.relationfield.schema import RelationChoice, RelationList

from edi.jsonforms import _


required_categories = [
    SimpleTerm('optional', 'optional', _('Optional')),
    SimpleTerm('required', 'required', _('Required'))
]
Required_categories = SimpleVocabulary(required_categories)


class IDependent(model.Schema):

    fieldset(
        'dependencies',
        label=_('Dependencies'),
        fields=['dependent_from_object']
    )

    # dependent_from_object = RelationList(
    #     title=_('Dependent from this answer option:'),
    #     description=_("If this field(set) is only shown when a specific question is answered or an option from another question is chosen, please choose from which (option or field) it is dependent."),
    #     value_type=RelationChoice(
    #         vocabulary="plone.app.vocabularies.Catalog",
    #     ),
    #     required=False)
    dependent_from_object = RelationChoice(
        title=_('Dependent from this answer option:'),
        description=_("If this field(set) is only shown when a specific question is answered or an option from another question is chosen, please choose from which (option or field) it is dependent."),
        vocabulary="plone.app.vocabularies.Catalog",
        required=False
    )

    directives.widget(
        "dependent_from_object",
        RelatedItemsFieldWidget,
        vocabulary="plone.app.vocabularies.Catalog",
        pattern_options={
            "selectableTypes": ["Option", "Field"],
        },
    )
