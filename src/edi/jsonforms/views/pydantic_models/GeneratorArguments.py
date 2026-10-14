from edi.jsonforms.content.reference import IReference
from edi.jsonforms.views.pydantic_models.FormProperties import FormProperties
from pydantic import BaseModel
from ZPublisher.HTTPRequest import HTTPRequest
from ZPublisher.HTTPRequest import WSGIRequest

import logging


logger = logging.getLogger(__name__)


class GeneratorArguments(BaseModel):
    request: WSGIRequest | HTTPRequest
    is_single_view: bool
    is_extended_schema: bool
    formProperties: FormProperties
    reference: IReference | None = (
        None  # to check if current child is somewhere nested in a referenced object
    )

    class Config:
        arbitrary_types_allowed = True

    def __init__(
        self,
        request: WSGIRequest | HTTPRequest,
        is_single_view: bool,
        is_extended_schema: bool = False,
        reference: IReference | None = None,
    ):
        super().__init__(
            request=request,
            is_single_view=is_single_view,
            is_extended_schema=is_extended_schema,
            formProperties=FormProperties(),
            reference=reference,
        )
