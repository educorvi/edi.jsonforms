import copy
import logging
from plone.base.utils import safe_hasattr

from edi.jsonforms.views.common import create_id, check_show_condition_in_request
from edi.jsonforms.content.common import IFormElement
from edi.jsonforms.content.array import IArray
from edi.jsonforms.content.complex import IComplex
from edi.jsonforms.views.pydantic_models.models import (
    BaseFormElementModel,
    FieldModel,
    SelectionFieldModel,
    UploadFieldModel,
    ReferenceModel,
    ObjectModel,
    ArrayModel,
    FieldsetModel,
    HelptextModel,
    ButtonHandlerModel,
)

logger = logging.getLogger(__name__)


# put these methods into the JsonSchemaView class so they can access necessary context variables like request or is_single_view


def create_basic_model(
    form_element: IFormElement, parent_model: BaseFormElementModel
) -> BaseFormElementModel:
    """
    returns an object of the model class based on the portal_type of the input content object
    """
    if form_element.portal_type == "Field":
        model = FieldModel(form_element, parent_model)
    elif form_element.portal_type == "SelectionField":
        model = SelectionFieldModel(form_element, parent_model)
    elif form_element.portal_type == "UploadField":
        model = UploadFieldModel(form_element, parent_model)
    elif form_element.portal_type == "Reference":
        model = ReferenceModel(form_element, parent_model)
    elif form_element.portal_type == "Complex":
        model = ObjectModel(form_element, parent_model)
    elif form_element.portal_type == "Array":
        model = ArrayModel(form_element, parent_model)
    elif form_element.portal_type == "Fieldset":
        model = FieldsetModel(form_element, parent_model)  # TODO
    elif form_element.portal_type == "Helptext":
        model = HelptextModel(form_element, parent_model)  # has no json schema
    elif form_element.portal_type == "Button Handler":
        model = ButtonHandlerModel(form_element, parent_model)  # has no json schema
    else:
        logger.error(f"Unknown portal_type: {form_element.portal_type}")
        return None  # return empty dict for unknown types

    if model:
        model.compute_fields()
    return model


def create_model(
    form_element: IFormElement, parent_model: BaseFormElementModel
) -> BaseFormElementModel:
    """
    creates a model for the given form_element based on its portal_type and returns it

    """

    if not check_show_condition_in_request(
        self.request,
        getattr(form_element, "show_condition", None),
        getattr(form_element, "negate_condition", False),
    ):
        return None
    model = create_basic_model(form_element, parent_model)
    if model.required:
        if model.dependencies:
            add_dependent_required_to_parent(model, parent_model)
        else:
            parent_model.required.append(model.id)

    return model


def create_models_for_children(parent_model: ObjectModel | ArrayModel) -> dict:
    """
    creates models for all children of the given form_element and returns them as a dict
    """

    # give the children the same dependencies as the parent plus their own
    parent_dependencies = []
    if parent_model.portal_type != "Form":
        parent_dependencies = (
            copy.copy(parent_model.dependencies)
            if safe_hasattr(parent_model, "dependencies")
            else []
        )

    models = {}
    if hasattr(parent_model, "getFolderContents"):
        for child in parent_model.getFolderContents():
            child = child.getObject()

            if child.portal_type not in ["Option", "OptionList"]:
                child.dependencies = parent_dependencies + child.dependencies
            model = create_model(child, parent_model)
            if model:
                models[create_id(child)] = model
    return models
