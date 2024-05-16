from plone.app.vocabularies.catalog import CatalogSource
from plone.supermodel import model
from plone.supermodel.directives import fieldset
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


@provider(IContextSourceBinder)
def get_possible_options(context):
    if context is None or context.dependent_from_question is None:
        return SimpleVocabulary([])
    # TODO alle optionen zurückgeben von ausgewählter/n fragen
    import pdb; pdb.set_trace()
    question = context.dependent_from_question
    terms = []
    options = question.to_object.getFolderContents() #
    #*** AccessControl.unauthorized.Unauthorized: You are not allowed to access '_Access_inactive_portal_content_Permission' in this context
    for o in options:
        pass
        # possible_options.append(
        #     SimpleVocabulary.createTerm(
        #         opts,         # test this
        #         opts,         # test this
        #         opts.Title    # test this
        #     )
        # )
    return SimpleVocabulary(terms)


class IDependent(model.Schema):
    fieldset(
        'dependencies',
        label=_('Dependencies'),
        fields=('dependent_from_question', 'required_option') #, 'dependent_from_questions', 'required_options')
    )

    # dependent_from_question = RelationChoice(title=_('Dependent from this field:'),
    #                                       description=_(
    #                                           "If this field(set) is only shown when a specific answer from another question is chosen, please choose the question from which it is dependent."),
    #                                       vocabulary='plone.app.vocabularies.Catalog',
    #                                       required=False)

    # TODO in ui loading failed. why?
    dependent_from_question = RelationChoice(title=_('Dependent from this field'),
                                              description=_("If this field(set) is only shown when a specific answer from another question is chosen, please choose the question from which it is dependent."),
                                              source=CatalogSource(portal_type=['SelectionField']),
                                              required=False,)

    # dependent_from_questions = RelationList(title=_('Dependent from these fields:'),
    #                                          description=_(
    #                                              "If this field(set) is only shown when a specific answer from another question is chosen, please choose the questions from which it is dependent."),
    #                                          default=[],
    #                                          value_type=RelationChoice(
    #                                              title=_('Field'),
    #                                              source=CatalogSource(portal_type=['SelectionField'])),
    #                                           required=False,)
    # todo kann von mehreren abhängen?
    # todo nur fragen auswählbar, die optionen haben? oder auch welche wo nur textinput etc




    required_option = RelationChoice(title=_('Dependent from these options:'),
                                      description=_('Choose the options from the selected question(s) from which it is dependent.'),
                                      source=get_possible_options,
                                      required=False)

    # required_options = RelationList(title=_('Dependent from these options:'),
    #                                       description=_('Choose the options from the selected question(s) from which it is dependent.'),
    #                                       default=[],
    #                                       value_type=RelationChoice(
    #                                           title=_('Option'),
    #                                           source=get_possible_options),
    #                                       required=False,)

    # todo validator, dass required_option ausgefüllt wenn dependent_from_question ausgefüllt)

