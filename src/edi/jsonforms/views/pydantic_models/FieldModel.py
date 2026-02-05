import logging
from typing import Optional
from edi.jsonforms.content.field import IField
from edi.jsonforms.views.pydantic_models.BaseFormElementModel import (
    BaseFormElementModel,
)

logger = logging.getLogger(__name__)


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
