from enum import Enum
import logging
from typing import Optional, List
from ZPublisher.HTTPRequest import WSGIRequest, HTTPRequest
from pydantic import BaseModel

from edi.jsonforms.content.upload_field import IUploadField

from edi.jsonforms.views.pydantic_models.BaseFormElementModel import (
    BaseFormElementModel,
)

logger = logging.getLogger(__name__)


class DataFormat(Enum):
    BASE64 = "Base64"
    URI = "URI"


class Upload(BaseModel):
    type: str = "string"
    format: Optional[str] = None
    contentEncoding: Optional[str] = None
    contentMediaType: Optional[List[str]] = None

    def __init__(
        self, data_format: DataFormat, accepted_file_types: Optional[List[str]] = None
    ):
        super().__init__()
        if data_format == DataFormat.BASE64:
            self.contentEncoding = "base64"
        elif data_format == DataFormat.URI:
            self.format = "uri"
        if accepted_file_types:
            self.contentMediaType = accepted_file_types

    def get_json_schema(self):
        return self.model_dump(exclude_none=True)


class UploadFieldModel(BaseFormElementModel):
    minItems: Optional[int] = None
    maxItems: Optional[int] = None
    format: Optional[str] = None
    items: Optional[Upload] = None
    data: Optional[Upload] = None
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

        upload = Upload(
            data_format=DataFormat(form_element.data_format),
            accepted_file_types=form_element.accepted_file_types,
        )
        if form_element.max_number_of_files:
            if form_element.max_number_of_files == 1:
                self.data = upload
            else:
                self.type = "array"
                self.items = upload
                self.maxItems = form_element.max_number_of_files
        else:
            self.type = "array"
            self.items = upload

        # self.maxSize = form_element.max_file_size
        # self.allowedTypes = form_element.accepted_file_types

    def get_json_schema(self):
        excluded_fields = self.get_json_dump_exclude_list().union({"data", "items"})
        json_schema = self.model_dump(exclude=excluded_fields, exclude_none=True)
        if self.data:
            json_schema.update(self.data.get_json_schema())
        elif self.items:
            json_schema["items"] = self.items.get_json_schema()
        return json_schema
