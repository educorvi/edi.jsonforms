import abc
import logging

from plone.base.utils import safe_hasattr
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any, override

from edi.jsonforms.content.common import IFormElement
from edi.jsonforms.content.field import IField
from edi.jsonforms.content.selection_field import ISelectionField
from edi.jsonforms.content.upload_field import IUploadField
from edi.jsonforms.content.complex import IComplex
from edi.jsonforms.content.array import IArray
from edi.jsonforms.content.reference import IReference
from edi.jsonforms.content.option import IOption
from edi.jsonforms.content.option_list import OptionList, get_keys_and_values_for_options_list
from edi.jsonforms.views.common import get_title, get_description, create_id

logger = logging.getLogger(__name__)


class JsonSchemaModel(BaseModel):
    type: str = "object"
    properties: dict
    required: List[str] = []
    allOf: Optional[List[dict]] = []


class BaseFormElementModel(abc.ABC):
    form_element: IFormElement
    id: str
    title: str
    description: Optional[str]
    comment: Optional[str]
    type: Optional[str]
    parent: "BaseFormElementModel"
    required: Optional[bool] = False
    dependencies: Optional[List['BaseFormElementModel']] = []

    def __init__(self, form_element: IFormElement, parent_model: "BaseFormElementModel"):
        self.id = create_id(form_element)
        self.form_element = form_element
        self.title = get_title(form_element)
        self.description = get_description(form_element)
        self.comment = (
            form_element.intern_information
            if safe_hasattr(form_element, "intern_information")
            else None
        )
        self.parent = parent_model
        self.required = (
            form_element.required_choice
            if safe_hasattr(form_element, "required_choice")
            else False
        )

    def compute_fields(self):
        pass  # TODO implement common field computations like dependencies and children etc


class FieldModel(BaseFormElementModel):
    minLength: Optional[int]
    maxLength: Optional[int]
    pattern: Optional[str]
    format: Optional[str]
    minimum: Optional[float]
    maximum: Optional[float]

    def __init__(self, form_element: IField, parent_model: BaseFormElementModel):
        super().__init__(form_element, parent_model)
        answer_type = form_element.answer_type
        if answer_type in ["text", "textarea", "password"]:
            self.type = "string"
            if form_element.minimum:
                self.minLength = form_element.minimum
            if form_element.maximum:
                self.maxLength = form_element.maximum
        elif answer_type == "tel":
            self.type = "string"
            self.pattern = "^\+?(\d{1,3})?[-.\s]?(\(?\d{1,4}\)?)?[-.\s]?\d{1,4}[-.\s]?\d{1,4}[-.\s]?\d{1,9}$"
            # or simply '^[\d+\-()\s]{1,25}$' (max 25 symbols, +, -, (, ), numbers and space are allowed
        elif answer_type == "url":
            self.type = "string"
            self.format = "hostname"
        elif answer_type == "email":
            self.type = "string"
            self.format = "email"
        elif answer_type == "date":
            self.type = "string"
            self.format = "date"
        elif answer_type == "datetime-local":
            self.type = "string"
            self.format = "date-time"
        elif answer_type == "time":
            self.type = "string"
            self.format = "time"
        elif answer_type == "number":
            self.type = "number"
        elif answer_type == "integer":
            self.type = "integer"
        elif answer_type == "boolean":
            self.type = "boolean"

        if answer_type in ["number", "integer"]:
            if form_element.minimum:
                self.minimum = form_element.minimum
            if form_element.maximum:
                self.maximum = form_element.maximum


class OptionModel(BaseModel):
    id: str
    title: str
    parent: ISelectionField

    def __init__(self, option: IOption):
        self.id = create_id(option)
        self.title = get_title(option)
        self.parent = option.aq_parent

    def __init__(self, id: str, title: str, parent: ISelectionField):
        self.id = id
        self.title = title
        self.parent = parent

    # a get method for name (title or id)
    def get_option_name(self) -> str:
        if self.parent.use_id_in_schema:
            return self.id
        else:
            return self.title


class OptionListModel(BaseModel):
    options: List[OptionModel]

    def __init__(self, option_list: OptionList):
        o_keys, o_values = get_keys_and_values_for_options_list(option_list)
        self.options = []
        for key, value in zip(o_keys, o_values):
            option_model = OptionModel(key, value, option_list.aq_parent)
            self.options.append(option_model)

    def get_option_names(self) -> List[str]:
        return [option.get_option_name() for option in self.options]


class SelectionFieldModel(BaseFormElementModel):
    enum: Optional[List[str]]
    items: Optional[Dict[str, List[str] | str]]

    def __init__(self, form_element: ISelectionField, parent_model: BaseFormElementModel):
        super().__init__(form_element, parent_model)

        answer_type = form_element.answer_type

        if answer_type == "radio" or answer_type == "select":
            self.type = "string"
            # self.enum = options_list
        elif answer_type == "checkbox" or answer_type == "selectmultiple":
            self.type = "array"
            # self.items = {"enum": options_list, "type": "string"}

    @override
    def compute_fields(self):
        super().compute_fields()
        options = self.form_element.getFolderContents()

        options_list = []
        for o in options:
            # options_list.extend(
            #     self.get_values_for_selectionfield(form_element, o, self.is_single_view)
            # )
        
        if self.type == "string":
            self.enum = options_list
        elif self.type == "array":
            self.items = {"enum": options_list, "type": "string"}

        # schema["allOf"].extend(self.get_dependent_options(child_object))



class UploadFieldModel(BaseFormElementModel):
    minItems: Optional[int]
    maxItems: Optional[int]
    format: Optional[str]
    items: Optional[dict]
    maxSize: Optional[int]
    allowedTypes: Optional[List[str]]

    def __init__(self, form_element: IUploadField, parent_model: BaseFormElementModel):
        super().__init__(form_element, parent_model)
        self.minItems = form_element.min_number_of_files

        if form_element.max_number_of_files:
            if form_element.max_number_of_files == 1:
                self.type = "string"
                self.format = "uri"
            else:
                self.type = "array"
                self.items = {
                    "type": "string",
                    "format": "uri",
                }
                self.maxItems = form_element.max_number_of_files
        else:
            self.type = "array"
            self.items = {
                "type": "string",
                "format": "uri",
            }

        self.maxSize = form_element.max_size
        self.allowedTypes = form_element.allowed_types


class ReferenceModel(BaseFormElementModel):
    targetType: str
    target: BaseFormElementModel

    def __init__(self, form_element: IReference, parent_model: BaseFormElementModel):
        super().__init__(form_element, parent_model)
        self.targetType = form_element.target_type

    # method to get json schema, overwrites standard method
    def get_json_schema(self) -> dict:
        pass
        # try:
        #     obj = reference.reference.to_object
        #     if obj:
        #         obj_schema = self.get_schema_for_child(obj)
        #         return obj_schema
        # except:  # referenced object got deleted, ignore
        #     return {}


class ObjectModel(BaseFormElementModel):
    type: str = "object"

    properties: Optional[Dict[str, Any]] = None
    allOf: Optional[List[Dict[str, Any]]] = None

    def __init__(self, form_element: IComplex, parent_model: BaseFormElementModel):
        super().__init__(form_element, parent_model)

        # self.properties = {}
        # self.allOf = []
        # self.required = []
        # self.dependentRequired = {}

        # children = form_element.getFolderContents()
        # for child in children:
        #     child = child.getObject()
        #     child_model = create_model(child)

        ####self.add_child_to_schema(child_object, complex_schema)


class ArrayModel(BaseFormElementModel):
    items: BaseFormElementModel
    type: str = "array"
    minItems: Optional[int]

    def __init__(self, form_element: IArray, parent_model: BaseFormElementModel):
        super().__init__(form_element, parent_model)
        if self.required:
            self.minItems = 1
        # array_schema["items"] = self.get_schema_for_object(array)

class FieldsetModel(BaseFormElementModel):


    def get_json_schema(self) -> dict:
        return {}  # Fieldset does not contribute to the json schema


class HelptextModel(BaseFormElementModel):
    # type: str = "string"

    # def __init__(self, form_element: IFormElement, parent_model: BaseFormElementModel):
    #     super().__init__(form_element, parent_model)

    def get_json_schema(self) -> dict:
        return {}  # Helptext does not contribute to the json schema
    

class ButtonHandlerModel(BaseFormElementModel):
    # type: str = "string"

    # def __init__(self, form_element: IFormElement, parent_model: BaseFormElementModel):
    #     super().__init__(form_element, parent_model)

    def get_json_schema(self) -> dict:
        return {}  # Button Handler does not contribute to the json schema
