import logging
from typing import Optional, List

from edi.jsonforms.content.upload_field import IUploadField

from edi.jsonforms.views.pydantic_models.BaseFormElementModel import (
    BaseFormElementModel,
)

logger = logging.getLogger(__name__)


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
