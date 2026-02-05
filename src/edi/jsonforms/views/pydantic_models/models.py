import logging

from edi.jsonforms.views.pydantic_models.BaseFormElementModel import (
    BaseFormElementModel,
)

logger = logging.getLogger(__name__)


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
