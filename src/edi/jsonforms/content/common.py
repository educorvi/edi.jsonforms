from plone.app.vocabularies.catalog import CatalogSource
from plone.app.z3cform.widget import RelatedItemsFieldWidget
from plone.supermodel import model
from plone.supermodel.directives import fieldset
from plone.autoform import directives
from zope import schema
from zope.globalrequest import getRequest
from zope.interface import Invalid
from zope.interface import provider
from zope.schema.interfaces import IContextSourceBinder
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
    return get_base_path_parent(context.aq_parent)

def get_base_path_parent(context):
    basePath = context

    while basePath.portal_type not in ['Form', 'Complex', 'Array', 'Fieldset']:
        basePath = basePath.aq_parent

    return "/".join(basePath.getPhysicalPath())


def check_dependencies(data):
    import pdb;pdb.set_trace()
    try:
        # editing process, object already exists and has a context
        context = data.context
        self_base_path = get_base_path(context)
        self_path = "/".join(context.getPhysicalPath())
    except:
        # adding process, object doesn't exist yet and has no context attribute
        context = getRequest().PUBLISHED.context
        self_base_path = get_base_path_parent(context)
        self_path = ""  # irrelevant, cannot depend on itself because it doesn't exist yet

    if data.dependencies:
        dependencies = data.dependencies
        for dep in dependencies:
            # check that self and object on which dependent are in the same group (complex, array or fieldset. Or Form)
            dep_base_path = get_base_path(dep)
            if not dep_base_path.startswith(self_base_path):
                raise Invalid(_("Object from which is dependent must be in the same Complex, Array, Fieldset or Form."))

            dep_path = "/".join(dep.getPhysicalPath())
            # check that self isn't dependent from itself
            if dep_path == self_path:
                raise Invalid(_("Cannot be dependent from itself."))


class IDependent(model.Schema):

    fieldset(
        'dependencies',
        label=_('Dependencies'),
        fields=['dependencies', 'connection_type']
    )

    dependencies = RelationList(
        title=_('Dependent from this answer option:'),
        description=_("If this field(set) is only shown when a specific question is answered or an option from another question is chosen, please choose from which (option or field) it is dependent."),
        value_type=RelationChoice(
            vocabulary='plone.app.vocabularies.Catalog',
        ),
        required=False)

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

class IDependentExtended(IDependent):
    title = schema.TextLine(title=_('Title of the field/question'), required=True)

    description = schema.Text(title=_('Description of the field/question'), required=False)

    directives.widget(required_choice=RadioFieldWidget)
    required_choice = schema.Choice(title=_('Selection of Field Requirement'),
                                    source=Required_categories,
                                    default='optional',
                                    required=True)

