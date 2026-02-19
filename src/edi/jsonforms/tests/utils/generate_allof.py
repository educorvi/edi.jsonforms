from typing import Optional
from edi.jsonforms.content.common import IFormElement
from edi.jsonforms.content.option import IOption
from edi.jsonforms.views.common import string_type_fields
from edi.jsonforms.views.common import create_id


def get_if_schema(
    form_element: IFormElement,
    independent_option_value: Optional[IOption] = None,
) -> dict:
    """
    helper function to get the if-schema of an independent child
    """
    id = create_id(form_element)
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
    elif (
        form_element.portal_type
        in [
            "UploadField",
            "Array",
        ]
    ):  # TODO not tested at the moment, because not supported by the form builder in plone.
        # only dependencies to fields and options are valid
        logic = {"minItems": 1}

    schema = {}
    if logic:
        schema["properties"] = {id: logic}
    schema["required"] = [id]
    return schema


def get_then_schema(dependent_form_element: IFormElement) -> dict:
    """
    helper function to get the if-schema of an independent child
    """
    id = create_id(dependent_form_element)
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
    elif dependent_form_element.portal_type in ["UploadField", "Array"]:
        logic = {"minItems": 1}

    schema = {}
    if logic:
        schema["properties"] = {id: logic}
    schema["required"] = [id]
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


def make_if_then_schema_nested(
    ref_schema: dict,
    parent_id: str,
    is_array: bool = False,
    index: int = 0,
    if_schema_nested: bool = False,
) -> dict:
    """
    helper function to nest a then schema into the properties (or items) of a parent object in the ref_schema
    the ref_schema needs to have an allOf, the element on the specified index is then made nested

    if also the if_schema needs to be nested, if_schema_nested must be set to True
    """
    if is_array:
        ref_schema["allOf"][index]["then"] = {
            "properties": {parent_id: {"items": ref_schema["allOf"][index]["then"]}},
            "required": [parent_id],
        }
    else:
        ref_schema["allOf"][index]["then"] = {
            "properties": {parent_id: ref_schema["allOf"][index]["then"]},
            "required": [parent_id],
        }

    if if_schema_nested:
        if is_array:
            ref_schema["allOf"][index]["if"] = {
                "properties": {parent_id: {"items": ref_schema["allOf"][index]["if"]}},
                "required": [parent_id],
            }
        else:
            ref_schema["allOf"][index]["if"] = {
                "properties": {parent_id: ref_schema["allOf"][index]["if"]},
                "required": [parent_id],
            }
    return ref_schema
