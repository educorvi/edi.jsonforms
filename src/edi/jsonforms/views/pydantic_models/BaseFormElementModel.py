import abc
import copy
import logging

from edi.jsonforms.views.pydantic_models.dependency_handler import (
    check_for_dependencies,
)
from plone.base.utils import safe_hasattr
from typing import Optional, List

from edi.jsonforms.content.common import IFormElement

from edi.jsonforms.views.common import (
    get_title,
    get_description,
    create_id,
)
from edi.jsonforms.views.pydantic_models.schema_generator import (
    JsonSchemaGenerator,
)

logger = logging.getLogger(__name__)


class BaseFormElementModel(abc.ABC):
    form_element: IFormElement
    id: str
    title: str
    description: Optional[str]
    comment: Optional[str]
    type: Optional[str]
    parent: "BaseFormElementModel"  # actually it can only be an ObjectModel or a model that extends this (Form)
    required: Optional[bool] = False
    dependencies: Optional[List[IFormElement]] = []

    def __init__(
        self, form_element: IFormElement, parent_model: "BaseFormElementModel"
    ):
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
        self.dependencies = copy.copy(form_element.dependencies)

    def get_id(self) -> str:
        return self.id

    def get_dependencies(self) -> List[IFormElement]:
        return self.dependencies

    def extend_dependencies(self, dependencies: List[IFormElement]):
        self.dependencies.extend(dependencies)

    def check_dependencies(self, is_single_view: bool) -> bool:
        check_for_dependencies(self, is_single_view)

    def set_children(self, json_schema_generator: JsonSchemaGenerator):
        pass  # only implemented in ObjectModel, ArrayModel, SelectionFieldModel
