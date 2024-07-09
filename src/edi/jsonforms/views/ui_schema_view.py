# -*- coding: utf-8 -*-

from edi.jsonforms import _
from Products.Five.browser import BrowserView
import json

from edi.jsonforms import _
from edi.jsonforms.views.common import possibly_required_types, create_id
from edi.jsonforms.views.showOn_properties import create_showon_properties



class UiSchemaView(BrowserView):
    uischema = {}

    # needed to put scopes in showOn-properties without having to compute them
    lookup_scopes = {}

    def __call__(self):
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


    def get_schema_for_array(self, array, scope):
        # save scope in lookup_scopes
        array_id = array.id + array.UID()
        array_scope = scope + array_id
        # self.lookup_scopes[array_id] = array_scope

        #return self.create_group(array, array_scope + '/properties/')
        array_schema = {
            'type': 'Control',
            'scope': array_scope,
            'options': {
                'childUiSchema': {
                    'type': 'Control',
                    'scope': array_scope + '/items',
                    'options': {
                        'placeholder': _('Enter an array element'),
                        'label': False
                    },
                    'elements': []
                }
            }
        }

        if array.dependencies:
            array_schema['showOn'] = create_showon_properties(array, self.lookup_scopes)

        children = array.getFolderContents()
        for child in children:
            child_object = child.getObject()

            # add children to the schema
            array_schema['options']['childUiSchema']['elements'].append(self.get_schema_for_child(child_object, array_scope + '/items/'))

        return array_schema

    def get_schema_for_object(self, complex, scope):
        # save scope in lookup_scopes
        complex_id = complex.id + complex.UID()
        complex_scope = scope + complex_id
        # self.lookup_scopes[complex_id] = complex_scope

        return self.create_group(complex, complex_scope + '/properties/')

    def get_schema_for_fieldset(self, fieldset, scope):
        # save scope in lookup_scopes
        # fieldset_id = fieldset.id + fieldset.UID()
        # fieldset_scope = scope + fieldset_id
        # self.lookup_scopes[fieldset_id] = fieldset_scope

        return self.create_group(fieldset, scope)


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
            base_schema['showOn'] = create_showon_properties(child, self.lookup_scopes)

        return base_schema

    def create_group(self, group, scope):
        group_schema = {
            'type': 'Group',
            'options': {'label': group.title},
        }

        if group.dependencies:
            group_schema['showOn'] = create_showon_properties(group, self.lookup_scopes)

        group_schema['elements'] = []
        children = group.getFolderContents()
        for child in children:
            child_object = child.getObject()
            group_schema['elements'].append(self.get_schema_for_child(child_object, scope))

        return group_schema
