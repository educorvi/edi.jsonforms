# from plone.app.textfield import RichText
from plone.app.vocabularies.catalog import CatalogSource
from plone.app.z3cform.widget import RelatedItemsFieldWidget
from plone.supermodel import model
from plone.supermodel.directives import fieldset
from plone.autoform import directives
from zope import schema
from zope.globalrequest import getRequest
from zope.interface import Invalid, invariant
# from zope.interface import provider
# from zope.schema.interfaces import IContextSourceBinder
from zope.schema.vocabulary import SimpleVocabulary, SimpleTerm
from z3c.relationfield.schema import RelationChoice, RelationList
from z3c.form.browser.radio import RadioFieldWidget

from edi.jsonforms import _


required_categories = [
    SimpleTerm('optional', 'optional', _('Optional')),
    SimpleTerm('required', 'required', _('Required'))
]
Required_categories = SimpleVocabulary(required_categories)


def get_base_path(context):
    # basePath = context
    #
    # while basePath.aq_parent.portal_type not in ['Form', 'Complex', 'Array', 'Fieldset']:
    #     basePath = basePath.aq_parent
    #
    # return "/".join(basePath.aq_parent.getPhysicalPath())
    # if context.portal_type in ['Complex', 'Array', 'Fieldset']:
    #     return "/".join(context.getPhysicalPath())
    return get_base_path_parent(context.aq_parent)

def get_base_path_parent(context):
    basePath = context

    while basePath.portal_type not in ['Form', 'Complex', 'Array', 'Fieldset']:
        basePath = basePath.aq_parent

    return "/".join(basePath.getPhysicalPath())


class IFormElement(model.Schema):
    """
    Interface for all content types that can be created within a Form, to check their id with an event handler (that it is unique within the Form).
    """



class IDependent(IFormElement):

    fieldset(
        'dependencies',
        label=_('Dependencies'),
        fields=['dependencies', 'connection_type']
    )

    dependencies = RelationList(
        title=_('Dependent from this answer option:'),
        description=_("If this field(set) should only be displayed based on the answer to another question or a specific option chosen from another question, please specify the question or option it depends on. For example, if the other field is a text line, this field will only be shown if the text line is not empty. If the other field is a number field, this field will only be shown if there is a number in the field and the number is not zero."),
        value_type=RelationChoice(
            vocabulary='plone.app.vocabularies.Catalog',
        ),
        default=[],
        required=False)

    @invariant
    def check_dependencies(data):
        if data.dependencies:
            dependencies = data.dependencies
            try:
                # editing process, object already exists and has a context
                context = data.__context__
                self_base_path = get_base_path(context)
                self_path = "/".join(context.getPhysicalPath())
            except:
                # adding process, object doesn't exist yet and has no context attribute
                context = getRequest().PUBLISHED.context
                self_base_path = get_base_path_parent(context)
                self_path = ""  # irrelevant, cannot depend on itself because it doesn't exist yet

            for dep in dependencies:
                # check that self and object on which dependent are in the same group (complex, array or fieldset. Or Form)
                dep_base_path = get_base_path(dep)
                if not dep_base_path.startswith(self_base_path):
                    raise Invalid(_("Object from which is dependent must be in the same Complex, Array, Fieldset or Form."))

                dep_path = "/".join(dep.getPhysicalPath())
                # check that self isn't dependent from itself and that self isn't dependent from a child (in case of an Array, Fieldset, Complex)
                if dep_path == self_path or (self_path != "" and dep_path.startswith(self_path)):
                    raise Invalid(_("Cannot be dependent from itself or a child from itself."))

    connection_type = schema.Bool(title=_('The dependencies have an AND-connection (default: (inklusive) OR). '
                                          'This option is ignored if less than two dependencies are given.'),
                                  required=False,
                                  default=False)

    # dependencies = RelationChoice(
    #     title=_('Dependent from this answer option:'),
    #     description=_("If this field(set) is only shown when a specific question is answered or an option from another question is chosen, please choose from which (option or field) it is dependent."),
    #     vocabulary="plone.app.vocabularies.Catalog",
    #     required=False
    # )

    directives.widget(
        "dependencies",
        RelatedItemsFieldWidget,
        vocabulary="plone.app.vocabularies.Catalog",
        pattern_options={
            #"basePath": get_base_path,
            "selectableTypes": ["Option", "Field"],
        },
    )

    fieldset(
        'additional-information',
        label=_('Additional Information'),
        fields=['intern_information']
    )

    # previously helptext
    intern_information = schema.Text(title=_('Unformatted intern information for the JSON-Schema'),
                                     description=_('Here you can provide additional information that the Software-Team should to take into account while creating the Form.'),
                                     required=False)
    
    # # TODO no added to ui-schema yet (version 3.1)
    # # TODO translate
    # user_info = schema.Text(title=_('Helptext for the user'),
    #                             description=_("Is displayed as a little i next to the title."),
    #                             required=False)

class IDependentExtended(IDependent):
    title = schema.TextLine(title=_('Title of the field/question'), required=True)

    description = schema.Text(title=_('Description of the field/question'), required=False)

    directives.widget(required_choice=RadioFieldWidget)
    required_choice = schema.Choice(title=_('Selection of Field Requirement'),
                                    source=Required_categories,
                                    default='optional',
                                    required=True)

    fieldset(
        'additional-information',
        label=_('Additional Information'),
        fields=['user_helptext']
    )

    # # previously helptext
    # intern_information = schema.Text(title=_('Unformatted intern information for the JSON-Schema'),
    #                                  description=_('Here you can provide additional information that the Software-Team should to take into account while creating the Form.'),
    #                                  required=False)

    # previously tipp
    # TODO will be displayed as a little "i". Right now ignored. Comes with UI-Schema Version 3.1
    user_helptext = schema.TextLine(title=_('Hint or helptext for the user'),
                             required=False)

