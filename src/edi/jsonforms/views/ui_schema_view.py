# -*- coding: utf-8 -*-

from urllib.parse import urlencode
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
            child_schema = self.get_schema_for_child(child_object, '/properties/')
            if child_schema != None and child_schema != {}:
                layout['elements'].append(child_schema)

        buttons = {
            "type": "Buttongroup",
            "buttons": [
                # {
                #     "type": "Button",
                #     "buttonType": "submit",
                #     "text": _("Submit"),
                #     "options": {
                #         "variant": "primary"
                #     }
                # },
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
        return json.dumps(self.uischema, ensure_ascii=False)

    def get_schema_for_child(self, child, scope, recursive=True):
        type = child.portal_type

        if type == 'Field':
            return self.get_schema_for_field(child, scope)
        elif type == 'SelectionField':
            return self.get_schema_for_selectionfield(child, scope)
        elif type == 'UploadField':
            return self.get_schema_for_uploadfield(child, scope)
        elif type == 'Helptext':
            return self.get_schema_for_helptext(child)
        elif type == 'Button Handler':
            return self.get_schema_for_buttons(child)
        elif type == 'Array':
            return self.get_schema_for_array(child, scope, recursive)
        elif type == 'Complex':
            return self.get_schema_for_object(child, scope, recursive)
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

        self.add_user_info(field, field_schema)
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

        if selectionfield.use_id_in_schema:
            selectionfield_schema['options']['enumTitles'] = {}
            for option in selectionfield.getFolderContents():
                selectionfield_schema['options']['enumTitles'][create_id(option)] = option.Title

        self.add_user_info(selectionfield, selectionfield_schema)
        return selectionfield_schema

    def get_schema_for_uploadfield(self, uploadfield, scope):
        uploadfield_schema = self.get_base_schema(uploadfield, scope)

        if uploadfield.accepted_file_types:
            uploadfield_schema['options'] = {'acceptedFileType': uploadfield.accepted_file_types}
        else:
            uploadfield_schema['options'] = {'acceptedFileType': '*'}

        if uploadfield.answer_type == 'file-multi':
            uploadfield_schema['options']['allowMultipleFiles'] = True

        self.add_user_info(uploadfield, uploadfield_schema)
        return uploadfield_schema

    def get_schema_for_helptext(self, helptext):
        # helptext as html-element
        helptext = {
            'type': 'HTML',
            'htmlData': str(helptext.helptext.output)
        }
        return helptext

    def get_schema_for_buttons(self, button_handler):
        buttons = button_handler.getFolderContents()
        if len(buttons) == 0:
            return {}
        
        buttons_schema = {
            "type": "Buttongroup",
            "buttons": []
        }

        for button in buttons:
            button = button.getObject()

            request_url = "http://localhost:8080/Plone3/fragebogen-test-else-zweig/@send-email"

            query_params = {
                "to_address": button.to_address
            }

            if button.reply_to_address:
                query_params['reply_to_address'] = button.reply_to_address
            if button.email_subject:
                query_params['subject'] = button.email_subject
            if button.email_text:
                query_params['email_text'] = button.email_text

            # Encode the query parameters
            encoded_query = urlencode(query_params)

            # Combine the base URL with the encoded query parameters
            request_url = f"{request_url}?{encoded_query}"

            button_schema = {
                "type": "Button",
                "buttonType": "submit",
                "text": button.button_label,
                "options": {
                    "variant": "success",
                    "submitOptions": {
                        "action": "request",
                        "request": {
                            "url": request_url,
                            "method": "POST",
                            "headers": {
                                'Accept': 'application/json',
                                'Content-Type': 'application/json'
                            }
                        }
                    }
                },
            }
            buttons_schema['buttons'].append(button_schema)

        return buttons_schema


    def get_schema_for_array(self, array, scope, recursive=True):
        # save scope in lookup_scopes
        array_id = create_id(array)
        array_scope = scope + array_id
        # self.lookup_scopes[array_id] = array_scope

        array_schema = {
            'type': 'Control',
            'scope': array_scope
        }

        if array.dependencies:
            showOn = create_showon_properties(array, self.lookup_scopes)
            if showOn != {}:
                array_schema['showOn'] = showOn

        # add children of array to the schema
        if recursive:
            array_schema['options'] = {'descendantControlOverrides': self.create_descendantControlOverrides(array_scope, array)}

        self.add_user_info(array, array_schema)

        return array_schema
    
    def get_schema_for_object(self, complex, scope, recursive=True):
        # save scope in lookup_scopes
        complex_id = create_id(complex)
        complex_scope = scope + complex_id

        # self.lookup_scopes[complex_id] = complex_scope

        complex_schema = {
            'type': 'Control',
            'scope': complex_scope
        }

        if complex.dependencies:
            showOn = create_showon_properties(complex, self.lookup_scopes)
            if showOn != {}:
                complex_schema['showOn'] = showOn

        # add children of complex to the schema
        if recursive:
            complex_schema['options'] = {'descendantControlOverrides': self.create_descendantControlOverrides(complex_scope, complex)}

        self.add_user_info(complex, complex_schema)

        return complex_schema


    def add_child_to_descendantControlOverrides(self, descendantControlOverrides, child_object, base_scope):
        child_tmp_schema = {}

        # add options and showon to the descendantControlOverrides
        if child_object.portal_type in ["Field", "SelectionField", "UploadField", "Complex", "Array"]:
            # descendantControlOverrides = add_control(descendantControlOverrides, child_object, scope)
            child_tmp_schema = self.get_schema_for_child(child_object, base_scope, False)
            
            child_schema = {}
            if "options" in child_tmp_schema:
                child_schema['options'] = child_tmp_schema['options']
            if "showOn" in child_tmp_schema:
                child_schema['showOn'] = child_tmp_schema['showOn']

            if child_schema != {}:
                descendantControlOverrides[child_tmp_schema['scope']] = child_schema
        else:   # ignore this type
            pass

        # add it recursively if child_object is a container type
        if child_object.portal_type in ["Complex", "Array"]:
            container_base_scope = child_tmp_schema['scope']
            if child_object.portal_type == "Array":
                container_base_scope += "/items/properties/"
            elif child_object.portal_type == "Complex":
                container_base_scope += "/properties/"
            for c in child_object.getFolderContents():
                c_object = c.getObject()
                descendantControlOverrides = self.add_child_to_descendantControlOverrides(descendantControlOverrides, c_object, container_base_scope)

        return descendantControlOverrides

    # only call if parent_object of portal_type Array or Complex
    def create_descendantControlOverrides(self, scope, parent_object):
        # add children to array_schema
        descendantControlOverrides = {}
        base_scope = scope
        if parent_object.portal_type == "Array":
            base_scope += "/items"
        base_scope += "/properties/"

        for child in parent_object.getFolderContents():
            child_object = child.getObject()
            descendantControlOverrides = self.add_child_to_descendantControlOverrides(descendantControlOverrides, child_object, base_scope)
    
        return descendantControlOverrides









    # ????????
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

    def add_user_info(self, child, child_schema):
        pass
    #     # TODO comes with ui-schema version 3.1
    #     if child.user_info:
    #         if 'options' in child_schema:
    #             child_schema['options']['helptext'] = child.user_info
    #         else:
    #             child_schema['options'] = {'helptext': child.user_info}

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

                child_schema = self.get_schema_for_child(child_object, scope)
                if child_schema != None and child_schema != {}:
                    group_schema['elements'].append(child_schema)

        return group_schema
