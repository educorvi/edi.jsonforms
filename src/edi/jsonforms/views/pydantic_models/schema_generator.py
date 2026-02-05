import logging
from pydantic import BaseModel


logger = logging.getLogger(__name__)


class JsonSchemaGenerator(BaseModel):
    request: any
    is_single_view: bool
    is_extended_schema: bool
    form: "FormModel"

    def __init__(
        self,
        form: "FormModel",
        request,
        is_single_view: bool,
        is_extended_schema: bool = False,
    ):
        self.form = form
        self.request = request
        self.is_single_view = is_single_view
        self.is_extended_schema = is_extended_schema

    def generate_json_schema(self) -> dict:
        return self.form.get_json_schema()
