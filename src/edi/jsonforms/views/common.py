from edi.jsonforms.content.common import IFormElement
from edi.jsonforms.content.option import IOption
from urllib.parse import quote_plus

import re


try:
    from edi.jsonforms_override.behaviors.interfaces import get_override_fork
    from edi.jsonforms_override.behaviors.interfaces import get_override_value
except ModuleNotFoundError:
    # if the import fails, define dummy functions that return empty strings, so that
    #     the code doesn't break and the override fields just don't work
    def get_override_fork(attribute: str):
        return ""

    def get_override_value(attribute: str):
        return ""


possibly_required_types = ["Field", "SelectionField", "UploadField", "Array"]

# for Field
string_type_fields = [
    "text",
    "textarea",
    "password",
    "tel",
    "url",
    "email",
    "date",
    "datetime-local",
    "time",
]

# for SelectionField
single_answer_types = ["radio", "select"]

container_types = ["Array", "Fieldset", "Complex"]


def create_id(obj):
    id_str = str(obj.id)
    return id_str


def create_unique_id(obj):
    id_str = str(obj.id) + str(obj.UID())
    escaped_id_str = id_str.replace(".", "").replace("/", "")
    return escaped_id_str


def get_option_name(option: IOption) -> str:
    if option.aq_parent.use_id_in_schema:
        return option.id
    else:
        return option.title


def get_view_url(obj):
    return obj.absolute_url()


def get_edit_url(obj):
    return obj.absolute_url() + "/edit"


def get_content_url(obj):
    if has_content(obj):
        return obj.absolute_url() + "/folder_contents"
    else:
        return get_view_url(obj)


def get_delete_url(obj):
    return obj.absolute_url() + "/delete_confirmation"


def has_content(obj):
    return obj.portal_type in [
        "Array",
        "SelectionField",
        "Button Group",
        "Fieldset",
        "Complex",
    ]


def get_fork(request):
    fork = request.get("fork", "")
    return fork


def get_value(overwritten_attribute, attribute, request):
    new_attribute = ""
    fork = get_fork(request)
    if fork and fork != "":
        for item in overwritten_attribute:
            if get_override_fork(item) == fork:
                new_attribute = get_override_value(item)

    if new_attribute:
        return new_attribute
    return attribute


def get_title(obj, request):
    title = obj.title
    # if object has the attribute override_title, use it instead of the title
    if hasattr(obj, "override_title") and obj.override_title:
        title = get_value(obj.override_title, title, request)
    return title


def get_description(obj, request):
    description = obj.description
    # if object has the attribute override_description, use it instead of
    #     the description
    if hasattr(obj, "override_description") and obj.override_description:
        description = get_value(obj.override_description, description, request)
    return description


# TODO use as soon as helptext is included in the schema
def get_user_helptext(obj, request):
    user_helptext = getattr(obj, "user_helptext", "")
    # if object has the attribute override_user_helptext, use it instead of
    #     the user_helptext
    if hasattr(obj, "override_user_helptext") and obj.override_user_helptext:
        user_helptext = get_value(obj.override_user_helptext, user_helptext, request)
    return user_helptext


def get_unit(obj, request):
    unit = obj.unit
    # if object has the attribute override_unit, use it instead of the unit
    if hasattr(obj, "override_unit") and obj.override_unit:
        unit = get_value(obj.override_unit, unit, request)
    return unit


def get_placeholder(obj, request):
    placeholder = obj.placeholder
    # if object has the attribute override_placeholder, use it instead of
    #     the placeholder
    if hasattr(obj, "override_placeholder") and obj.override_placeholder:
        placeholder = get_value(obj.override_placeholder, placeholder, request)
    return placeholder


# def create_id(object_id, object_uid):
#     return str(object_id) + str(object_uid)


def check_show_condition_in_request(request, show_condition, negate_condition=False):
    """Check if the show condition is met in the request."""
    # if no show_condition is set, show the field
    if not show_condition or show_condition == "":
        return True

    # if show_condition only contains spaces or commas it is also considered as
    #     empty so show the field
    conditions = re.split(r",\s*", show_condition)
    conditions = [quote_plus(c) for c in conditions if c and c.strip() != ""]
    if len(conditions) == 0:
        return True

    fork = get_fork(request)

    # if no fork is set but a show_condition is set without negation, don't
    #     show the field
    if not fork and fork != "":
        return negate_condition

    # fork and condition are set:
    if not negate_condition:
        return fork in conditions
    else:
        return fork not in conditions


def get_path(obj: IFormElement, without_root=False):
    """
    get the path of an object in the json schema (leaves out fieldsets)
    e.g. /properties/object1/properties/selectionfield1/properties/option1
    """
    path = create_id(obj)
    while obj.aq_parent.portal_type != "Form":
        obj = obj.aq_parent
        if obj.portal_type == "Array":
            path = create_id(obj) + "/items/properties/" + path
        elif obj.portal_type != "Fieldset":
            path = create_id(obj) + "/properties/" + path
    return "/properties/" + path
