# -*- coding: utf-8 -*-

from copy import deepcopy
from urllib.parse import urlencode
from edi.jsonforms import _
from Products.Five.browser import BrowserView
import json

from edi.jsonforms import _
from edi.jsonforms.views.common import *
from edi.jsonforms.views.showOn_properties import create_showon_properties



class UiSchemaView(BrowserView):

    tools_on = True

    def __init__(self, context, request):
        super().__init__(context, request)
        self.uischema = {}

        # needed to put scopes in showOn-properties without having to compute them
        self.lookup_scopes = {}
    
    def __call__(self):
        self.get_schema()
        return json.dumps(self.uischema, ensure_ascii=False, indent=4)
    
    def set_tools_on(self, tools_on):
        self.tools_on = tools_on
    
    def get_schema(self):
        self.set_ui_base_schema()
        
        form = self.context
        children = form.getFolderContents()
        for child in children:
            self.add_child_to_schema(child.getObject())

        return self.uischema
    
    def set_ui_base_schema(self):
        self.uischema = {}
        self.lookup_scopes = {}

        self.uischema = {
            'version': '2.0',
            'layout': {
                'type': 'VerticalLayout',
                'elements': []
            }
        }

    def add_child_to_schema(self, child_object):
        if child_object.portal_type != 'Button Handler' and not check_show_condition_in_request(self.request, child_object.show_condition, child_object.negate_condition):
            return

        # add children to the schema
        child_schema = self.get_schema_for_child(child_object, '/properties/')
        if child_schema != None and child_schema != {}:
            self.uischema['layout']['elements'].append(child_schema)

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
            field_schema['options']['multi'] = True
        elif answer_type == 'password':
            field_schema['options']['format'] = 'password'
        elif answer_type == 'tel':
            field_schema['options']['format'] = 'tel'
        elif answer_type == 'url':
            field_schema['options']['format'] = 'url'
        elif answer_type == 'email':
            field_schema['options']['format'] = 'email'
        elif answer_type == 'date':
            field_schema['options']['format'] = 'date'
        elif answer_type == 'datetime-local':
            field_schema['options']['format'] = 'datetime-local'
        elif answer_type == 'time':
            field_schema['options']['format'] = 'time'
        elif answer_type in ['number', 'integer']:
            unit = get_unit(field, self.request)
            if unit:
                field_schema['options']['append'] = unit
        elif answer_type == 'boolean':
            pass
            # TODO

        placeholder = get_placeholder(field, self.request)
        if placeholder and field.answer_type in ['text', 'textarea', 'password', 'tel', 'url', 'email']:
            field_schema['options']['placeholder'] = placeholder

        # remove unnecessary options
        if field_schema['options'] == {}:
            del field_schema['options']

        self.add_user_info(field, field_schema)
        return field_schema

    def get_schema_for_selectionfield(self, selectionfield, scope):
        selectionfield_schema = self.get_base_schema(selectionfield, scope)

        answer_type = selectionfield.answer_type
        if answer_type == 'radio':
            selectionfield_schema['options']['displayAs'] = 'radiobuttons'
            selectionfield_schema['options']['stacked'] = True
        elif answer_type in ['checkbox', 'selectmultiple']:
            # TODO differentiate between checkbox and selectmultiple, both are displayed as checkboxes
            selectionfield_schema['options']['stacked'] = True
        elif answer_type == 'select':
            pass

        if selectionfield.use_id_in_schema:
            selectionfield_schema['options']['enumTitles'] = {}
            for option in selectionfield.getFolderContents():
                selectionfield_schema['options']['enumTitles'][create_id(option)] = option.Title
        
        if selectionfield_schema['options'] == {}:
            del selectionfield_schema['options']

        self.add_user_info(selectionfield, selectionfield_schema)
        return selectionfield_schema

    def get_schema_for_uploadfield(self, uploadfield, scope):
        uploadfield_schema = self.get_base_schema(uploadfield, scope)

        if uploadfield.accepted_file_types:
            uploadfield_schema['options']['acceptedFileType'] = uploadfield.accepted_file_types
        else:
            uploadfield_schema['options']['acceptedFileType'] = '*'

        if uploadfield.answer_type == 'file-multi':
            uploadfield_schema['options']['allowMultipleFiles'] = True

        self.add_user_info(uploadfield, uploadfield_schema)
        return uploadfield_schema

    def get_schema_for_helptext(self, helptext):
        # helptext as html-element
        tmp_schema = self.add_tools_to_schema({}, helptext)

        helptext_schema = {
            'type': 'HTML',
            'htmlData': tmp_schema['options']['preHtml'] + '\n' + str(helptext.helptext.output),
        }
        return helptext_schema

    def get_schema_for_buttons(self, button_handler):
        request_button_schema = {
            "type": "Button",
            "buttonType": "submit",
            "text": "", # FILL
            "options": {
                "variant": "success",
                "submitOptions": {
                    "action": "request",
                    "request": {
                        "url": "", # FILL
                        "method": "POST",
                        "headers": {
                            'Accept': 'application/json',
                            'Content-Type': 'application/json'
                        }
                    }
                }
            },
        }
        
        buttons = button_handler.getFolderContents()
        if len(buttons) == 0:
            return {}
        
        buttons_schema = {
            "type": "Buttongroup",
            "buttons": []
        }

        for button in buttons:
            button = button.getObject()

            if button.portal_type == 'Email Handler':
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

                button_schema = request_button_schema.copy()
                button_schema['text'] = button.button_label
                button_schema['options']['submitOptions']['request']['url'] = request_url

                buttons_schema['buttons'].append(button_schema)
            elif button.portal_type == 'Reset Button':
                button_schema = {
                    "type": "Button",
                    "buttonType": "reset",
                    "text": button.button_label,
                    "options": {
                        "variant": "danger"
                    }
                }
                buttons_schema['buttons'].append(button_schema)
            elif button.portal_type == 'Webservice Handler':
                request_url = "http://localhost:8080/Plone3/fragebogen-test-else-zweig/@webservice-request"

                i = 1
                query_params = {}
                endpoints = button.getFolderContents()
                for endpoint in endpoints:
                    endpoint = endpoint.getObject()
                    if endpoint.portal_type == 'Endpoint':
                        query_params[f'endpoint_{i}_url'] = endpoint.url
                        if endpoint.api_key_header_name and endpoint.api_key:
                            query_params[f'endpoint_{i}_api_key_header_name'] = endpoint.api_key_header_name
                            query_params[f'endpoint_{i}_api_key'] = endpoint.api_key
                    i += 1

                if button.page_after_success:
                    query_params['page_after_success'] = button.page_after_success
                encoded_query = urlencode(query_params)
                request_url = f"{request_url}?{encoded_query}"

                button_schema = deepcopy(request_button_schema)
                button_schema['text'] = button.button_label
                button_schema['options']['submitOptions']['request']['url'] = request_url

                buttons_schema['buttons'].append(button_schema)

        return buttons_schema


    def get_schema_for_array(self, array, scope, recursive=True):
        # don't save scope because one cannot depend on an array
        array_schema = self.get_base_schema(array, scope, save_scope=False, has_user_helptext=False)
        array_scope = scope + create_id(array)

        # add children of array to the schema
        if recursive:
            array_schema['options']['descendantControlOverrides'] = self.create_descendantControlOverrides(array_scope, array)

        self.add_user_info(array, array_schema)

        if array_schema['options'] == {}:
            del array_schema['options']

        return array_schema
    
    def get_schema_for_object(self, complex, scope, recursive=True):
        # don't save scope because one cannot depend on a complex object
        complex_schema = self.get_base_schema(complex, scope, save_scope=False, has_user_helptext=False)
        complex_scope = scope + create_id(complex)

        # add children of complex to the schema
        if recursive:
            complex_schema['options']['descendantControlOverrides'] = self.create_descendantControlOverrides(complex_scope, complex)

        self.add_user_info(complex, complex_schema)

        if complex_schema['options'] == {}:
            del complex_schema['options']

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
                if not check_show_condition_in_request(self.request, c_object.show_condition, c_object.negate_condition):
                    continue
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
            if not check_show_condition_in_request(self.request, child_object.show_condition, child_object.negate_condition):
                continue
            descendantControlOverrides = self.add_child_to_descendantControlOverrides(descendantControlOverrides, child_object, base_scope)
    
        return descendantControlOverrides


    def add_tools_to_schema(self, child_schema, child_object):
        if self.tools_on:
            # html_links = ['<span>\
            #             <a href="{view_url}" title="View"><svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi bi-eye" viewBox="0 0 16 16">\
            #                 <path d="M16 8s-3-5.5-8-5.5S0 8 0 8s3 5.5 8 5.5S16 8 16 8M1.173 8a13 13 0 0 1 1.66-2.043C4.12 4.668 5.88 3.5 8 3.5s3.879 1.168 5.168 2.457A13 13 0 0 1 14.828 8q-.086.13-.195.288c-.335.48-.83 1.12-1.465 1.755C11.879 11.332 10.119 12.5 8 12.5s-3.879-1.168-5.168-2.457A13 13 0 0 1 1.172 8z"/>\
            #                 <path d="M8 5.5a2.5 2.5 0 1 0 0 5 2.5 2.5 0 0 0 0-5M4.5 8a3.5 3.5 0 1 1 7 0 3.5 3.5 0 0 1-7 0"/>\
            #             </svg></a>\
            #             <a href="{edit_url}" title="Edit"><svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi bi-pen-fill" viewBox="0 0 16 16">\
            #                 <path d="m13.498.795.149-.149a1.207 1.207 0 1 1 1.707 1.708l-.149.148a1.5 1.5 0 0 1-.059 2.059L4.854 14.854a.5.5 0 0 1-.233.131l-4 1a.5.5 0 0 1-.606-.606l1-4a.5.5 0 0 1 .131-.232l9.642-9.642a.5.5 0 0 0-.642.056L6.854 4.854a.5.5 0 1 1-.708-.708L9.44.854A1.5 1.5 0 0 1 11.5.796a1.5 1.5 0 0 1 1.998-.001"/>\
            #             </svg></a>',

            #             '<a href="{content_url}" title="Content"><svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi bi-card-list" viewBox="0 0 16 16">\
            #                 <path d="M14.5 3a.5.5 0 0 1 .5.5v9a.5.5 0 0 1-.5.5h-13a.5.5 0 0 1-.5-.5v-9a.5.5 0 0 1 .5-.5zm-13-1A1.5 1.5 0 0 0 0 3.5v9A1.5 1.5 0 0 0 1.5 14h13a1.5 1.5 0 0 0 1.5-1.5v-9A1.5 1.5 0 0 0 14.5 2z"/>\
            #                 <path d="M5 8a.5.5 0 0 1 .5-.5h7a.5.5 0 0 1 0 1h-7A.5.5 0 0 1 5 8m0-2.5a.5.5 0 0 1 .5-.5h7a.5.5 0 0 1 0 1h-7a.5.5 0 0 1-.5-.5m0 5a.5.5 0 0 1 .5-.5h7a.5.5 0 0 1 0 1h-7a.5.5 0 0 1-.5-.5m-1-5a.5.5 0 1 1-1 0 .5.5 0 0 1 1 0M4 8a.5.5 0 1 1-1 0 .5.5 0 0 1 1 0m0 2.5a.5.5 0 1 1-1 0 .5.5 0 0 1 1 0"/>\
            #             </svg></a>',

            #             '<a href={delete_url}" title="Delete"><svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi bi-trash" viewBox="0 0 16 16">\
            #                 <path d="M5.5 5.5A.5.5 0 0 1 6 6v6a.5.5 0 0 1-1 0V6a.5.5 0 0 1 .5-.5m2.5 0a.5.5 0 0 1 .5.5v6a.5.5 0 0 1-1 0V6a.5.5 0 0 1 .5-.5m3 .5a.5.5 0 0 0-1 0v6a.5.5 0 0 0 1 0z"/>\
            #                 <path d="M14.5 3a1 1 0 0 1-1 1H13v9a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V4h-.5a1 1 0 0 1-1-1V2a1 1 0 0 1 1-1H6a1 1 0 0 1 1-1h2a1 1 0 0 1 1 1h3.5a1 1 0 0 1 1 1zM4.118 4 4 4.059V13a1 1 0 0 0 1 1h6a1 1 0 0 0 1-1V4.059L11.882 4zM2.5 3h11V2h-11z"/>\
            #             </svg></a>\
            #         </span>']
            html_links = ['<span><a href="{view_url}" title="View"><i class="bi bi-eye"></a>\n\
                            <a href="{edit_url}" title="Edit"><i class="bi bi-pen-fill"></a>\n',
                            '<a href="{content_url}" title="Content"><i class="bi bi-card-list"></i></a>\n',
                            '<a href="{delete_url}" title="Delete"><i class="bi bi-trash"></i></a></span>'
                         ]

            tools = html_links[0].format(view_url=get_view_url(child_object), edit_url=get_edit_url(child_object))
            if has_content(child_object):
                tools += html_links[1].format(content_url=get_content_url(child_object))
            tools += html_links[2].format(delete_url=get_delete_url(child_object))

            child_schema = self.add_option_to_schema(child_schema, {'preHtml': tools})
        return child_schema

    def add_dependencies_to_schema(self, child_schema, child_object):
        # add showOn dependencies
        if child_object.dependencies:
            showOn = create_showon_properties(child_object, self.lookup_scopes)
            if showOn != {}:
                child_schema['showOn'] = showOn
        return child_schema

    def add_option_to_schema(self, child_schema, options: dict):
        if 'options' not in child_schema:
            child_schema['options'] = options
        else:
            for key, value in options.items():
                child_schema['options'][key] = value
        return child_schema



    # ????????
    def get_schema_for_fieldset(self, fieldset, scope, recursive=True):
        # save scope in lookup_scopes
        # fieldset_id = create_id(fieldset)
        # fieldset_scope = scope + fieldset_id
        # self.lookup_scopes[fieldset_id] = fieldset_scope

        return self.create_group(fieldset, scope, recursive)


    def get_base_schema(self, child, scope, save_scope=True, has_user_helptext=True):
        child_id = create_id(child)
        child_scope = scope + child_id
        base_schema = {
            'type': 'Control',
            'scope': child_scope,
        }

        if save_scope:
            self.lookup_scopes[child_id] = child_scope

        if has_user_helptext:
            user_helptext = get_user_helptext(child, self.request)
            if user_helptext:
                base_schema = self.add_option_to_schema(base_schema, {'help': {'text': user_helptext}})

        base_schema = self.add_tools_to_schema(base_schema, child)
        base_schema = self.add_dependencies_to_schema(base_schema, child)
        base_schema = self.add_option_to_schema(base_schema, {})

        return base_schema

    def add_user_info(self, child, child_schema):
        pass
    #     # TODO comes with ui-schema version 3.1
    #     if child.user_info:
    #         self.add_option_to_schema(child_schema, {'helptext': child.user_info})

    def create_group(self, group, scope, recursive):
        group_schema = {
            'type': 'Group',
        }
        if group.show_title:
            group_schema = self.add_option_to_schema(group_schema, {'label': get_title(group, self.request)})

        group_schema = self.add_tools_to_schema(group_schema, group)
        group_schema = self.add_dependencies_to_schema(group_schema, group)

        if recursive:
            group_schema['elements'] = []

            children = group.getFolderContents()
            for child in children:
                child_object = child.getObject()
                if not check_show_condition_in_request(self.request, child_object.show_condition, child_object.negate_condition):
                    continue

                child_schema = self.get_schema_for_child(child_object, scope)
                if child_schema != None and child_schema != {}:
                    child_schema = self.add_tools_to_schema(child_schema, child_object)
                    group_schema['elements'].append(child_schema)

        return group_schema
