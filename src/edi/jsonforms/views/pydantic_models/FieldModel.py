import logging
from typing import Optional
from ZPublisher.HTTPRequest import WSGIRequest

from edi.jsonforms.content.field import IField
from edi.jsonforms.views.common import string_type_fields
from edi.jsonforms.views.pydantic_models.BaseFormElementModel import (
    BaseFormElementModel,
)

logger = logging.getLogger(__name__)


class FieldModel(BaseFormElementModel):
    minLength: Optional[int] = None
    maxLength: Optional[int] = None
    pattern: Optional[str] = None
    format: Optional[str] = None
    minimum: Optional[float] = None
    maximum: Optional[float] = None

    def __init__(
        self,
        form_element: IField,
        parent_model: BaseFormElementModel,
        request: WSGIRequest,
    ):
        super().__init__(form_element, parent_model, request)
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

        if (
            not self.minLength
            and self.is_required
            and answer_type in string_type_fields
        ):
            self.minLength = 1

    def get_json_schema(self) -> dict:
        return super().get_json_schema()
