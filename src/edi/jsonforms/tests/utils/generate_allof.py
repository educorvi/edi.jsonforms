from typing import Optional
from edi.jsonforms.content.common import IFormElement
from edi.jsonforms.content.option import IOption
from edi.jsonforms.views.common import string_type_fields
from edi.jsonforms.views.common import create_id


def get_if_schema(
    form_element: IFormElement, independent_option_value: Optional[IOption] = None
) -> dict:
    """
    helper function to get the if-schema of an independent child
    """
    logic = {}
    if form_element.portal_type == "Field":
        if form_element.answer_type in string_type_fields:
            logic = {"minLength": 1}
        elif form_element.answer_type == "boolean":
            logic = {"const": True}
        else:  # number or integer
            pass
    elif form_element.portal_type == "SelectionField":
        if form_element.answer_type == "checkbox":
            logic = {"contains": {"const": independent_option_value.title}}
        elif form_element.answer_type == "radio":
            logic = {"const": independent_option_value.title}

    schema = {}
    if logic:
        schema["properties"] = {create_id(form_element): logic}
    schema["required"] = [create_id(form_element)]
    return schema


def get_then_schema(dependent_form_element: IFormElement) -> dict:
    """
    helper function to get the if-schema of an independent child
    """
    logic = {}
    if dependent_form_element.portal_type == "Field":
        if dependent_form_element.answer_type in string_type_fields:
            logic = {"minLength": 1}
        elif dependent_form_element.answer_type == "boolean":
            logic = {"const": True}
        else:  # number or integer
            pass
    elif dependent_form_element.portal_type == "SelectionField":
        if dependent_form_element.answer_type == "checkbox":
            logic = {"minItems": 1}
        elif dependent_form_element.answer_type == "radio":
            logic = {}

    schema = {}
    if logic:
        schema["properties"] = {create_id(dependent_form_element): logic}
    schema["required"] = [create_id(dependent_form_element)]
    return schema


def get_if_then_schema(
    independent_child: IFormElement,
    dependent_child: IFormElement,
    independent_option_value: Optional[IOption] = None,
) -> dict:
    """
    helper function to get the if-schema of an independent child
    """
    schema = {
        "if": get_if_schema(independent_child, independent_option_value),
        "then": get_then_schema(dependent_child),
    }
    return schema
