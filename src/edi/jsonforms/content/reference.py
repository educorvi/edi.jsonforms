# -*- coding: utf-8 -*-
# from plone.app.textfield import RichText
# from plone.autoform import directives
from plone.dexterity.content import Container
# from plone.namedfile import field as namedfile
from plone.supermodel import model
# from plone.supermodel.directives import fieldset
# from z3c.form.browser.radio import RadioFieldWidget
# from zope import schema
from zope.interface import implementer
from z3c.relationfield.schema import RelationChoice
from zope.interface import Invalid, invariant


from edi.jsonforms import _
from edi.jsonforms.content.common import IDependent, IFormElement


class IReference(IDependent):
    """ Marker interface and Dexterity Python Schema for Reference
    """
    reference = RelationChoice(
            title=_("Reference"),
            required=True,
            description=_("Reference to another Form Element (i.e. Field, Array or Fieldset)"),
            #source=CatalogSource(portal_type=['Form', 'Complex', 'Array', 'Fieldset'], base_path=get_base_path),
            vocabulary='plone.app.vocabularies.Catalog',
    )

    @invariant
    def check_reference(data):
        if data.reference:
            try:
                ref_obj = data.reference
            except:
                raise Invalid(_("The referenced object is either empty or deleted/invalid."))
            
            if ref_obj.portal_type == 'Fieldset':
                raise Invalid(_("You cannot reference a Fieldset."))
            elif ref_obj.portal_type == 'Reference':
                raise Invalid(_("You cannot reference a Reference."))
            elif ref_obj.portal_type == 'Form':
                raise Invalid(_("You cannot reference a Form."))
            elif ref_obj == data:
                raise Invalid(_("You cannot reference the object itself."))
            
            elif data.dependencies:
                for dep in data.dependencies:
                    if ref_obj == dep:
                        raise Invalid(_("You cannot depend on the object that is referenced."))

            import pdb; pdb.set_trace()
            def get_parent_form(obj):
                parent = obj.aq_parent
                if parent.portal_type in ['Form']:
                    return parent
                elif isinstance(parent.portal_type, IFormElement):
                    return get_parent_form(parent)
                else:
                    raise Invalid(_("The referenced object is not within a Form."))
            
            try:
                ref_form = get_parent_form(ref_obj)
                own_form = get_parent_form(data)
                
                if ref_form != own_form:
                    raise Invalid(_("The referenced object is not within the same Form."))
            except Invalid as e:
                raise e


@implementer(IReference)
class Reference(Container):
    """ Content-type class for IReference
    """
