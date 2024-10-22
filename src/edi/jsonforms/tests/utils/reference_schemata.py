


#### get default schemas

def get_child_ref_schema(type, title):
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

def get_form_ref_schema(title="a form"):
    return get_object_ref_schema(title)

def get_complex_ref_schema(title="a complex object"):
    return get_object_ref_schema(title)

def get_object_ref_schema(title):
    object_reference_schema = {
        "type": "object",
        "title": title,
        "properties": {},
        "required": [],
        "dependentRequired": {},
        "allOf": []
    }
    return object_reference_schema

def get_field_ref_schema(type, title="a field"):
    field_reference_schemata = {
        "text": {"title": title, "type": "string"},
        "textarea": {"title": title, "type": "string"},
        "password": {"title": title, "type": "string"},
        "tel": {"title": title, "type": "string", "pattern": "^\\+?(\\d{1,3})?[-.\\s]?(\\(?\\d{1,4}\\)?)?[-.\\s]?\\d{1,4}[-.\\s]?\\d{1,4}[-.\\s]?\\d{1,9}$"},
        "url": {"title": title, "type": "string", "format": "hostname"},
        "email": {"title": title, "type": "string", "format": "email"},
        "date": {"title": title, "type": "string", "format": "date"},
        "datetime-local": {"title":title, "type": "string", "format": "date-time"},
        "time": {"title": title, "type": "string", "format": "time"},
        "number": {"title": title, "type": "number"},
        "integer": {"title": title, "type": "integer"},
        "boolean": {"title": title, "type": "boolean"}
    }
    return field_reference_schemata[type]

def get_selectionfield_ref_schema(type, title="a selectionfield", options=[]):
    selectionfield_reference_schemata = {
        "radio": {"title": title, "type": "string", "enum": []},
        "checkbox": {"title": title, "type": "array", "items": {"enum": [], "type": "string"}},
        "select": {"title": title, "type": "string", "enum": []},
        "selectmultiple": {"title": title, "type": "array", "items": {"enum": [], "type": "string"}}
    }
    if options != []:
        if "enum" in selectionfield_reference_schemata:
            selectionfield_reference_schemata['enum'] = options
        else:
            selectionfield_reference_schemata['items']['enum'] = options
    return selectionfield_reference_schemata[type]

def get_uploadfield_ref_schema(type, title="an uploadfield"):
    uploadfield_reference_schemata = {
        "file": {"title": title, "type": "string", "format": "uri"},
        "file-multi": {"title": title, "type": "array", "items": {"type": "string", "format": "uri"}}
    }
    return uploadfield_reference_schemata[type]

def get_array_ref_schema(title="an array"):
    array_reference_schema = {
        "type": "array",
        "title": title,
        "items": {
            "type": "object",
            "properties": {},
            "required": [],
            "dependentRequired": {},
            "allOf": []
        }
    }
    return array_reference_schema

