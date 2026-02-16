#### get default schemas


def get_child_ref_schema(type: str, title: str) -> dict:
    if type in ["radio", "checkbox", "select", "selectmultiple"]:
        return get_selectionfield_ref_schema(type, title)
    elif type in ["file", "file-multi"]:
        return get_uploadfield_ref_schema(type, title)
    elif type == "Array":
        return get_array_ref_schema(title)
    elif type == "Complex":
        return get_complex_ref_schema(title)
    else:
        return get_field_ref_schema(type, title)


def get_form_ref_schema(title="a form") -> dict:
    return get_object_ref_schema(title)


def get_complex_ref_schema(title="a complex object") -> dict:
    return get_object_ref_schema(title)


def get_object_ref_schema(title: str) -> dict:
    object_reference_schema = {
        "type": "object",
        "title": title,
        "properties": {},
        "required": [],
        "dependentRequired": {},
        "allOf": [],
    }
    return object_reference_schema


def get_field_ref_schema(type: str, title="a field") -> dict:
    field_reference_schemata = {
        "text": {"title": title, "type": "string"},
        "textarea": {"title": title, "type": "string"},
        "password": {"title": title, "type": "string"},
        "tel": {
            "title": title,
            "type": "string",
            "pattern": "^\\+?(\\d{1,3})?[-.\\s]?(\\(?\\d{1,4}\\)?)?[-.\\s]?\\d{1,4}[-.\\s]?\\d{1,4}[-.\\s]?\\d{1,9}$",
        },
        "url": {"title": title, "type": "string", "format": "hostname"},
        "email": {"title": title, "type": "string", "format": "email"},
        "date": {"title": title, "type": "string", "format": "date"},
        "datetime-local": {"title": title, "type": "string", "format": "date-time"},
        "time": {"title": title, "type": "string", "format": "time"},
        "number": {"title": title, "type": "number"},
        "integer": {"title": title, "type": "integer"},
        "boolean": {"title": title, "type": "boolean"},
    }
    return field_reference_schemata[type]


"""
options is a list of strings
"""


def get_selectionfield_ref_schema(
    type: str, title="a selectionfield", options=[]
) -> dict:
    selectionfield_reference_schemata = {
        "radio": {"title": title, "type": "string", "enum": []},
        "checkbox": {
            "title": title,
            "type": "array",
            "items": {"enum": [], "type": "string"},
        },
        "select": {"title": title, "type": "string", "enum": []},
        "selectmultiple": {
            "title": title,
            "type": "array",
            "items": {"enum": [], "type": "string"},
        },
    }
    selectionfield_reference_schemata = selectionfield_reference_schemata[type]
    if options != []:
        if "enum" in selectionfield_reference_schemata:
            selectionfield_reference_schemata["enum"] = options
        else:
            selectionfield_reference_schemata["items"]["enum"] = options
    return selectionfield_reference_schemata


def get_uploadfield_ref_schema(type: str, title="an uploadfield") -> dict:
    uploadfield_reference_schemata = {
        "file": {"title": title, "type": "string", "format": "uri"},
        "file-multi": {
            "title": title,
            "type": "array",
            "items": {"type": "string", "format": "uri"},
        },
    }
    return uploadfield_reference_schemata[type]


def get_array_ref_schema(title="an array") -> dict:
    array_reference_schema = {
        "type": "array",
        "title": title,
        "items": {
            "type": "object",
            "properties": {},
            "required": [],
            "dependentRequired": {},
            "allOf": [],
        },
    }
    return array_reference_schema


### ui schemas


def get_form_ref_schema_ui():
    schema = {
        "version": "2.0",
        "layout": {
            "type": "VerticalLayout",
            "elements": [
                {
                    "type": "Buttongroup",
                    "buttons": [
                        {
                            "type": "Button",
                            "buttonType": "submit",
                            "text": "Submit",
                            "options": {"variant": "primary"},
                        },
                        {
                            "type": "Button",
                            "buttonType": "reset",
                            "text": "Reset this form",
                            "options": {"variant": "danger"},
                        },
                    ],
                }
            ],
        },
    }
    return schema


def insert_into_elements(
    elements: dict, child_schema: list, has_buttons_element=True
) -> dict:
    # add child_schema to the elements before the buttons
    if has_buttons_element:
        elements.insert(-1, child_schema)
    else:
        elements.append(child_schema)
    return elements


"""
the title is only required if the type is "Fieldset"
"""


def get_child_ref_schema_ui(type: str, scope: str, title="") -> dict:
    if type in ["radio", "checkbox", "select", "selectmultiple"]:
        return get_selectionfield_ref_schema_ui(type, scope)
    elif type in ["file", "file-multi"]:
        return get_uploadfield_ref_schema_ui(type, scope)
    elif type == "Helptext":
        return get_helptext_ref_schema_ui(title)
    elif type == "Array":
        return get_array_ref_schema_ui(scope)
    elif type == "Complex":
        return get_complex_ref_schema_ui(scope)
    elif type == "Fieldset":
        return get_fieldset_ref_schema_ui(title, scope)
    else:
        return get_field_ref_schema_ui(type, scope)


def get_field_ref_schema_ui(type: str, scope: str) -> dict:
    schema = {"type": "Control", "scope": scope}
    field_reference_schemata_ui = {
        "text": {},
        "textarea": {"options": {"multi": True}},
        "password": {"options": {"format": "password"}},
        "tel": {"options": {"format": "tel"}},
        "url": {"options": {"format": "url"}},
        "email": {"options": {"format": "email"}},
        "date": {"options": {"format": "date"}},
        "datetime-local": {"options": {"format": "date-time"}},
        "time": {"options": {"format": "time"}},
        "number": {},
        "integer": {},
        "boolean": {},
    }

    schema.update(field_reference_schemata_ui[type])
    return schema


def get_selectionfield_ref_schema_ui(type: str, scope: str) -> dict:
    schema = {"type": "Control", "scope": scope}

    selectionfield_reference_schemata_ui = {
        "radio": {"options": {"displayAs": "radiobuttons", "stacked": True}},
        "checkbox": {"options": {"stacked": True}},
        "select": {},
        "selectmultiple": {"options": {"stacked": True}},
    }

    schema.update(selectionfield_reference_schemata_ui[type])
    return schema


def get_uploadfield_ref_schema_ui(type: str, scope: str) -> dict:
    schema = {"type": "Control", "scope": scope}

    uploadfield_reference_schemata = {
        "file": {"options": {"acceptedFileType": "*"}},
        "file-multi": {
            "options": {"acceptedFileType": "*", "allowMultipleFiles": True}
        },
    }
    schema.update(uploadfield_reference_schemata[type])
    return schema


def get_helptext_ref_schema_ui(text: str) -> dict:
    schema = {"type": "HTML", "htmlData": text}
    return schema


def get_array_ref_schema_ui(scope: str) -> dict:
    schema = {
        "type": "Control",
        "scope": scope,
        "options": {"descendantControlOverrides": {}},
    }
    return schema


def get_complex_ref_schema_ui(scope: str) -> dict:
    schema = {
        "type": "Control",
        "scope": scope,
        "options": {"descendantControlOverrides": {}},
    }
    return schema


def get_fieldset_ref_schema_ui(title: str) -> dict:
    schema = {"type": "Group", "options": {"label": title}, "elements": []}
    return schema


"""
descendantControlOverrides: needs key "descendantControlOverrides": {...}
"""


def insert_schema_into_descConOv(
    descendantControlOverrides: dict, child_schema: dict, scope: str
):
    controlOverrides = {}
    if "options" in child_schema:
        controlOverrides["options"] = child_schema["options"]
    if "showOn" in child_schema:
        controlOverrides["showOn"] = child_schema["showOn"]

    if controlOverrides != {}:
        descendantControlOverrides["options"]["descendantControlOverrides"][scope] = (
            controlOverrides
        )
