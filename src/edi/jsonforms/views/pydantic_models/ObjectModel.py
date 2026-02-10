import copy
import logging
from ZPublisher.HTTPRequest import WSGIRequest

from edi.jsonforms.views.pydantic_models.dependency_handler import (
    add_dependent_required,
    get_dependencies_of_closest_ancestor_with_dependencies,
)
from edi.jsonforms.views.pydantic_models.GeneratorArguments import GeneratorArguments
from plone.base.utils import safe_hasattr
from typing import Optional, List, Dict, Any

from edi.jsonforms.content.common import IFormElement
from edi.jsonforms.content.complex import IComplex
from edi.jsonforms.content.array import IArray
from edi.jsonforms.content.form import Form, IForm

from edi.jsonforms.views.common import check_show_condition_in_request
from edi.jsonforms.views.pydantic_models.FieldModel import FieldModel
from edi.jsonforms.views.pydantic_models.SelectionFieldModel import (
    SelectionFieldModel,
)
from edi.jsonforms.views.pydantic_models.UploadFieldModel import UploadFieldModel

# from edi.jsonforms.views.pydantic_models.ReferenceModel import ReferenceModel
# from edi.jsonforms.views.pydantic_models.ArrayModel import ArrayModel
# from edi.jsonforms.views.pydantic_models.FieldsetModel import FieldsetModel
from edi.jsonforms.views.pydantic_models.BaseFormElementModel import (
    BaseFormElementModel,
)

logger = logging.getLogger(__name__)


# in this file to avoid circular imports, since ObjectModel is needed in the create_model_recursivly function but also used inside the ObjectModel to create child models for complex fields and arrays
def create_model_recursivly(
    form_element: IFormElement,
    parent_model: BaseFormElementModel,
    generatorArguments: GeneratorArguments,
    recursively: bool = True,
) -> BaseFormElementModel:
    """
    returns an object of the model class based on the portal_type of the input content object
    it recursively creates child models for complex fields and arrays and adds them to the properties of the created model
    it also adds the required fields to the required list of the parent model and handles dependencies by
    """
    if form_element.portal_type == "Field":
        model = FieldModel(form_element, parent_model, generatorArguments.request)
    elif form_element.portal_type == "SelectionField":
        model = SelectionFieldModel(
            form_element, parent_model, generatorArguments.request
        )
        if recursively:
            model.set_children(generatorArguments)
    elif form_element.portal_type == "UploadField":
        model = UploadFieldModel(form_element, parent_model, generatorArguments.request)
    elif form_element.portal_type == "Reference":
        model = ReferenceModel(form_element, parent_model, generatorArguments)
        if recursively:
            model.set_children(generatorArguments)
    elif form_element.portal_type in ["Complex", "Form"]:  # handle form like an object
        model = ObjectModel(form_element, parent_model, generatorArguments.request)
        if recursively:
            model.set_children(generatorArguments)
    elif form_element.portal_type == "Array":
        model = ArrayModel(form_element, parent_model, generatorArguments.request)
        if recursively:
            model.set_children(generatorArguments)
    elif form_element.portal_type == "Fieldset":
        model = FieldsetModel(form_element, parent_model, generatorArguments.request)
        if recursively:
            model.set_children(generatorArguments)
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

    properties: Optional[Dict[str, BaseFormElementModel]] = None
    allOf: Optional[List[Dict[str, Dict[str, Any]]]] = None
    required: Optional[List[str]] = None
    dependentRequired: Optional[Dict[str, List[str]]] = None

    def __init__(
        self,
        form_element: IComplex
        | IArray
        | IForm,  # to create the intern object model for array items
        parent_model: Optional[
            BaseFormElementModel
        ],  # is None if form_element is the outer form or if in form-element-view
        request: WSGIRequest,
    ):
        super().__init__(form_element, parent_model, request)
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

    def update_dependentRequired(self, dependentRequired: Dict[str, List[str]]):
        for key, value in dependentRequired.items():
            if key in self.dependentRequired:
                self.dependentRequired[key].extend(value)
            else:
                self.dependentRequired[key] = value

    def set_children(self, generatorArguments: GeneratorArguments):
        """
        :param generatorArguments: arguments to give through the recursive calls

        creates models for all children of the given form_element
        also sets required, dependentrequired and allof of self based on the children's dependencies and required fields
        returns a dict of the created children models (child_id: child_model)
        """
        models = {}
        if safe_hasattr(self.form_element, "getFolderContents"):
            for child in self.form_element.getFolderContents():
                child = child.getObject()
                self.create_and_add_model(
                    child, generatorArguments
                )  # creates child model and adds it to self.properties, dependentRequired etc.

        if self.form_element and isinstance(self.form_element, Form):
            self.update_allOf(generatorArguments.formProperties.allOf)
            self.update_dependentRequired(
                generatorArguments.formProperties.dependentRequired
            )
            self.update_required(generatorArguments.formProperties.required)

        return models

    def create_and_add_model(
        self,
        form_element: IFormElement,
        generatorArguments: GeneratorArguments,
    ) -> Optional[BaseFormElementModel]:
        """
        creates a model for the given form_element based on its portal_type and returns it
        also makes an entry inside the parent_models's required and dependentRequired and allof lists if necessary
        returns None if the form_element should not be shown based on its show_condition and negate_condition
        """

        if not check_show_condition_in_request(
            generatorArguments.request,
            getattr(form_element, "show_condition", None),
            getattr(form_element, "negate_condition", False),
        ):
            return None

        model = create_model_recursivly(form_element, self, generatorArguments)
        if model is None:
            return None

        # give the children the same dependencies as the closest ancestor with dependencies if they have none of their own
        if model.get_dependencies() == []:
            parent_dependencies = (
                get_dependencies_of_closest_ancestor_with_dependencies(model)
            )
            model.extend_dependencies(parent_dependencies)

        # add child model to properties of self
        self.set_property(model.get_id(), model)

        # if child is required, add it to the required list of self
        # unless it has dependencies, then add to allOf or dependentRequired
        if model.is_required:
            if model.check_dependencies(generatorArguments.is_single_view):
                add_dependent_required(
                    generatorArguments.formProperties,
                    model,
                    generatorArguments.is_extended_schema,
                )  # adds child to dependentRequired or allOf of the outer form
            else:
                self.required.append(model.get_id())

        return model

    def get_json_schema(self) -> dict:
        # return dict(self, exclude={"form_element", "parent", "dependencies", "id"})
        excluded_fields = self.get_json_dump_exclude_list().union({"properties"})
        json_schema = self.model_dump(
            exclude=excluded_fields,
            exclude_none=True,
        )
        if json_schema.get("required") == []:
            del json_schema["required"]
        if json_schema.get("dependentRequired") == {}:
            del json_schema["dependentRequired"]
        if json_schema.get("allOf") == []:
            del json_schema["allOf"]

        json_schema["properties"] = {}
        for key, value in self.properties.items():
            if isinstance(value, BaseFormElementModel):
                json_schema["properties"][key] = value.get_json_schema()
        if json_schema.get("properties") == {}:
            del json_schema["properties"]

        return json_schema


###############################


from edi.jsonforms.content.fieldset import IFieldset
# from edi.jsonforms.views.pydantic_models.ObjectModel import ObjectModel
# from edi.jsonforms.views.pydantic_models.GeneratorArguments import GeneratorArguments


class FieldsetModel(ObjectModel):
    """
    This class is different from the other BaseFormElementModel-classes. It does not store any information, but the init method creates the children and stores them in the parent_model
    """

    parent: Optional[ObjectModel]

    def __init__(
        self, form_element: IFieldset, parent_model: ObjectModel, request: WSGIRequest
    ):
        super().__init__(form_element, parent_model, request)

    def set_children(self, generatorArguments: GeneratorArguments):
        super().set_children(generatorArguments)
        self.parent.update_properties(self.properties)
        self.parent.update_required(self.required)
        # self.parent.extend_dependencies(self.dependencies) # are not relevant, were already added to the children's dependencies in the create_and_add_model method
        self.parent.update_dependentRequired(self.dependentRequired)

    def get_json_schema(self) -> dict:
        return {}  # Fieldset does not contribute to the json schema


###################################

# import logging

# from typing import Optional

from edi.jsonforms.content.array import IArray
# from edi.jsonforms.views.pydantic_models.BaseFormElementModel import (
#     BaseFormElementModel,
# )
# from edi.jsonforms.views.pydantic_models.ObjectModel import ObjectModel
# from edi.jsonforms.views.pydantic_models.GeneratorArguments import GeneratorArguments


# logger = logging.getLogger(__name__)


class ArrayModel(BaseFormElementModel):
    items: ObjectModel = None
    type: str = "array"
    minItems: Optional[int] = None

    def __init__(
        self,
        form_element: IArray,
        parent_model: BaseFormElementModel,
        request: WSGIRequest,
    ):
        super().__init__(form_element, parent_model, request)
        if self.is_required:
            self.minItems = 1

    def set_children(self, generatorArguments: GeneratorArguments):
        """
        :param compute_children_method: creates instances of the children models and returns them as a dict (child_id: child_model)
        """
        object_model = ObjectModel(
            self.form_element, self.parent, generatorArguments.request
        )
        object_model.set_children(generatorArguments)
        self.items = object_model

    def get_json_schema(self) -> dict:
        excluded_fields = self.get_json_dump_exclude_list().union({"items"})
        json_schema = self.model_dump(
            exclude=excluded_fields,
            exclude_none=True,
        )
        items_schema = self.items.get_json_schema()
        del items_schema[
            "title"
        ]  # title of the items is not needed in the json schema, since it is not a real form element but just a wrapper for the items of the array
        json_schema["items"] = items_schema
        return json_schema


##################################
from edi.jsonforms.content.reference import IReference


class ReferenceModel(BaseFormElementModel):
    # targetType: str
    target: BaseFormElementModel = None

    def __init__(
        self,
        form_element: IReference,
        parent_model: BaseFormElementModel,
        generatorArguments: GeneratorArguments,
    ):
        super().__init__(form_element, parent_model, generatorArguments.request)

        reference_object = form_element.reference.to_object
        if reference_object:
            # set required of reference to the required_choice of the referenced object
            self.required_choice = (
                reference_object.required_choice
                if safe_hasattr(reference_object, "required_choice")
                else False
            )

            model = create_model_recursivly(
                reference_object, parent_model, generatorArguments, False
            )

            # set id of referenced object to the id of the reference, so it can be found in the properties of the parent model
            model.set_id(self.id)

            # give referenced object model the same dependencies as the reference and afterwards call set_children, so the children also have those dependencies
            dependencies = self.get_dependencies()
            model.set_dependencies(dependencies)

            self.target = model

    def set_children(self, generatorArguments: GeneratorArguments):
        if safe_hasattr(self.target, "set_children"):
            self.target.set_children(generatorArguments)

    # method to get json schema, overwrites standard method
    def get_json_schema(self) -> dict:
        if self.target:
            return self.target.get_json_schema()
        else:
            return {}
