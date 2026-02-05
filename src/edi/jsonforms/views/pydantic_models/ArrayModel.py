import logging

from typing import Optional

from edi.jsonforms.content.array import IArray
from edi.jsonforms.views.pydantic_models.BaseFormElementModel import (
    BaseFormElementModel,
)
from edi.jsonforms.views.pydantic_models.ObjectModel import ObjectModel


logger = logging.getLogger(__name__)


class ArrayModel(BaseFormElementModel):
    items: ObjectModel = None
    type: str = "array"
    minItems: Optional[int]

    def __init__(self, form_element: IArray, parent_model: BaseFormElementModel):
        super().__init__(form_element, parent_model)
        if self.required:
            self.minItems = 1

    def set_children(self, create_and_set_children_method: callable[ObjectModel]):
        """
        :param compute_children_method: creates instances of the children models and returns them as a dict (child_id: child_model)
        """
        object_model = ObjectModel(self.form_element, self.parent)
        object_model.set_children(create_and_set_children_method)
        self.items = object_model

    def get_json_schema(self) -> dict:
        # remove title from object from schema inside items
        return {}  # TODO
