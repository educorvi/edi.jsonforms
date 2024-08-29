

def get_field_reference_schema(type, title="a field"):
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

def get_selectionfield_reference_schema(type, title="a selectionfield"):
    selectionfield_reference_schemata = {
        "radio": {"title": title, "type": "string", "enum": []},
        "checkbox": {"title": title, "type": "array", "items": {"enum": [], "type": "string"}},
        "select": {"title": title, "type": "string", "enum": []},
        "selectmultiple": {"title": title, "type": "array", "items": {"enum": [], "type": "string"}}
    }
    return selectionfield_reference_schemata[type]

def get_uploadfield_reference_schema(type, title="an uploadfield"):
    uploadfield_reference_schemata = {
        "file": {"title": title, "type": "string", "format": "uri"},
        "file-multi": {"title": title, "type": "array", "items": {"type": "string", "format": "uri"}}
    }
    return uploadfield_reference_schemata[type]


