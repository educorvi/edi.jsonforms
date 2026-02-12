# -*- coding: utf-8 -*-

from copy import deepcopy
from urllib.parse import urlencode
from edi.jsonforms import _
from Products.Five.browser import BrowserView
import json

from edi.jsonforms.views.common import *
from edi.jsonforms.views.showOn_properties import create_showon_properties
from edi.jsonforms.content.option_list import get_keys_and_values_for_options_list

from plone.base.utils import safe_hasattr

from edi.jsonforms.views.common import get_option_name


class UiSchemaView(BrowserView):
    tools_on = False
    rita_dependent_options = {}
    is_single_view = False

    def __init__(self, context, request):
        super().__init__(context, request)
        self.uischema = {}

        # needed to put scopes in showOn-properties without having to compute them
        self.lookup_scopes = {}

        self.rita_dependent_options = {}

    def __call__(self):
        self.get_schema()
        return json.dumps(self.uischema, ensure_ascii=False, indent=4)

    def set_tools(self, tools_on):
        self.tools_on = tools_on

    def get_schema(self):
        self.set_ui_base_schema()

        form = self.context
        children = form.getFolderContents()
        for child in children:
            self.add_child_to_schema(child.getObject(), self.uischema)

        return self.uischema

    def set_ui_base_schema(self):
        self.uischema = {}
        self.lookup_scopes = {}

        self.uischema = {
            "version": "2.0",
            "layout": {"type": "VerticalLayout", "elements": []},
        }

    def add_child_to_schema(self, child_object, schema, scope="/properties/"):
        """
        schema needs the key 'elements' or 'layout' with the key 'elements'
        """
        if (
            child_object.portal_type != "Button Handler"
            and not check_show_condition_in_request(
                self.request, child_object.show_condition, child_object.negate_condition
            )
        ):
            return schema

        # add children to the schema
        child_schema = self.get_schema_for_child(child_object, scope)
        if child_schema != None and child_schema != {}:
            if "layout" in schema:
                schema["layout"]["elements"].append(child_schema)
            elif "elements" in schema:
                schema["elements"].append(child_schema)
            else:
                print(
                    "Error in UiSchemaView: could not add child to schema, no layout or elements found in schema"
                )

        # return schema

    def get_schema_for_child(self, child, scope, recursive=True, overwrite_scope=None):
        type = child.portal_type
        child_schema = {}

        if type == "Field":
            child_schema = self.get_schema_for_field(child, scope)
        elif type == "SelectionField":
            child_schema = self.get_schema_for_selectionfield(child, scope)
        elif type == "UploadField":
            child_schema = self.get_schema_for_uploadfield(child, scope)
        elif type == "Reference":
            child_schema = self.get_schema_for_reference(child, scope)
        elif type == "Helptext":
            child_schema = self.get_schema_for_helptext(child)
        elif type == "Button Handler":
            child_schema = self.get_schema_for_buttons(child)
        elif type == "Array":
            child_schema = self.get_schema_for_array(
                child, scope, recursive, overwrite_scope
            )
        elif type == "Complex":
            child_schema = self.get_schema_for_object(
                child, scope, recursive, overwrite_scope
            )
        elif type == "Fieldset":
            child_schema = self.get_schema_for_fieldset(child, scope)

        # add pre_html and post_html to the schema
        if hasattr(child, "pre_html") and child.pre_html is not None:
            existing_pre = child_schema["options"].get("preHtml")
            if existing_pre:
                child_schema["options"]["preHtml"] = (
                    f"{existing_pre}<br>{child.pre_html.output}"
                )
            else:
                child_schema["options"]["preHtml"] = child.pre_html.output
        if hasattr(child, "post_html") and child.post_html is not None:
            child_schema["options"]["postHtml"] = child.post_html.output

        return child_schema

    def get_schema_for_field(self, field, scope):
        field_schema = self.get_base_schema(field, scope)

        answer_type = field.answer_type
        if answer_type == "text":
            pass
        elif answer_type == "textarea":
            field_schema["options"]["multi"] = True
        elif answer_type == "password":
            field_schema["options"]["format"] = "password"
        elif answer_type == "tel":
            field_schema["options"]["format"] = "tel"
        elif answer_type == "url":
            field_schema["options"]["format"] = "url"
        elif answer_type == "email":
            field_schema["options"]["format"] = "email"
        elif answer_type == "date":
            field_schema["options"]["format"] = "date"
        elif answer_type == "datetime-local":
            field_schema["options"]["format"] = "datetime-local"
        elif answer_type == "time":
            field_schema["options"]["format"] = "time"
        elif answer_type in ["number", "integer"]:
            unit = get_unit(field, self.request)
            if unit:
                field_schema["options"]["append"] = unit
        elif answer_type == "boolean":
            pass
            # TODO

        placeholder = get_placeholder(field, self.request)
        if placeholder and field.answer_type in [
            "text",
            "textarea",
            "password",
            "tel",
            "url",
            "email",
        ]:
            field_schema["options"]["placeholder"] = placeholder

        # remove unnecessary options
        if field_schema["options"] == {}:
            del field_schema["options"]

        return field_schema

    def get_schema_for_selectionfield(self, selectionfield, scope):
        selectionfield_schema = self.get_base_schema(selectionfield, scope)

        answer_type = selectionfield.answer_type
        if answer_type == "radio":
            selectionfield_schema["options"]["displayAs"] = "radiobuttons"
            selectionfield_schema["options"]["stacked"] = True
        elif answer_type in ["checkbox", "selectmultiple"]:
            # TODO differentiate between checkbox and selectmultiple, both are displayed as checkboxes
            selectionfield_schema["options"]["stacked"] = True
        elif answer_type == "select":
            pass

        if selectionfield.use_id_in_schema:
            selectionfield_schema["options"]["enumTitles"] = {}
            for option in selectionfield.getFolderContents():
                if option.portal_type == "Option":
                    selectionfield_schema["options"]["enumTitles"][
                        create_id(option)
                    ] = option.Title
                elif option.portal_type == "OptionList":
                    keys, vals = get_keys_and_values_for_options_list(
                        option.getObject()
                    )
                    selectionfield_schema["options"]["enumTitles"].update(
                        dict(zip(keys, vals))
                    )

        option_filters = {}
        options = selectionfield.getFolderContents()
        for option in options:
            o = option.getObject()
            if safe_hasattr(o, "ritarules"):
                if o.ritarules != "" and o.ritarules is not None:
                    try:
                        formatted_rita_rule = json.loads(o.ritarules)
                        option_filters[get_option_name(o)] = formatted_rita_rule
                    except (json.JSONDecodeError, TypeError, ValueError):
                        print(f"Invalid rita rule for option {get_option_name(o)}")
                        pass
        if len(option_filters) > 0:
            selectionfield_schema["options"]["optionFilters"] = option_filters
            self.rita_dependent_options[scope + selectionfield.id] = option_filters

        if selectionfield_schema["options"] == {}:
            del selectionfield_schema["options"]

        return selectionfield_schema

    def get_schema_for_uploadfield(self, uploadfield, scope):
        uploadfield_schema = self.get_base_schema(uploadfield, scope)

        if uploadfield.accepted_file_types:
            uploadfield_schema["options"]["acceptedFileType"] = (
                uploadfield.accepted_file_types
            )
        else:
            uploadfield_schema["options"]["acceptedFileType"] = "*"

        if uploadfield.max_file_size:
            uploadfield_schema["options"]["maxFileSize"] = (
                uploadfield.max_file_size * 1024 * 1024
            )  # in bytes

        if uploadfield.display_as_array:
            uploadfield_schema["options"]["displayAsSingleUploadField"] = False
        else:
            uploadfield_schema["options"]["displayAsSingleUploadField"] = True
        # if uploadfield.max_number_of_files:
        #     uploadfield_schema['options']['maxNumberOfFiles'] = uploadfield.max_number_of_files
        # if uploadfield.min_number_of_files:
        #     uploadfield_schema['options']['minNumberOfFiles'] = uploadfield.min_number_of_files

        #     if uploadfield.min_number_of_files > 1:
        #         uploadfield_schema['options']['allowMultipleFiles'] = True

        # if uploadfield.answer_type == 'file-multi':
        #     uploadfield_schema['options']['allowMultipleFiles'] = True

        return uploadfield_schema

    def get_schema_for_reference(self, reference, scope):
        try:
            obj = reference.reference.to_object
            if obj:
                reference_schema = self.get_base_schema(
                    reference, scope, has_user_helptext=False
                )
                tools = self.tools_on
                self.set_tools(
                    False
                )  # to deactivate tools for children of referenced object
                obj_schema = self.get_schema_for_child(
                    obj, scope, overwrite_scope=reference_schema["scope"]
                )
                self.set_tools(tools)  # reactivate tools

                # replace scope and showon of referenced object with the one of the reference
                obj_schema["scope"] = reference_schema["scope"]
                if "showOn" in reference_schema:
                    obj_schema["showOn"] = reference_schema["showOn"]
                elif "showOn" in obj_schema:
                    del obj_schema["showOn"]

                self.add_tools_to_schema(obj_schema, reference)
                if self.tools_on:
                    obj_schema["options"]["preHtml"] = (
                        '<i class="bi bi-arrow-90deg-left"></i> \n '
                        + obj_schema["options"]["preHtml"]
                    )
                    self.add_option_to_schema(
                        obj_schema, {"help": {"text": _("This is a reference.")}}
                    )

                return obj_schema
        except:
            return {}  # referenced object got deleted, ignore

    def helptext_schema(self, htmlData):
        # helptext as html-element
        helptext_schema = {
            "type": "HTML",
            "htmlData": htmlData,
        }
        return helptext_schema

    def get_schema_for_helptext(self, helptext):
        # helptext as html-element
        text = ""
        if self.tools_on:
            text += f"{self.get_tools_html(helptext)}\n"
        if safe_hasattr(helptext.helptext, "output"):
            text += str(helptext.helptext.output)

        helptext_schema = self.helptext_schema(text)
        helptext_schema = self.add_dependencies_to_schema(helptext_schema, helptext)
        return helptext_schema

    def get_schema_for_buttons(self, button_handler):
        request_button_schema = {
            "type": "Button",
            "buttonType": "submit",
            "text": "",  # FILL
            "options": {
                "variant": "primary",
                "submitOptions": {
                    "action": "request",
                    "request": {
                        "url": "",  # FILL
                        "method": "POST",
                        "headers": {
                            "Accept": "application/json",
                            "Content-Type": "application/json",
                        },
                        "onSuccessRedirect": "",
                    },
                },
            },
        }

        buttons = button_handler.getFolderContents()
        if len(buttons) == 0:
            return {}

        buttons_schema = {"type": "Buttongroup", "buttons": []}

        for button in buttons:
            button = button.getObject()

            if button.portal_type == "Email Handler":
                request_url = self.context.absolute_url() + "/@send-email"

                query_params = {"to_address": button.to_address}

                if button.reply_to_address:
                    query_params["reply_to_address"] = button.reply_to_address
                if button.email_subject:
                    query_params["subject"] = button.email_subject
                if button.email_text:
                    query_params["email_text"] = button.email_text

                # Encode the query parameters
                encoded_query = urlencode(query_params)

                # Combine the base URL with the encoded query parameters
                request_url = f"{request_url}?{encoded_query}"

                button_schema = request_button_schema.copy()
                button_schema["text"] = button.button_label
                button_schema["options"]["submitOptions"]["request"]["url"] = (
                    request_url
                )
                if (
                    safe_hasattr(button, "page_after_success")
                    and button.page_after_success
                ):
                    button_schema["options"]["submitOptions"]["request"][
                        "onSuccessRedirect"
                    ] = button.page_after_success

                button_schema["options"]["variant"] = button.button_variant

                buttons_schema["buttons"].append(button_schema)
            elif button.portal_type == "Reset Button":
                button_schema = {
                    "type": "Button",
                    "buttonType": "reset",
                    "text": button.button_label,
                    "options": {"variant": "danger"},
                }
                button_schema["options"]["variant"] = button.button_variant
                buttons_schema["buttons"].append(button_schema)
            elif button.portal_type == "Webservice Handler":
                request_url = self.context.absolute_url() + "/@webservice-request"
                i = 1
                query_params = {}
                endpoints = button.getFolderContents()
                for endpoint in endpoints:
                    endpoint = endpoint.getObject()
                    if endpoint.portal_type == "Endpoint":
                        query_params[f"endpoint_{i}_url"] = endpoint.url
                        if endpoint.api_key_header_name and endpoint.api_key:
                            query_params[f"endpoint_{i}_api_key_header_name"] = (
                                endpoint.api_key_header_name
                            )
                            query_params[f"endpoint_{i}_api_key"] = endpoint.api_key
                    i += 1

                if button.page_after_success:
                    query_params["page_after_success"] = button.page_after_success
                encoded_query = urlencode(query_params)
                request_url = f"{request_url}?{encoded_query}"

                button_schema = deepcopy(request_button_schema)
                button_schema["text"] = button.button_label
                button_schema["options"]["submitOptions"]["request"]["url"] = (
                    request_url
                )
                button_schema["options"]["submitOptions"]["request"][
                    "onSuccessRedirect"
                ] = button.page_after_success

                button_schema["options"]["variant"] = button.button_variant

                buttons_schema["buttons"].append(button_schema)

        return buttons_schema

    def get_schema_for_array(self, array, scope, recursive=True, overwrite_scope=None):
        array_schema = self.get_schema_for_object(
            array, scope, recursive, overwrite_scope
        )

        if not array.show_title:
            self.add_option_to_schema(array_schema, {"label": False})

        if array.button_label:
            self.add_option_to_schema(
                array_schema, {"addButtonText": array.button_label}
            )

        return array_schema
        # # don't save scope because one cannot depend on an array
        # array_schema = self.get_base_schema(array, scope, save_scope=False, has_user_helptext=False)
        # if overwrite_scope:
        #     array_scope = overwrite_scope
        # else:
        #     array_scope = scope + create_id(array)

        # # add children of array to the schema
        # if recursive:
        #     array_schema['options']['descendantControlOverrides'] = self.create_descendantControlOverrides(array_scope, array)

        # self.add_user_info(array, array_schema)

        # # array_schema['options']['label'] = False

        # if array_schema['options'] == {}:
        #     del array_schema['options']

        # return array_schema

    def get_schema_for_object(
        self, complex, scope, recursive=True, overwrite_scope=None
    ):
        # don't save scope because one cannot depend on a complex object
        complex_schema = self.get_base_schema(
            complex, scope, save_scope=False, has_user_helptext=False
        )
        if overwrite_scope:
            complex_scope = overwrite_scope
        else:
            complex_scope = scope + create_id(complex)

        # add children of complex to the schema
        if recursive:
            complex_schema["options"]["descendantControlOverrides"] = (
                self.create_descendantControlOverrides(complex_scope, complex)
            )

        self.add_user_helptext(complex, complex_schema)

        if complex_schema["options"] == {}:
            del complex_schema["options"]

        return complex_schema

    def add_child_to_descendantControlOverrides(
        self, descendantControlOverrides, child_object, base_scope
    ):
        child_tmp_schema = {}

        # add options and showon to the descendantControlOverrides
        if child_object.portal_type in [
            "Field",
            "SelectionField",
            "UploadField",
            "Complex",
            "Array",
        ]:
            # descendantControlOverrides = add_control(descendantControlOverrides, child_object, scope)
            child_tmp_schema = self.get_schema_for_child(
                child_object, base_scope, False
            )
            if (
                child_object.portal_type == "UploadField"
                and child_object.display_as_array
            ):
                child_tmp_schema["scope"] += "/items"

            child_schema = {}
            if "options" in child_tmp_schema:
                child_schema["options"] = child_tmp_schema["options"]
            if "showOn" in child_tmp_schema:
                child_schema["showOn"] = child_tmp_schema["showOn"]

            if child_schema != {}:
                descendantControlOverrides[child_tmp_schema["scope"]] = child_schema
        else:  # ignore this type
            pass

        # add it recursively if child_object is a container type
        if child_object.portal_type in ["Complex", "Array"]:
            container_base_scope = child_tmp_schema["scope"]
            if child_object.portal_type == "Array":
                container_base_scope += "/items/properties/"
            elif child_object.portal_type == "Complex":
                container_base_scope += "/properties/"
            for c in child_object.getFolderContents():
                c_object = c.getObject()
                if not check_show_condition_in_request(
                    self.request, c_object.show_condition, c_object.negate_condition
                ):
                    continue
                descendantControlOverrides = (
                    self.add_child_to_descendantControlOverrides(
                        descendantControlOverrides, c_object, container_base_scope
                    )
                )

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
            if not check_show_condition_in_request(
                self.request, child_object.show_condition, child_object.negate_condition
            ):
                continue
            descendantControlOverrides = self.add_child_to_descendantControlOverrides(
                descendantControlOverrides, child_object, base_scope
            )

        return descendantControlOverrides

    def get_tools_html(self, child_object):
        aria_view = _("View element")
        aria_edit = _("Edit element")
        aria_content = _("Show element content")
        aria_delete = _("Delete element")

        html_links = [
            '<span><a aria-label="{aria_view}" href="{view_url}" title="{view}"><i class="bi bi-eye"></a>\n\
                        <a aria-label="{aria_edit}" href="{edit_url}" title="{edit}"><i class="bi bi-pen-fill"></a>\n',
            '<a aria-label="{aria_content}" href="{content_url}" title="{content}"><i class="bi bi-card-list"></i></a>\n',
            '<a aria-label="{aria_delete}" href="{delete_url}" title="{delete}"><i class="bi bi-trash"></i></a></span>',
        ]

        tools = html_links[0].format(
            aria_view=aria_view,
            view_url=get_view_url(child_object),
            view=_("View"),
            aria_edit=aria_edit,
            edit_url=get_edit_url(child_object),
            edit=_("Edit"),
        )
        if has_content(child_object):
            tools += html_links[1].format(
                aria_content=aria_content,
                content_url=get_content_url(child_object),
                content=_("Content"),
            )
        tools += html_links[2].format(
            aria_delete=aria_delete,
            delete_url=get_delete_url(child_object),
            delete=_("Delete"),
        )
        return tools

    def add_tools_to_schema(self, child_schema, child_object):
        if self.tools_on:
            tools = self.get_tools_html(child_object)
            child_schema = self.add_option_to_schema(child_schema, {"preHtml": tools})
        return child_schema

    def add_dependencies_to_schema(self, child_schema, child_object):
        if self.is_single_view:
            return child_schema
        # add showOn dependencies
        if child_object.dependencies:
            showOn = create_showon_properties(child_object, self.lookup_scopes)
            if showOn != {}:
                child_schema["showOn"] = showOn
        return child_schema

    def add_option_to_schema(self, child_schema, options: dict):
        if "options" not in child_schema:
            child_schema["options"] = options
        else:
            for key, value in options.items():
                child_schema["options"][key] = value
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
            "type": "Control",
            "scope": child_scope,
        }

        if save_scope:
            self.lookup_scopes[child_id] = child_scope

        if has_user_helptext:
            self.add_user_helptext(child, base_schema)

        base_schema = self.add_tools_to_schema(base_schema, child)
        base_schema = self.add_dependencies_to_schema(base_schema, child)
        base_schema = self.add_option_to_schema(base_schema, {})

        return base_schema

    def add_user_helptext(self, child, child_schema):
        user_helptext = get_user_helptext(child, self.request)
        if user_helptext:
            child_schema = self.add_option_to_schema(
                child_schema, {"help": {"text": user_helptext}}
            )

    def create_group(self, group, scope, recursive):
        group_schema = {
            "type": "Group",
        }
        if group.show_title:
            group_schema = self.add_option_to_schema(
                group_schema, {"label": get_title(group, self.request)}
            )
        if group.description is not None:
            group_schema = self.add_option_to_schema(
                group_schema, {"description": group.description}
            )

        # group_schema = self.add_tools_to_schema(group_schema, group) # gets ignored, add html element before group instead
        group_schema = self.add_dependencies_to_schema(group_schema, group)

        if self.tools_on and group.aq_parent.portal_type == "Form":
            helptext_schema = self.helptext_schema(self.get_tools_html(group))
            helptext_schema = self.add_dependencies_to_schema(
                helptext_schema, group
            )  # helptext has same showOn as group
            self.uischema["layout"]["elements"].append(helptext_schema)

        if recursive:
            group_schema["elements"] = []

            children = group.getFolderContents()
            for child in children:
                child_object = child.getObject()
                if not check_show_condition_in_request(
                    self.request,
                    child_object.show_condition,
                    child_object.negate_condition,
                ):
                    continue

                if self.tools_on and child_object.portal_type == "Fieldset":
                    helptext_schema = self.helptext_schema(
                        self.get_tools_html(child_object)
                    )
                    helptext_schema = self.add_dependencies_to_schema(
                        helptext_schema, child_object
                    )
                    group_schema["elements"].append(helptext_schema)
                self.add_child_to_schema(child_object, group_schema, scope)

        return group_schema
