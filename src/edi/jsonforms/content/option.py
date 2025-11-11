# -*- coding: utf-8 -*-
# from plone.app.textfield import RichText
# from plone.autoform import directives
from plone.dexterity.content import Item

# from plone.namedfile import field as namedfile
# from plone.supermodel import model

# from plone.supermodel.directives import fieldset
# from z3c.form.browser.radio import RadioFieldWidget
from zope import schema
from zope.interface import implementer

# from zope.schema.vocabulary import SimpleVocabulary, SimpleTerm
from zope.globalrequest import getRequest
from zope.interface import Invalid, invariant


from edi.jsonforms import _
from edi.jsonforms.content.common import IDependent


class IOption(IDependent):
    """Marker interface and Dexterity Python Schema for Option"""

    title = schema.TextLine(title=_("Label of the answer option"))

    connection_type = schema.Bool(
        title=_(
            "The dependencies have an AND-connection (default: (inklusive) OR). "
            "This option is ignored if less than two dependencies are given."
        ),
        readonly=True,
    )

    @invariant
    def check_dependencies(data):
        # def get_parent_form(context):
        #     current = context
        #     try:
        #         while current.portal_type != "Form":
        #             current = current.aq_parent
        #     except Exception:
        #         return None
        #     return current
        def get_parent(context):
            current = context
            try:
                i = 0
                current = current.aq_parent
                while current.portal_type == "Fieldset":
                    i += 1
                    if i > 100:
                        raise Invalid(
                            _("Could not determine parent SelectionField.")
                        )  # avoid infinite loop]:
                    current = current.aq_parent
            except Exception:
                return None
            return current

        if data.dependencies:
            dependencies = data.dependencies
            try:
                # editing process, object already exists and has a context
                context = data.__context__
            except Exception:
                # adding process, object doesn't exist yet and has no context attribute
                context = getRequest().PUBLISHED.context

            option_parent = context.aq_parent
            for dep in dependencies:
                dep_parent = dep.aq_parent
                if dep.portal_type != "Option":
                    raise Invalid(_("Dependency must be an option."))
                if get_parent(dep.aq_parent) != get_parent(
                    context.aq_parent
                ):  # get parents of the SelectionFields
                    raise Invalid(
                        _(
                            "Selectionfields of the option and the dependent option must be in the same container."
                        )
                    )
                if dep_parent == option_parent:
                    raise Invalid(
                        _("Dependency must not be in the same SelectionField.")
                    )
                # if context == dep:
                #     raise Invalid(_("Cannot be dependent from itself.")) # already covered by "not in the same SelectionField" check


@implementer(IOption)
class Option(Item):
    """ """
