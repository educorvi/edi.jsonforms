import copy
import logging

from edi.jsonforms.views.pydantic_models import FieldsetModel
from edi.jsonforms.views.pydantic_models.dependency_handler import (
    add_dependent_required,
)
from edi.jsonforms.views.pydantic_models.schema_generator import JsonSchemaGenerator
from plone.base.utils import safe_hasattr
from typing import Optional, List, Dict, Any

from edi.jsonforms.content.common import IFormElement

from edi.jsonforms.views.common import check_show_condition_in_request
from edi.jsonforms.views.pydantic_models.FieldModel import FieldModel
from edi.jsonforms.views.pydantic_models.SelectionFieldModel import (
    SelectionFieldModel,
)
from edi.jsonforms.views.pydantic_models.UploadFieldModel import UploadFieldModel
from edi.jsonforms.views.pydantic_models.ReferenceModel import ReferenceModel
from edi.jsonforms.views.pydantic_models.ArrayModel import ArrayModel
from edi.jsonforms.content.complex import IComplex
from edi.jsonforms.content.array import IArray
from edi.jsonforms.views.pydantic_models.BaseFormElementModel import (
    BaseFormElementModel,
)

logger = logging.getLogger(__name__)


# in this file to avoid circular imports, since ObjectModel is needed in the create_model_recursivly function but also used inside the ObjectModel to create child models for complex fields and arrays
def create_model_recursivly(
    form_element: IFormElement,
    parent_model: BaseFormElementModel,
    json_schema_generator: JsonSchemaGenerator,
) -> BaseFormElementModel:
    """
    returns an object of the model class based on the portal_type of the input content object
    it recursively creates child models for complex fields and arrays and adds them to the properties of the created model
    it also adds the required fields to the required list of the parent model and handles dependencies by
    """
    if form_element.portal_type == "Field":
        model = FieldModel(form_element, parent_model)
    elif form_element.portal_type == "SelectionField":
        model = SelectionFieldModel(form_element, parent_model)
        model.set_children(json_schema_generator)
    elif form_element.portal_type == "UploadField":
        model = UploadFieldModel(form_element, parent_model)
    elif form_element.portal_type == "Reference":
        model = ReferenceModel(form_element, parent_model)
    elif form_element.portal_type == "Complex":
        model = ObjectModel(form_element, parent_model)
        model.set_children(json_schema_generator)
    elif form_element.portal_type == "Array":
        model = ArrayModel(form_element, parent_model)
        model.set_children(json_schema_generator)
    elif form_element.portal_type == "Fieldset":
        model = FieldsetModel(form_element, parent_model)
        model.set_children(json_schema_generator)
        model = None  # Fieldset does not contribute to the json schema, the children are added to the parent model of the Fieldset, so we return None here to avoid adding the fieldset itself as a property to the parent model
    elif form_element.portal_type == "Helptext":
        # model = HelptextModel(form_element, parent_model)  # has no json schema
        return None
    elif form_element.portal_type == "Button Handler":
        # model = ButtonHandlerModel(form_element, parent_model)  # has no json schema
        return None
    else:
        logger.error(f"Unknown portal_type: {form_element.portal_type}")
        return None  # return empty dict for unknown types

    return model


class ObjectModel(BaseFormElementModel):
    type: str = "object"

    properties: Optional[Dict[str, BaseFormElementModel]]
    allOf: Optional[List[Dict[str, Dict[str, Any]]]]
    required: Optional[List[str]]
    dependentRequired: Optional[Dict[str, List[str]]]

    def __init__(
        self,
        form_element: IComplex
        | IArray,  # to create the intern object model for array items
        parent_model: BaseFormElementModel,
    ):
        super().__init__(form_element, parent_model)
        self.properties = {}
        self.allOf = []
        self.required = []
        self.dependentRequired = {}

    def set_property(self, property_id: str, property_model: BaseFormElementModel):
        self.properties[property_id] = property_model

    def update_properties(self, properties: Dict[str, BaseFormElementModel]):
        self.properties.update(properties)

    def update_allOf(self, allOf: List[Dict[str, Dict[str, Any]]]):
        self.allOf.extend(allOf)

    def update_required(self, required: List[str]):
        self.required.extend(required)

    def set_children(self, json_schema_generator: JsonSchemaGenerator):
        """
        :param parent_model: the model whose children should be created and which is also adapted

        creates models for all children of the given form_element
        also sets required, dependentrequired and allof of parent_model based on the children's dependencies and required fields
        returns a dict of the created children models (child_id: child_model)
        """

        models = {}
        if safe_hasattr(self.form_element, "getFolderContents"):
            for child in self.form_element.getFolderContents():
                child = child.getObject()
                self.create_and_add_model(
                    child, json_schema_generator
                )  # creates child model and adds it to self.properties, dependentRequired etc.

        return models

    def create_and_add_model(
        self, form_element: IFormElement, json_schema_generator: JsonSchemaGenerator
    ) -> Optional[BaseFormElementModel]:
        """
        creates a model for the given form_element based on its portal_type and returns it
        also makes an entry inside the parent_models's required and dependentRequired and allof lists if necessary
        returns None if the form_element should not be shown based on its show_condition and negate_condition
        """

        if not check_show_condition_in_request(
            self.request,
            getattr(form_element, "show_condition", None),
            getattr(form_element, "negate_condition", False),
        ):
            return None

        model = create_model_recursivly(form_element, self)

        # give the children the same dependencies as the parent plus their own
        parent_dependencies = (
            copy.copy(self.dependencies) if safe_hasattr(self, "dependencies") else []
        )
        model.extend_dependencies(parent_dependencies)

        if model:
            self.set_property(model.get_id(), model)

        if model.required:
            if model.check_dependencies(json_schema_generator.is_single_view):
                add_dependent_required(
                    json_schema_generator.form,
                    model,
                    json_schema_generator.is_extended_schema,
                )  # adds child to dependentRequired or allOf of the outer form
            else:
                self.required.append(model.get_id())

        return model
