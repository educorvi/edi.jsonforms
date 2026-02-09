# from edi.jsonforms.views.pydantic_models.ObjectModel import ObjectModel
# from edi.jsonforms.views.pydantic_models.BaseFormElementModel import (
#     BaseFormElementModel,
# )
# from edi.jsonforms.content.form import IForm
# from edi.jsonforms.views.pydantic_models.schema_generator import JsonSchemaGenerator


# class FormModel(ObjectModel):
#     def __init__(self, form_element: IForm, parent_model: BaseFormElementModel = None):
#         super().__init__(form_element, parent_model)

#     def set_children(
#         self, json_schema_generator: JsonSchemaGenerator, form: "FormModel" = None
#     ):
#         super().set_children(json_schema_generator, self)

#     def get_json_schema(self) -> dict:
#         # TODO
#         return super().get_json_schema()
pass
