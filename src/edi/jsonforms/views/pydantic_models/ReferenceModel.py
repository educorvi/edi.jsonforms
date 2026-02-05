from edi.jsonforms.content.reference import IReference

from edi.jsonforms.views.pydantic_models.BaseFormElementModel import (
    BaseFormElementModel,
)


class ReferenceModel(BaseFormElementModel):
    targetType: str
    target: BaseFormElementModel

    def __init__(self, form_element: IReference, parent_model: BaseFormElementModel):
        super().__init__(form_element, parent_model)
        self.targetType = form_element.target_type

    # method to get json schema, overwrites standard method
    def get_json_schema(self) -> dict:
        pass
        # try:
        #     obj = reference.reference.to_object
        #     if obj:
        #         obj_schema = self.get_schema_for_child(obj)
        #         return obj_schema
        # except:  # referenced object got deleted, ignore
        #     return {}
