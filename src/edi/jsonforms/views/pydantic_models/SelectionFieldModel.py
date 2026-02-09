import logging
from ZPublisher.HTTPRequest import WSGIRequest

from edi.jsonforms.views.pydantic_models.dependency_handler import (
    add_dependent_options,
)
from plone.base.utils import safe_hasattr
from pydantic import BaseModel
from typing import Optional, List, Dict

from edi.jsonforms.content.selection_field import ISelectionField
from edi.jsonforms.content.option import IOption
from edi.jsonforms.content.option_list import (
    OptionList,
    get_keys_and_values_for_options_list,
)
from edi.jsonforms.views.common import (
    get_title,
    create_id,
    check_show_condition_in_request,
)
from edi.jsonforms.views.pydantic_models.BaseFormElementModel import (
    BaseFormElementModel,
)
from edi.jsonforms.views.pydantic_models.GeneratorArguments import GeneratorArguments

logger = logging.getLogger(__name__)


class OptionModel(BaseModel):
    id: str
    title: str
    parent: ISelectionField
    dependencies: Optional[List[IOption]] = []

    class Config:
        arbitrary_types_allowed = True

    def __init__(self, id: str, title: str, parent: ISelectionField):
        self.id = id
        self.title = title
        self.parent = parent

    @classmethod
    def from_option(cls, option: IOption):
        return cls(
            id=create_id(option),
            title=get_title(option),
            parent=option.aq_parent,
        )

    @classmethod
    def from_id_and_title(cls, id: str, title: str, parent: ISelectionField):
        return cls(id=id, title=title, parent=parent)

    # a get method for name (title or id)
    def get_option_name(self) -> str:
        if self.parent.use_id_in_schema:
            return self.id
        else:
            return self.title

    def check_dependencies(self, is_single_view: bool) -> bool:
        # return check_for_dependencies(self, is_single_view)
        if is_single_view:  # if form-element-view, ignore all dependencies
            return False
        if self.dependencies:
            return True
        else:
            return False


class OptionListModel(BaseModel):
    options: List[OptionModel]

    def __init__(self, option_list: OptionList):
        o_keys, o_values = get_keys_and_values_for_options_list(option_list)
        self.options = []
        for key, value in zip(o_keys, o_values):
            option_model = OptionModel.from_id_and_title(
                key, value, option_list.aq_parent
            )
            self.options.append(option_model)

    def get_option_names(self) -> List[str]:
        return [option.get_option_name() for option in self.options]


class SelectionFieldModel(BaseFormElementModel):
    enum: Optional[List[str]]
    items: Optional[Dict[str, List[str] | str]]

    def __init__(
        self,
        form_element: ISelectionField,
        parent_model: BaseFormElementModel,
        request: WSGIRequest,
    ):
        super().__init__(form_element, parent_model, request)

        answer_type = form_element.answer_type

        if answer_type == "radio" or answer_type == "select":
            self.type = "string"
            # self.enum = options_list
        elif answer_type == "checkbox" or answer_type == "selectmultiple":
            self.type = "array"
            # self.items = {"enum": options_list, "type": "string"}

    def get_options(self, generatorArguments: GeneratorArguments):
        """
        sets options to self.form_element.getFolderContents()

        :param ignore_conditions: can be i.e. is_single_view, to get all options regardless of conditions and dependencies
        """
        options = self.form_element.getFolderContents()

        options_list = []
        for o in options:
            o.getObject()
            if o.portal_type == "Option":
                if generatorArguments.ignore_conditions:
                    option_model = OptionModel.from_option(o)
                    options_list.append(option_model.get_option_name())
                else:
                    show = True
                    if safe_hasattr(o, "show_condition") and o.show_condition:
                        negate_condition = getattr(o, "negate_condition", False)
                        show = check_show_condition_in_request(
                            generatorArguments.request,
                            o.show_condition,
                            negate_condition,
                        )
                    option_model = OptionModel.from_option(o)
                    if show and not option_model.check_dependencies(
                        generatorArguments.is_single_view
                    ):
                        options_list.append(option_model.get_option_name())
            elif o.portal_type == "OptionList":
                keys, vals = get_keys_and_values_for_options_list(o)
                if self.form_element.use_id_in_schema:
                    options_list.extend(keys)
                else:
                    options_list.extend(vals)
        return options_list

    def set_children(self, generatorArguments: GeneratorArguments):
        options_list = self.get_options(generatorArguments)

        if self.type == "string":
            self.enum = options_list
        elif self.type == "array":
            self.items = {"enum": options_list, "type": "string"}

        # adds the allOf of the dependent options to the form
        add_dependent_options(
            self.form_element,
            generatorArguments.is_single_view,
            generatorArguments.formProperties,
        )
        # schema["allOf"].extend(self.get_dependent_options(child_object))
