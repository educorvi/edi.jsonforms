# -*- coding: utf-8 -*-

from edi.jsonforms import _
from Products.Five.browser import BrowserView
import json

from edi.jsonforms import _
from edi.jsonforms.views.common import possibly_required_types, create_id
from edi.jsonforms.views.showOn_properties import create_showon_properties



class UiSchemaView(BrowserView):

    def __init__(self, context, request):
        super().__init__(context, request)
        self.uischema = {}

        # needed to put scopes in showOn-properties without having to compute them
        self.lookup_scopes = {}

    def __call__(self):
        self.uischema = {}
        self.lookup_scopes = {}

        form = self.context
        self.uischema = {'version': '2.0', 'layout': {}}

        layout = {'type': 'VerticalLayout', 'elements': []}

        children = form.getFolderContents()
        for child in children:
            child_object = child.getObject()

            # add children to the schema
            layout['elements'].append(self.get_schema_for_child(child_object, '/properties/'))

        buttons = {
            "type": "Buttongroup",
            "buttons": [
                {
                    "type": "Button",
                    "buttonType": "submit",
                    "text": _("Submit"),
                    "options": {
                        "variant": "primary"
                    }
                },
                {
                    "type": "Button",
                    "buttonType": "reset",
                    "text": _("Reset this form"),
                    "options": {
                        "variant": "danger"
                    }
                }
            ]
        }
        layout['elements'].append(buttons)
        self.uischema['layout'] = layout
        return json.dumps(self.uischema)

    def get_schema_for_child(self, child, scope):
        type = child.portal_type

        if type == 'Field':
            return self.get_schema_for_field(child, scope)
        elif type == 'SelectionField':
            return self.get_schema_for_selectionfield(child, scope)
        elif type == 'UploadField':
            return self.get_schema_for_uploadfield(child, scope)
        elif type == 'Array':
            return self.get_schema_for_array(child, scope)
        elif type == 'Complex':
            return self.get_schema_for_object(child, scope)
        elif type == 'Fieldset':
            return self.get_schema_for_fieldset(child, scope)
        return {}

    def get_schema_for_field(self, field, scope):
        field_schema = self.get_base_schema(field, scope)

        answer_type = field.answer_type
        if answer_type == 'text':
            pass
        elif answer_type == 'textarea':
            field_schema['options'] = {'multi': True}
        elif answer_type == 'password':
            field_schema['options'] = {'format': 'password'}
        elif answer_type == 'tel':
            field_schema['options'] = {'format': 'tel'}
        elif answer_type == 'url':
            field_schema['options'] = {'format': 'url'}
        elif answer_type == 'email':
            field_schema['options'] = {'format': 'email'}
        elif answer_type == 'date':
            field_schema['options'] = {'format': 'date'}
        elif answer_type == 'datetime-local':
            field_schema['options'] = {'format': 'date-time'}
        elif answer_type == 'time':
            field_schema['options'] = {'format': 'time'}
        elif answer_type in ['number', 'integer']:
            if field.unit:
                field_schema['options'] = {'append': field.unit}
        elif answer_type == 'boolean':
            pass
            # TODO

        if field.placeholder and field.answer_type in ['text', 'textarea', 'password', 'tel', 'url', 'email']:
            if 'options' in field_schema:
                field_schema['options']['placeholder'] = field.placeholder
            else:
                field_schema['options'] = {'placeholder': field.placeholder}
        return field_schema

    def get_schema_for_selectionfield(self, selectionfield, scope):
        selectionfield_schema = self.get_base_schema(selectionfield, scope)

        answer_type = selectionfield.answer_type
        if answer_type == 'radio':
            selectionfield_schema['options'] = {
                'displayAs': 'radiobuttons',
                'stacked': True
            }
        elif answer_type in ['checkbox', 'selectmultiple']:
            # TODO differentiate between checkbox and selectmultiple, both are displayed as checkboxes
            selectionfield_schema['options'] = {'stacked': True}
        elif answer_type == 'select':
            pass # nothing

        return selectionfield_schema

    def get_schema_for_uploadfield(self, uploadfield, scope):
        uploadfield_schema = self.get_base_schema(uploadfield, scope)

        if uploadfield.accepted_file_types:
            uploadfield_schema['options'] = {'acceptedFileType': uploadfield.accepted_file_types}
        else:
            uploadfield_schema['options'] = {'acceptedFileType': '*'}

        if uploadfield.answer_type == 'file-multi':
            uploadfield_schema['options']['allowMultipleFiles'] = True

        return uploadfield_schema


    def get_schema_for_array(self, array, scope, recursive=True):
        # save scope in lookup_scopes
        array_id = create_id(array)
        array_scope = scope + array_id
        # self.lookup_scopes[array_id] = array_scope

        array_schema = {
            'type': 'Control',
            'scope': array_scope,
            'options': {
                'descendantControlOverrides': {}
            }
        }

        if array.dependencies:
            showOn = create_showon_properties(array, self.lookup_scopes)
            if showOn != {}:
                array_schema['showOn'] = showOn

        def add_child(descendantControlOverrides, child_object, base_scope):
            if child_object.portal_type in ["Field", "SelectionField", "UploadField"]:
                descendantControlOverrides = add_control(descendantControlOverrides, child_object, base_scope)
            elif child_object.portal_type in ["Fieldset", "Complex"]:
                descendantControlOverrides = add_group(descendantControlOverrides, child_object, base_scope)
            elif child_object.portal_type == "Array":
                descendantControlOverrides = add_array(descendantControlOverrides, child_object, base_scope)
            else:   # ignore this type
                pass
            return descendantControlOverrides
        
        def convert_to_child_of_array_schema(schema):
            child_schema = {}
            if "options" in schema:
                child_schema['options'] = schema['options']
            if "showOn" in schema:
                child_schema['showOn'] = schema['showOn']
            return child_schema

        def add_control(descendantControlOverrides, child_object, base_scope):
            child_tmp_schema = self.get_schema_for_child(child_object, base_scope)
            child_schema = convert_to_child_of_array_schema(child_tmp_schema)
            if child_schema != {}:
                descendantControlOverrides[child_tmp_schema['scope']] = child_schema
            return descendantControlOverrides

        def add_group(descendantControlOverrides, object, scope):
            if object.portal_type == "Fieldset":
                # child_tmp_schema = self.get_schema_for_fieldset(object, scope, False)
                base_scope = scope
            elif object.portal_type == "Complex":
                child_tmp_schema = self.get_schema_for_object(object, scope, False)
                complex_scope = scope + create_id(object)
                base_scope = complex_scope + "/properties/"

                child_schema = convert_to_child_of_array_schema(child_tmp_schema)
                if child_schema != {}:
                    descendantControlOverrides[complex_scope] = child_schema
            else:
                return descendantControlOverrides

            # add children
            children = object.getFolderContents()
            for child in children:
                child_object = child.getObject()
                descendantControlOverrides = add_child(descendantControlOverrides, child_object, base_scope)

            return descendantControlOverrides

        def add_array(descendantControlOverrides, object, scope):
            child_tmp_schema = self.get_schema_for_array(object, scope, False)
            if "showOn" in child_tmp_schema:
                descendantControlOverrides[child_tmp_schema['scope']]['showOn'] = child_tmp_schema['showOn']

            base_scope = child_tmp_schema['scope'] + "/items/properties/"
            children = object.getFolderContents()
            for child in children:
                child_object = child.getObject()
                descendantControlOverrides = add_child(descendantControlOverrides, child_object, base_scope)

            return descendantControlOverrides

        if recursive:
            # add children to array_schema
            base_scope = array_scope + "/items/properties/"
            descendantControlOverrides = {}
            children = array.getFolderContents()
            for child in children:
                child_object = child.getObject()
                descendantControlOverrides = add_child(descendantControlOverrides, child_object, base_scope)

            array_schema['options']['descendantControlOverrides'] = descendantControlOverrides

        return array_schema
    
    def get_schema_for_object(self, complex, scope, recursive=True):
        # save scope in lookup_scopes
        complex_id = create_id(complex)
        complex_scope = scope + complex_id
        # self.lookup_scopes[complex_id] = complex_scope

        return self.create_group(complex, complex_scope + '/properties/', recursive)

    def get_schema_for_fieldset(self, fieldset, scope, recursive=True):
        # save scope in lookup_scopes
        # fieldset_id = create_id(fieldset)
        # fieldset_scope = scope + fieldset_id
        # self.lookup_scopes[fieldset_id] = fieldset_scope

        return self.create_group(fieldset, scope, recursive)


    def get_base_schema(self, child, scope):
        child_id = create_id(child)
        child_scope = scope + child_id
        base_schema = {
            'type': 'Control',
            'scope': child_scope,
        }
        self.lookup_scopes[child_id] = child_scope

        # add showOn dependencies
        if child.dependencies:
            showOn = create_showon_properties(child, self.lookup_scopes)
            if showOn != {}:
                base_schema['showOn'] = showOn

        return base_schema

    def create_group(self, group, scope, recursive):
        group_schema = {
            'type': 'Group',
            'options': {'label': group.title},
        }

        if group.dependencies:
            showOn = create_showon_properties(group, self.lookup_scopes)
            if showOn != {}:
                group_schema['showOn'] = showOn

        if recursive:
            group_schema['elements'] = []
            children = group.getFolderContents()
            for child in children:
                child_object = child.getObject()
                group_schema['elements'].append(self.get_schema_for_child(child_object, scope))

        return group_schema
