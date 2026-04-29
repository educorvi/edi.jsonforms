# -*- coding: utf-8 -*-
# from plone.app.textfield import RichText
# from plone.autoform import directives
from plone.dexterity.content import Container
from plone.autoform import directives
from plone.app.z3cform.widget import RelatedItemsFieldWidget

# from plone.namedfile import field as namedfile
from plone.supermodel import model

# from plone.supermodel.directives import fieldset
# from z3c.form.browser.radio import RadioFieldWidget
# from zope import schema
from zope.interface import implementer
from z3c.relationfield.schema import RelationChoice
from zope.interface import Invalid, invariant
from zope.globalrequest import getRequest


from edi.jsonforms import _
from edi.jsonforms.content.common import IDependent, IFormElement
import logging

logger = logging.getLogger(__name__)


class IReference(IDependent):
    """Marker interface and Dexterity Python Schema for Reference"""

    reference = RelationChoice(
        title=_("Reference"),
        required=True,
        description=_("Reference to another Form Element (e.g. Field or Array)"),
        vocabulary="plone.app.vocabularies.Catalog",
    )

    @invariant
    def check_reference(data):
        if data.reference:
            try:
                ref_obj = data.reference
            except Exception as e:
                logger.warning(f"Error accessing reference object: {e}")
                raise Invalid(
                    _("The referenced object is either empty or deleted/invalid.")
                )

            if ref_obj.portal_type == "Fieldset":
                raise Invalid(_("You cannot reference a Fieldset."))
            elif ref_obj.portal_type == "Reference":
                raise Invalid(_("You cannot reference a Reference."))
            elif ref_obj.portal_type == "Form":
                raise Invalid(_("You cannot reference a Form."))
            elif ref_obj == data:
                raise Invalid(_("You cannot reference the object itself."))

            elif data.dependencies:
                for dep in data.dependencies:
                    if ref_obj == dep:
                        raise Invalid(
                            _("You cannot depend on the object that is referenced.")
                        )

            def get_parent_form(obj):
                try:
                    parent = obj.aq_parent
                except Exception as e:
                    logger.warning(f"Error accessing parent object: {e}")
                    try:
                        parent = data.__context__.aq_parent
                    except Exception as e:
                        logger.warning(f"Error accessing context parent object: {e}")
                        try:
                            parent = getRequest().PUBLISHED.context.aq_parent
                        except Exception as e:
                            logger.warning(
                                f"Error accessing request parent object: {e}"
                            )
                            raise Invalid(_("Could not determine the parent Form."))

                if parent.portal_type in ["Form"]:
                    return parent
                elif IFormElement.providedBy(parent):
                    return get_parent_form(parent)
                else:
                    raise Invalid(_("The referenced object is not within a Form."))

            try:
                ref_form = get_parent_form(ref_obj)
                own_form = get_parent_form(data)

                if ref_form != own_form:
                    raise Invalid(
                        _("The referenced object is not within the same Form.")
                    )
            except Invalid as e:
                raise e


@implementer(IReference)
class Reference(Container):
    """Content-type class for IReference"""
