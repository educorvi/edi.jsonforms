from edi.jsonforms.content.option import IOption
from edi.jsonforms.content.option_list import get_keys_and_values_for_options_list
from edi.jsonforms.content.option_list import OptionList
from edi.jsonforms.content.selection_field import ISelectionField
from edi.jsonforms.views.common import check_show_condition_in_request
from edi.jsonforms.views.common import create_id
from edi.jsonforms.views.common import single_answer_types
from edi.jsonforms.views.pydantic_models.BaseFormElementModel import (
    BaseFormElementModel,
)
from edi.jsonforms.views.pydantic_models.dependency_handler import add_dependent_options
from edi.jsonforms.views.pydantic_models.dependency_handler import (
    check_for_dependencies,
)
from edi.jsonforms.views.pydantic_models.GeneratorArguments import GeneratorArguments
from plone.base.utils import safe_hasattr
from pydantic import BaseModel
from pydantic import Field
from ZPublisher.HTTPRequest import HTTPRequest
from ZPublisher.HTTPRequest import WSGIRequest

import logging


logger = logging.getLogger(__name__)


class OptionModel(BaseModel):
    option_id: str
    option_title: str
    parent: ISelectionField
    dependencies: list[IOption] | None = Field(default_factory=list)

    class Config:
        arbitrary_types_allowed = True

    def __init__(self, option_id: str, option_title: str, parent: ISelectionField):
        """
        constructor for OptionModel, sets id, title and parent of the option
        dependencies stay empty
        """
        super().__init__(option_id=option_id, option_title=option_title, parent=parent)

    @classmethod
    def from_option(cls, option: IOption):
        option_model = cls(
            option_id=create_id(option),
            option_title=option.title,
            parent=option.aq_parent,
        )
        if safe_hasattr(option, "dependencies"):
            option_model.dependencies = option.dependencies
        return option_model

    @classmethod
    def from_id_and_title(
        cls, option_id: str, option_title: str, parent: ISelectionField
    ):
        """
        constructor for OptionModel, sets id, title and parent of the option
        dependencies stay empty
        """
        return cls(option_id=option_id, option_title=option_title, parent=parent)

    # a get method for name (title or id)
    def get_option_name(self) -> str:
        if self.parent.use_id_in_schema:
            return self.option_id
        else:
            return self.option_title

    def check_dependencies(self, is_single_view: bool) -> bool:
        return check_for_dependencies(self, is_single_view)
        # if is_single_view:  # if form-element-view, ignore all dependencies
        #     return False
        # if self.dependencies:
        #     return True
        # else:
        #     return False


class OptionListModel(BaseModel):
    options: list[OptionModel]

    def __init__(self, option_list: OptionList):
        super().__init__(options=[])
        o_keys, o_values = get_keys_and_values_for_options_list(option_list)
        for key, value in zip(o_keys, o_values, strict=False):
            option_model = OptionModel.from_id_and_title(
                key, value, option_list.aq_parent
            )
            self.options.append(option_model)

    def get_option_names(self) -> list[str]:
        return [option.get_option_name() for option in self.options]


class SelectionFieldModel(BaseFormElementModel):
    enum: list[str] | None = None
    items: dict[str, list[str] | str] | None = None
    minItems: int | None = None

    def __init__(
        self,
        form_element: ISelectionField,
        parent_model: BaseFormElementModel,
        request: WSGIRequest | HTTPRequest,
    ):
        super().__init__(form_element, parent_model, request)

        answer_type = form_element.answer_type

        if answer_type in single_answer_types:
            self.type = "string"
            self.enum = []
        elif answer_type not in single_answer_types:
            # elif answer_type == "checkbox" or answer_type == "selectmultiple":
            self.type = "array"
            if self.is_required:
                self.minItems = 1
            self.items = {"enum": [], "type": "string"}

    def get_options(self, generatorArguments: GeneratorArguments) -> list[str]:
        """
        gets options as strings of
            self.form_element.restrictedTraverse("@@contentlisting")()
        includes dependencies in the computation

        :param generatorArguments: can be i.e. is_single_view, to get all options
            regardless of conditions and dependencies
        """
        options = self.form_element.restrictedTraverse("@@contentlisting")()

        options_list = []
        for o in options:
            o = o.getObject()

            # compute if should be shown
            if generatorArguments.is_single_view:
                show = True
            else:
                show = True
                if safe_hasattr(o, "show_condition") and o.show_condition:
                    negate_condition = getattr(o, "negate_condition", False)
                    show = check_show_condition_in_request(
                        generatorArguments.request,
                        o.show_condition,
                        negate_condition,
                    )

            if o.portal_type == "Option":
                if show:
                    option_model = OptionModel.from_option(o)
                    if not option_model.check_dependencies(
                        generatorArguments.is_single_view
                    ):
                        options_list.append(option_model.get_option_name())
            elif o.portal_type == "OptionList" and show:
                keys, vals = get_keys_and_values_for_options_list(o)
                if self.form_element.use_id_in_schema:
                    options_list.extend(keys)
                else:
                    options_list.extend(vals)
        return options_list

    def set_option(self, option_model: OptionModel | OptionListModel):
        """
        sets the option for the selectionfield
        ignores dependencies of the options
        :param option_model: OptionModel or OptionListModel to set
        """
        if isinstance(option_model, OptionModel):
            option_name = option_model.get_option_name()

            if self.type == "string":
                self.enum.append(option_name)
            elif self.type == "array" and self.items and "enum" in self.items:
                self.items["enum"].append(option_name)
        elif isinstance(option_model, OptionListModel):
            for option in option_model.options:
                self.set_option(option)

    def unset_options(self):
        """
        removes all options from the selectionfield
        """
        if self.type == "string":
            self.enum = []
        elif self.type == "array" and self.items and "enum" in self.items:
            self.items["enum"] = []

    def set_children(self, generatorArguments: GeneratorArguments):
        """
        sets the options for the selectionfield and adds the allOf of the dependent
            options to the form

        :param generatorArguments: needed to get is_single_view (ignore dependencies)
            and formProperties (to add dependent options to the formModel later)
        """
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

    def get_json_schema(self):
        return super().get_json_schema()
