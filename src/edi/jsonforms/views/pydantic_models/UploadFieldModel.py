import logging
from typing import Optional, List
from ZPublisher.HTTPRequest import WSGIRequest, HTTPRequest

from edi.jsonforms.content.upload_field import IUploadField

from edi.jsonforms.views.pydantic_models.BaseFormElementModel import (
    BaseFormElementModel,
)

logger = logging.getLogger(__name__)


class UploadFieldModel(BaseFormElementModel):
    minItems: Optional[int] = None
    maxItems: Optional[int] = None
    format: Optional[str] = None
    items: Optional[dict] = None
    # maxSize: Optional[int] = None
    # allowedTypes: Optional[List[str]] = None

    def __init__(
        self,
        form_element: IUploadField,
        parent_model: BaseFormElementModel,
        request: WSGIRequest | HTTPRequest,
    ):
        super().__init__(form_element, parent_model, request)
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

        # self.maxSize = form_element.max_file_size
        # self.allowedTypes = form_element.accepted_file_types

    def get_json_schema(self):
        return super().get_json_schema()
