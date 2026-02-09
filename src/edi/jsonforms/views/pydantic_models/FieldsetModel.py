# from edi.jsonforms.content.fieldset import IFieldset
# from edi.jsonforms.views.pydantic_models.ObjectModel import ObjectModel
# from edi.jsonforms.views.pydantic_models.GeneratorArguments import GeneratorArguments


# class FieldsetModel(ObjectModel):
#     """
#     This class is different from the other BaseFormElementModel-classes. It does not store any information, but the init method creates the children and stores them in the parent_model
#     """

#     def __init__(self, form_element: IFieldset, parent_model: ObjectModel):
#         super().__init__(form_element, parent_model)

#     def set_children(self, generatorArguments: GeneratorArguments):
#         super().set_children(generatorArguments)
#         self.parent.update_properties(self.properties)
#         self.parent.update_required(self.required)
#         self.parent.extend_dependencies(self.dependencies)
#         self.parent.update_dependentRequired(self.dependentRequired)

#     def get_json_schema(self) -> dict:
#         return {}  # Fieldset does not contribute to the json schema
