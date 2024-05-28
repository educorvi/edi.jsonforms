# -*- coding: utf-8 -*-

from edi.jsonforms import _
from Products.Five.browser import BrowserView
import json

# from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile


class JsonSchemaView(BrowserView):
    # If you want to define a template here, please remove the template from
    # the configure.zcml registration of this view.
    # template = ViewPageTemplateFile('json_schema_view.pt')
    jsonschema = {}

    possibly_required_types = ['Field', 'SelectionField', 'Array']

    def __call__(self):
        form = self.context
        self.jsonschema['type'] = 'object'
        self.jsonschema = add_title_and_description(self.jsonschema, form.title, form.description)

        children = form.getFolderContents()
        self.jsonschema['properties'] = {}
        self.jsonschema['required'] = []
        self.jsonschema['dependentRequired'] = {}
        for child in children:
            child_object = child.getObject()
            child_id = create_id(child.id, child_object.UID())

            # add children to the schema
            if child_object.portal_type == 'Fieldset':
                self.jsonschema = self.modify_schema_for_fieldset(self.jsonschema, child_object)
            else:
                self.jsonschema['properties'][child_id] = self.get_schema_for_child(child_object)

            # mark children as required
            if child_object.portal_type in self.possibly_required_types and child_object.required_choice == 'required':
                if child_object.dependent_from_object is not None:
                    self.jsonschema = self.add_dependent_required(self.jsonschema, child_object, child_id)
                else:
                    self.jsonschema['required'].append(child_id)

        # Implement your own actions:
        self.msg = json.dumps(self.jsonschema)
        return self.index()

    def add_dependent_required(self, schema, child_object, child_id):
        dependent_from = child_object.dependent_from_object.to_object
        dependent_id = create_id(dependent_from.id, dependent_from.UID())
        if dependent_from.portal_type == 'Option':
            selection_parent = dependent_from.aq_parent
            if_then = {
                'if': {
                    'properties': {
                        create_id(selection_parent.id, selection_parent.UID()): {'const': dependent_from.title}
                    }
                },
                'then': {
                    'required': child_id
                }
            }
            if 'allOf' in schema:
                schema['allOf'].append(if_then)
            else:
                schema['allOf'] = [if_then]
        else:
            if dependent_id in schema['dependentRequired']:
                schema['dependentRequired'][dependent_id].append(child_id)
            else:
                schema['dependentRequired'][dependent_id] = [child_id]
        return schema

    def modify_schema_for_fieldset(self, schema, fieldset):
        children = fieldset.getFolderContents()
        for child in children:
            child_object = child.getObject()
            child_id = create_id(child.id, child_object.UID())
            if child_object.portal_type == 'Fieldset':
                schema = modify_schema_for_fieldset(self, schema, child_object)
            else:
                schema['properties'][child_id] = self.get_schema_for_child(child_object)
                if child_object.portal_type in self.possibly_required_types and child_object.required_choice == 'required':
                    schema['required'].append(child_id)
                    schema = add_title_and_description(schema, child_object.title, child_object.description)
        return schema

    def get_schema_for_child(self, child):
        type = child.portal_type

        if type == 'Field':
            return self.get_schema_for_field(child)
        elif type == 'SelectionField':
            return self.get_schema_for_selectionfield(child)
        elif type == 'Array':
            return self.get_schema_for_array(child)
        elif type == 'Complex':
            return self.get_schema_for_object(child)
        return {}

    def get_schema_for_field(self, field):
        field_schema = add_title_and_description({}, field.title, field.description)
        answer_type = field.answer_type
        if answer_type == 'text':
            field_schema['type'] = 'string'
        elif answer_type == 'textarea':
            field_schema['type'] = 'string'
        elif answer_type == 'password':
            field_schema['type'] = 'string'
        elif answer_type == 'tel':
            field_schema['type'] = 'string'
            field_schema['pattern'] = '^\+?(\d{1,3})?[-.\s]?(\(?\d{1,4}\)?)?[-.\s]?\d{1,4}[-.\s]?\d{1,4}[-.\s]?\d{1,9}$'
            # or simply '^[\d+\-()\s]{1,25}$' (max 25 symbols, +, -, (, ), numbers and space are allowed
        elif answer_type == 'url':
            field_schema['type'] = 'string'
            field_schema['type'] = 'hostname'
        elif answer_type == 'email':
            field_schema['type'] = 'string'
            field_schema['format'] = 'email'
        elif answer_type == 'date':
            field_schema['type'] = 'string'
            field_schema['type'] = 'date'
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
        return field_schema

    def get_schema_for_selectionfield(self, selectionfield):
        selectionfield_schema = add_title_and_description({}, selectionfield.title, selectionfield.description)
        answer_type = selectionfield.answer_type
        options = selectionfield.getFolderContents()
        if answer_type == 'radio' or answer_type == 'select':
            selectionfield_schema['type'] = 'string'
            selectionfield_schema['enum'] = []
        elif answer_type == 'checkbox' or answer_type == 'selectmultiple':
            selectionfield_schema['type'] = 'array'
            selectionfield_schema['enum'] = []
        elif answer_type == 'file':
            selectionfield_schema['type'] = 'string'
            selectionfield_schema['format'] = 'uri'
        elif answer_type == 'file-multi':
            selectionfield_schema['type'] = 'array'
            selectionfield_schema['items'] = {
                'type': 'string',
                'format': 'uri'
            }

        if answer_type in ['radio', 'checkbox']:
            for o in options:
                selectionfield_schema['enum'].append(o.Title)
        return selectionfield_schema

    def get_schema_for_array(self, array):
        array_schema = add_title_and_description({'type': 'array'}, array.title, array.description)
        if array.required_choice == 'required':
            array_schema['minItems'] = 1
        array_schema['items'] = self.get_schema_for_object(array)
        return array_schema

    def get_schema_for_object(self, object):
        complex_schema = {}
        complex_schema['type'] = 'object'
        if object.portal_type != 'Array':
            complex_schema['title'] = object.title
            if object.description:
                complex_schema['description'] = object.description
        complex_schema['properties'] = {}
        complex_schema['required'] = []

        children = object.getFolderContents()
        for child in children:
            child_object = child.getObject()
            child_id = create_id(child.id, child_object.UID())

            # add children to the schema
            if child_object.portal_type == 'Fieldset':
                complex_schema = self.modify_schema_for_fieldset(complex_schema, child_object)
            else:
                complex_schema['properties'][create_id(child.id, child_object.UID())] = self.get_schema_for_child(child_object)

            # mark children as required
            if child_object.portal_type in self.possibly_required_types and child_object.required_choice == 'required':
                if child_object.dependent_from_object is not None:
                    complex_schema = self.add_dependent_required(complex_schema, child_object, child_id)
                else:
                    complex_schema['required'].append(child_id)

        return complex_schema



def add_title_and_description(schema, title, description):
    schema['title'] = title
    if description:
        schema['description'] = description
    return schema

def create_id(id, uid):
    return str(id) + str(uid)
