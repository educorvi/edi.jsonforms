from plone.app.vocabularies.catalog import CatalogSource
from plone.supermodel import model
from plone.supermodel.directives import fieldset
from zope import schema
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
        fields=('dependent_from_question', 'required_option', 'dependent_from_question2')
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

    dependent_from_question2 = RelationList(title=_('Dependent from these fields:'),
                                             description=_(
                                                 "If this field(set) is only shown when a specific answer from another question is chosen, please choose the questions from which it is dependent."),
                                             default=[],
                                             value_type=RelationChoice(
                                                 title=_('Field'),
                                                 source=CatalogSource(portal_type=['SelectionField'])),
                                              required=False,)
    # todo kann von mehreren abhängen?
    # todo nur fragen auswählbar, die optionen haben? oder auch welche wo nur textinput etc

    def get_possible_answer_options(self):
        pass
        # TODO alle optionen zurückgeben von ausgewählter/n fragen
        # possible_options = {}
        # obj = plone.api.content.get(self.dependent_from_question)
        # options = obj.getFolderContents()
        # for o in options:
        #     possible_options.append(o)


    required_option = schema.TextLine(title=_('Dependent from these options'),
                                      description='Choose the options from the selected question(s) from which it is dependent.',
                                      required=False)

    # todo validator, dass required_option ausgefüllt wenn dependent_from_question ausgefüllt)

