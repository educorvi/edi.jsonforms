# -*- coding: utf-8 -*-

from edi.jsonforms import _
from Products.Five.browser import BrowserView
from plone import api

import copy
import json

from edi.jsonforms.views.common import *

class JsonSchemaView(BrowserView):
    is_extended_schema = False # True if schema is generated for an api call and not for the usual form view
    content_types_without_schema = ['Helptext', 'Button Handler']

    def __init__(self, context, request):
        super().__init__(context, request)
        self.jsonschema = {}
        self.ids = set()
        self.id_duplicates = set()

    def __call__(self):
        self.get_schema()
        return json.dumps(self.jsonschema, ensure_ascii=False, indent=4)
    
    def set_is_extended_schema(self, value=True):
        self.is_extended_schema = value
    
    def get_schema(self):
        form = self.context
        self.set_json_base_schema()

        children = form.getFolderContents()
        for child in children:
            self.add_child_to_schema(child.getObject())

        self.check_duplicates()

        return self.jsonschema
    
    def set_json_base_schema(self):
        self.jsonschema = {
            'type': 'object'
        }
        self.jsonschema['properties'] = {}
        self.jsonschema['required'] = []
        self.jsonschema['dependentRequired'] = {}
        self.jsonschema['allOf'] = []
        self.ids = set()
        self.id_duplicates = set()

    def add_child_to_schema(self, child_object):
        if child_object.portal_type in self.content_types_without_schema or not check_show_condition_in_request(self.request, child_object.show_condition, child_object.negate_condition):
            return
        child_id = self.create_and_check_id(child_object)

        # add children to the schema
        if child_object.portal_type == 'Fieldset':
            self.jsonschema = self.modify_schema_for_fieldset(self.jsonschema, child_object)
        else:
            self.jsonschema['properties'][child_id] = self.get_schema_for_child(child_object)

        # mark children as required
        if child_object.portal_type in possibly_required_types and child_object.required_choice == 'required':
            if check_for_dependencies(child_object):
                self.jsonschema = self.add_dependent_required(self.jsonschema, child_object, child_id)
            else:
                self.jsonschema['required'].append(child_id)

    def check_duplicates(self):
        if self.id_duplicates:
            if len(self.id_duplicates) == 1:
                message = _('The id {id} is not unique. Please change it manually due to possible unexpected behavior').format(id=list(self.id_duplicates)[0])
            else:
                message = _('The ids {ids} are not unique. Please change them manually due to possible unexpected behavior').format(ids=', '.join(self.id_duplicates))
            api.portal.show_message(
                message=message,
                request=self.request,
                type='warning'
            )

    def modify_schema_for_fieldset(self, schema, fieldset):
        children = fieldset.getFolderContents()
        for child in children:
            child_object = child.getObject()
            if not check_show_condition_in_request(self.request, child_object.show_condition, child_object.negate_condition):
                continue
            child_id = self.create_and_check_id(child_object)
            if child_object.portal_type == 'Fieldset':
                schema = self.modify_schema_for_fieldset(schema, child_object)
            elif child_object.portal_type not in self.content_types_without_schema:
                schema['properties'][child_id] = self.get_schema_for_child(child_object)
                if child_object.portal_type in possibly_required_types and child_object.required_choice == 'required':
                    if check_for_dependencies(child_object):
                        schema = self.add_dependent_required(schema, child_object, child_id)
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
        field_schema = self.create_base_schema__field({}, field)
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
        selectionfield_schema = self.create_base_schema__field({}, selectionfield)
        answer_type = selectionfield.answer_type
        options = selectionfield.getFolderContents()

        options_list = []
        if selectionfield.use_id_in_schema:
            for o in options:
                options_list.append(create_id(o))
        else:
            for o in options:
                options_list.append(o.Title)

        if answer_type == 'radio' or answer_type == 'select':
            selectionfield_schema['type'] = 'string'
            selectionfield_schema['enum'] = options_list
        elif answer_type == 'checkbox' or answer_type == 'selectmultiple':
            selectionfield_schema['type'] = 'array'
            selectionfield_schema['items'] = {
                'enum': options_list,
                'type': 'string'
            }
        return selectionfield_schema

    def get_schema_for_uploadfield(self, uploadfield):
        uploadfield_schema = self.create_base_schema__field({}, uploadfield)
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
        array_schema = self.add_title_and_description({'type': 'array'}, array)
        array_schema = add_interninformation(array_schema, array)
        if array.required_choice == 'required':
            array_schema['minItems'] = 1
        array_schema['items'] = self.get_schema_for_object(array)
        return array_schema

    def get_schema_for_object(self, object):
        complex_schema = {}
        complex_schema['type'] = 'object'
        if object.portal_type != 'Array':
            complex_schema = self.add_title_and_description(complex_schema, object)
            complex_schema = add_interninformation(complex_schema, object)
        complex_schema['properties'] = {}
        complex_schema['required'] = []
        complex_schema['dependentRequired'] = {}
        complex_schema['allOf'] = []

        children = object.getFolderContents()
        for child in children:
            child_object = child.getObject()
            if not check_show_condition_in_request(self.request, child_object.show_condition, child_object.negate_condition):
                continue
            child_id = self.create_and_check_id(child_object)

            # add children to the schema
            if child_object.portal_type == 'Fieldset':
                complex_schema = self.modify_schema_for_fieldset(complex_schema, child_object)
            elif child_object.portal_type not in self.content_types_without_schema:
                complex_schema['properties'][child_id] = self.get_schema_for_child(child_object)

            # mark children as required
            if child_object.portal_type in possibly_required_types and child_object.required_choice == 'required':
                if check_for_dependencies(child_object):
                    complex_schema = self.add_dependent_required(complex_schema, child_object, child_id)
                else:
                    complex_schema['required'].append(child_id)

        return complex_schema
    
    def add_dependent_required(self, schema, child_object, child_id):
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
                                create_id(selection_parent): {'const': get_title(self.request, dep)}
                            }
                        },
                        'then': {
                            'required': [child_id]
                        }
                    }

                    if self.is_extended_schema:
                        if_then['else'] = create_else_statement(child_object)
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
    
    def create_and_check_id(self, object):
        id = create_id(object)
        if id not in self.ids:
            self.ids.add(id)
        else:
            self.id_duplicates.add(id)
        return id
    
    """
    create base schema for a field, selectionfield or an uploadfield
    """
    def create_base_schema__field(self, schema, child):
        base_schema = self.add_title_and_description(schema, child)
        # base_schema = add_userhelptext(base_schema, child)
        base_schema = add_interninformation(base_schema, child)
        return base_schema    

    def add_title_and_description(self, schema, child):
        schema['title'] = get_title(child, self.request)
        description = get_description(child, self.request)
        if description:
            schema['description'] = description

        return schema



def check_for_dependencies(child_object):
    if child_object.dependencies is not None and child_object.dependencies != []:
        return True
    else:
        return False

def add_interninformation(schema, child):
    if child.intern_information:
        schema['comment'] = child.intern_information
    return schema

def create_else_statement(child_object):
    if child_object.portal_type == 'Field':
        if child_object.answer_type in string_type_fields:
            return {
                'properties': {
                    create_id(child_object): {'maxLength': 0}
                }
            }
