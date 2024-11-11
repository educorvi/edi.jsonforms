# -*- coding: utf-8 -*-

from edi.jsonforms import _
from Products.Five.browser import BrowserView

import copy
import json

from edi.jsonforms.views.common import possibly_required_types, create_id

def check_for_dependencies(child_object):
    if child_object.dependencies is not None and child_object.dependencies != []:
        return True
    else:
        return False

class JsonSchemaView(BrowserView):

    def __init__(self, context, request):
        super().__init__(context, request)
        self.jsonschema = {}

    def __call__(self):
        self.jsonschema = {}
        form = self.context
        self.jsonschema['type'] = 'object'
        self.jsonschema = add_title_and_description(self.jsonschema, form)

        children = form.getFolderContents()
        self.jsonschema['properties'] = {}
        self.jsonschema['required'] = []
        self.jsonschema['dependentRequired'] = {}
        self.jsonschema['allOf'] = []
        for child in children:
            child_object = child.getObject()
            child_id = create_id(child_object)

            # add children to the schema
            if child_object.portal_type == 'Fieldset':
                self.jsonschema = self.modify_schema_for_fieldset(self.jsonschema, child_object)
            else:
                self.jsonschema['properties'][child_id] = self.get_schema_for_child(child_object)

            # mark children as required
            if child_object.portal_type in possibly_required_types and child_object.required_choice == 'required':
                if check_for_dependencies(child_object):
                    self.jsonschema = add_dependent_required(self.jsonschema, child_object, child_id)
                else:
                    self.jsonschema['required'].append(child_id)

        return json.dumps(self.jsonschema)

    def modify_schema_for_fieldset(self, schema, fieldset):
        children = fieldset.getFolderContents()
        for child in children:
            child_object = child.getObject()
            child_id = create_id(child_object)
            if child_object.portal_type == 'Fieldset':
                schema = self.modify_schema_for_fieldset(schema, child_object)
            else:
                schema['properties'][child_id] = self.get_schema_for_child(child_object)
                if child_object.portal_type in possibly_required_types and child_object.required_choice == 'required':
                    if check_for_dependencies(child_object):
                        schema = add_dependent_required(schema, child_object, child_id)
                    else:
                        schema['required'].append(child_id)
        return schema

    def get_schema_for_child(self, child):
        type = child.portal_type

        if type == 'Field':
            return self.get_schema_for_field(child)
        elif type == 'SelectionField':
            return self.get_schema_for_selectionfield(child)
        elif type == 'UploadField':
            return self.get_schema_for_uploadfield(child)
        elif type == 'Array':
            return self.get_schema_for_array(child)
        elif type == 'Complex':
            return self.get_schema_for_object(child)
        return {}

    def get_schema_for_field(self, field):
        field_schema = create_base_schema__field({}, field)
        answer_type = field.answer_type
        if answer_type in ['text', 'textarea', 'password']:
            field_schema['type'] = 'string'
            if field.minimum:
                field_schema['minLength'] = field.minimum
            if field.maximum:
                field_schema['maxLength'] = field.maximum
        elif answer_type == 'tel':
            field_schema['type'] = 'string'
            field_schema['pattern'] = '^\+?(\d{1,3})?[-.\s]?(\(?\d{1,4}\)?)?[-.\s]?\d{1,4}[-.\s]?\d{1,4}[-.\s]?\d{1,9}$'
            # or simply '^[\d+\-()\s]{1,25}$' (max 25 symbols, +, -, (, ), numbers and space are allowed
        elif answer_type == 'url':
            field_schema['type'] = 'string'
            field_schema['format'] = 'hostname'
        elif answer_type == 'email':
            field_schema['type'] = 'string'
            field_schema['format'] = 'email'
        elif answer_type == 'date':
            field_schema['type'] = 'string'
            field_schema['format'] = 'date'
        elif answer_type == 'datetime-local':
            field_schema['type'] = 'string'
            field_schema['format'] = 'date-time'
        elif answer_type == 'time':
            field_schema['type'] = 'string'
            field_schema['format'] = 'time'
        elif answer_type == 'number':
            field_schema['type'] = 'number'
        elif answer_type == 'integer':
            field_schema['type'] = 'integer'
        elif answer_type == 'boolean':
            field_schema['type'] = 'boolean'

        if answer_type in ['number', 'integer']:
            if field.minimum:
                field_schema['minimum'] = field.minimum
            if field.maximum:
                field_schema['maximum'] = field.maximum
        return field_schema

    def get_schema_for_selectionfield(self, selectionfield):
        selectionfield_schema = create_base_schema__field({}, selectionfield)
        answer_type = selectionfield.answer_type
        options = selectionfield.getFolderContents()
        if answer_type == 'radio' or answer_type == 'select':
            selectionfield_schema['type'] = 'string'
            selectionfield_schema['enum'] = []
            for o in options:
                selectionfield_schema['enum'].append(o.Title)
        elif answer_type == 'checkbox' or answer_type == 'selectmultiple':
            selectionfield_schema['type'] = 'array'
            selectionfield_schema['items'] = {
                'enum': [],
                'type': 'string'
            }
            for o in options:
                selectionfield_schema['items']['enum'].append(o.Title)
        return selectionfield_schema

    def get_schema_for_uploadfield(self, uploadfield):
        uploadfield_schema = create_base_schema__field({}, uploadfield)
        answer_type = uploadfield.answer_type
        if answer_type == 'file':
            uploadfield_schema['type'] = 'string'
            uploadfield_schema['format'] = 'uri'
        elif answer_type == 'file-multi':
            uploadfield_schema['type'] = 'array'
            uploadfield_schema['items'] = {
                'type': 'string',
                'format': 'uri'
            }
        return uploadfield_schema

    def get_schema_for_array(self, array):
        array_schema = add_title_and_description({'type': 'array'}, array)
        array_schema = add_interninformation(array_schema, array)
        if array.required_choice == 'required':
            array_schema['minItems'] = 1
        array_schema['items'] = self.get_schema_for_object(array)
        return array_schema

    def get_schema_for_object(self, object):
        complex_schema = {}
        complex_schema['type'] = 'object'
        if object.portal_type != 'Array':
            # complex_schema['title'] = object.title
            # if object.description:
            #     complex_schema['description'] = object.description
            complex_schema = add_title_and_description(complex_schema, object)
            complex_schema = add_interninformation(complex_schema, object)
        complex_schema['properties'] = {}
        complex_schema['required'] = []
        complex_schema['dependentRequired'] = {}
        complex_schema['allOf'] = []

        children = object.getFolderContents()
        for child in children:
            child_object = child.getObject()
            child_id = create_id(child_object)

            # add children to the schema
            if child_object.portal_type == 'Fieldset':
                complex_schema = self.modify_schema_for_fieldset(complex_schema, child_object)
            else:
                complex_schema['properties'][create_id(child_object)] = self.get_schema_for_child(child_object)

            # mark children as required
            if child_object.portal_type in possibly_required_types and child_object.required_choice == 'required':
                if check_for_dependencies(child_object):
                    complex_schema = add_dependent_required(complex_schema, child_object, child_id)
                else:
                    complex_schema['required'].append(child_id)

        return complex_schema


"""
create base schema for a field, selectionfield or an uploadfield
"""
def create_base_schema__field(schema, child):
    base_schema = add_title_and_description(schema, child)
    # base_schema = add_userhelptext(base_schema, child)
    base_schema = add_interninformation(base_schema, child)
    return base_schema

def add_title_and_description(schema, child):
    schema['title'] = child.title
    if child.description:
        schema['description'] = child.description

    return schema

def add_interninformation(schema, child):
    if child.intern_information:
        schema['comment'] = child.intern_information
    return schema

def add_dependent_required(schema, child_object, child_id):
    dependencies = child_object.dependencies

    # copy 'allOf' and 'dependentRequired' to check that at least one of them changed
    schema_allof_copy = copy.deepcopy(schema['allOf'])
    schema_dependentrequired_copy = copy.deepcopy(schema['dependentRequired'])

    for dep in dependencies:
        try:
            dep = dep.to_object
            dep_id = create_id(dep)
            if dep.portal_type == 'Option':
                selection_parent = dep.aq_parent
                if_then = {
                    'if': {
                        'properties': {
                            create_id(selection_parent): {'const': dep.title}
                        }
                    },
                    'then': {
                        'required': child_id
                    }
                }
                # if 'allOf' in schema:
                #     schema['allOf'].append(if_then)
                # else:
                #     schema['allOf'] = [if_then]
                schema['allOf'].append(if_then)
            else:
                if dep_id in schema['dependentRequired']:
                    schema['dependentRequired'][dep_id].append(child_id)
                else:
                    schema['dependentRequired'][dep_id] = [child_id]
        except:
            # dependency got deleted, plone error, ignore this dependency
            continue
    
    # Check that at least one dependency wasn't deleted so that 'allOf' and/or 'dependentRequired' changed.
    # Otherwise add child_object to required-list of the schema, because it is required and not dependent required, if it has no valid dependencies anymore
    if schema_allof_copy == schema['allOf'] and schema_dependentrequired_copy == schema['dependentRequired']:
        schema['required'].append(child_id)
    return schema