import abc
import copy
import logging

from plone.base.utils import safe_hasattr
from typing import Optional, List
from ZPublisher.HTTPRequest import WSGIRequest, HTTPRequest

from edi.jsonforms.content.common import IFormElement
from edi.jsonforms.content.form import IForm

from edi.jsonforms.views.common import (
    get_title,
    get_description,
    create_id,
)
from pydantic import BaseModel, Field
# from edi.jsonforms.views.pydantic_models.schema_generator import (
#     JsonSchemaGenerator,
# )

logger = logging.getLogger(__name__)


class BaseFormElementModel(BaseModel, abc.ABC):
    form_element: IFormElement
    id: str
    title: str
    description: Optional[str] = None
    comment: Optional[str] = None
    type: Optional[str] = None
    parent: Optional[
        "BaseFormElementModel"
    ]  # actually it can only be an ObjectModel or a model that extends this (Form)
    required_choice: Optional[bool] = False
    dependencies: Optional[List[IFormElement]] = Field(default_factory=list)

    class Config:
        arbitrary_types_allowed = True

    def __init__(
        self,
        form_element: IFormElement | IForm,
        parent_model: Optional[
            "BaseFormElementModel"
        ],  # only None if form_element is the outer form
        request: WSGIRequest | HTTPRequest,
    ):
        description = get_description(form_element, request)
        comment = (
            form_element.intern_information
            if safe_hasattr(form_element, "intern_information")
            else None
        )
        required_choice = (
            True
            if safe_hasattr(form_element, "required_choice")
            and form_element.required_choice == "required"
            else False
        )
        dependencies = (
            copy.copy(form_element.dependencies)
            if safe_hasattr(form_element, "dependencies")
            else []
        )
        super().__init__(
            form_element=form_element,
            id=create_id(form_element),
            title=get_title(form_element, request),
            description=description if description else None,
            comment=comment,
            parent=parent_model,
            required_choice=required_choice,
            dependencies=dependencies,
        )
        # self.id = create_id(form_element)
        # self.form_element = form_element
        # self.title = get_title(form_element, request)
        # self.description = get_description(form_element, request)
        # self.comment = (
        #     form_element.intern_information
        #     if safe_hasattr(form_element, "intern_information")
        #     else None
        # )
        # self.parent = parent_model
        # self.required = (
        #     form_element.required_choice
        #     if safe_hasattr(form_element, "required_choice")
        #     else False
        # )
        # if safe_hasattr(form_element, "dependencies"):
        #     self.dependencies = copy.copy(form_element.dependencies)

    @property
    def is_required(self) -> bool:
        return self.required_choice

    def get_id(self) -> str:
        return self.id

    def set_id(self, id: str):
        self.id = id

    def get_dependencies(self) -> List[IFormElement]:
        return self.dependencies

    def extend_dependencies(self, dependencies: List[IFormElement]):
        self.dependencies.extend(dependencies)

    def set_dependencies(self, dependencies: List[IFormElement]):
        self.dependencies = dependencies

    def check_dependencies(self, is_single_view: bool) -> bool:
        # check_for_dependencies(self, is_single_view)
        if is_single_view:  # if form-element-view, ignore all dependencies
            return False
        if self.dependencies:
            return True
        else:
            return False

    def get_json_dump_exclude_list(self) -> dict:
        return {"form_element", "parent", "dependencies", "id", "required_choice"}

    def get_json_schema(self) -> dict:
        return self.model_dump(
            exclude=self.get_json_dump_exclude_list(), exclude_none=True
        )

    # def set_children(
    #     self, json_schema_generator: JsonSchemaGenerator, form: ObjectModel
    # ):
    #     pass  # only implemented in ObjectModel, ArrayModel, SelectionFieldModel
