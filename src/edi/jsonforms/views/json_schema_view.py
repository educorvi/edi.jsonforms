# -*- coding: utf-8 -*-

from Products.Five.browser import BrowserView

import copy
import itertools
import json

from edi.jsonforms.views.common import *

from edi.jsonforms.content.option_list import get_keys_and_values_for_options_list


class JsonSchemaView(BrowserView):
    is_extended_schema = False  # True if schema is generated for an api call and not for the usual form view
    content_types_without_schema = ["Helptext", "Button Handler"]

    def __init__(self, context, request):
        super().__init__(context, request)
        self.jsonschema = {}
        self.ids = set()

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
            self.add_child_to_schema(child.getObject(), self.jsonschema)

        return self.jsonschema

    def set_json_base_schema(self):
        self.jsonschema = {"type": "object"}
        self.jsonschema["properties"] = {}
        self.jsonschema["required"] = []
        self.jsonschema["dependentRequired"] = {}
        self.jsonschema["allOf"] = []
        self.ids = set()

    def add_child_to_schema(self, child_object, schema):
        """
        schema needs the keys 'properties' and 'required'
        """
        if (
            child_object.portal_type in self.content_types_without_schema
            or not check_show_condition_in_request(
                self.request, child_object.show_condition, child_object.negate_condition
            )
        ):
            return
        child_id = self.create_and_check_id(child_object)

        # add children to the schema
        if child_object.portal_type == "Fieldset":
            schema = self.modify_schema_for_fieldset(schema, child_object)
        elif "properties" in schema:
            schema["properties"][child_id] = self.get_schema_for_child(child_object)
        else:
            print(
                "Error in JsonSchemaView: could not add child to schema, no 'properties' found in schema"
            )
            return

        # mark children as required
        if (
            child_object.portal_type in possibly_required_types
            and child_object.required_choice == "required"
        ):
            if check_for_dependencies(child_object):
                schema = self.add_dependent_required(schema, child_object, child_id)
            elif "required" in schema:
                schema["required"].append(child_id)
            else:
                print(
                    "Error in JsonSchemaView: could not add requirements of child to schema, no 'required' found in schema"
                )
                return

        # handle dependencies for Option content type
        if child_object.portal_type == "SelectionField":
            schema["allOf"].extend(self.get_dependent_options(child_object))

    def modify_schema_for_fieldset(self, schema, fieldset):
        children = fieldset.getFolderContents()
        for child in children:
            child_object = child.getObject()
            self.add_child_to_schema(child_object, schema)
        return schema

    def get_schema_for_child(self, child):
        type = child.portal_type

        if type == "Field":
            return self.get_schema_for_field(child)
        elif type == "SelectionField":
            return self.get_schema_for_selectionfield(child)
        elif type == "UploadField":
            return self.get_schema_for_uploadfield(child)
        elif type == "Reference":
            return self.get_schema_for_reference(child)
        elif type == "Array":
            return self.get_schema_for_array(child)
        elif type == "Complex":
            return self.get_schema_for_object(child)
        return {}

    def get_schema_for_field(self, field):
        field_schema = self.create_base_schema__field({}, field)
        answer_type = field.answer_type
        if answer_type in ["text", "textarea", "password"]:
            field_schema["type"] = "string"
            if field.minimum:
                field_schema["minLength"] = field.minimum
            if field.maximum:
                field_schema["maxLength"] = field.maximum
        elif answer_type == "tel":
            field_schema["type"] = "string"
            field_schema["pattern"] = (
                "^\+?(\d{1,3})?[-.\s]?(\(?\d{1,4}\)?)?[-.\s]?\d{1,4}[-.\s]?\d{1,4}[-.\s]?\d{1,9}$"
            )
            # or simply '^[\d+\-()\s]{1,25}$' (max 25 symbols, +, -, (, ), numbers and space are allowed
        elif answer_type == "url":
            field_schema["type"] = "string"
            field_schema["format"] = "hostname"
        elif answer_type == "email":
            field_schema["type"] = "string"
            field_schema["format"] = "email"
        elif answer_type == "date":
            field_schema["type"] = "string"
            field_schema["format"] = "date"
        elif answer_type == "datetime-local":
            field_schema["type"] = "string"
            field_schema["format"] = "date-time"
        elif answer_type == "time":
            field_schema["type"] = "string"
            field_schema["format"] = "time"
        elif answer_type == "number":
            field_schema["type"] = "number"
        elif answer_type == "integer":
            field_schema["type"] = "integer"
        elif answer_type == "boolean":
            field_schema["type"] = "boolean"

        if answer_type in ["number", "integer"]:
            if field.minimum:
                field_schema["minimum"] = field.minimum
            if field.maximum:
                field_schema["maximum"] = field.maximum
        return field_schema

    def get_schema_for_selectionfield(self, selectionfield):
        selectionfield_schema = self.create_base_schema__field({}, selectionfield)
        answer_type = selectionfield.answer_type
        options = selectionfield.getFolderContents()

        options_list = []
        for o in options:
            if o.portal_type == "Option":
                o = o.getObject()
                if not check_for_dependencies(o):
                    options_list.append(self.get_option_name(o))
                # dependencies of options are handled in add_child_to_schema
            elif o.portal_type == "OptionList":
                keys, vals = get_keys_and_values_for_options_list(o.getObject())
                if selectionfield.use_id_in_schema:
                    local_options_list = keys
                else:
                    local_options_list = vals
                options_list.extend(local_options_list)

        if answer_type == "radio" or answer_type == "select":
            selectionfield_schema["type"] = "string"
            selectionfield_schema["enum"] = options_list
        elif answer_type == "checkbox" or answer_type == "selectmultiple":
            selectionfield_schema["type"] = "array"
            selectionfield_schema["items"] = {"enum": options_list, "type": "string"}
        return selectionfield_schema

    def get_schema_for_uploadfield(self, uploadfield):
        uploadfield_schema = self.create_base_schema__field({}, uploadfield)
        # answer_type = uploadfield.answer_type

        uploadfield_schema["minItems"] = uploadfield.min_number_of_files

        if uploadfield.max_number_of_files:
            if uploadfield.max_number_of_files == 1:
                uploadfield_schema["type"] = "string"
                uploadfield_schema["format"] = "uri"
            else:
                uploadfield_schema["type"] = "array"
                uploadfield_schema["items"] = {
                    "type": "string",
                    "format": "uri",
                }
                uploadfield_schema["maxItems"] = uploadfield.max_number_of_files
        else:
            uploadfield_schema["type"] = "array"
            uploadfield_schema["items"] = {
                "type": "string",
                "format": "uri",
            }

        return uploadfield_schema

    def get_schema_for_reference(self, reference):
        try:
            obj = reference.reference.to_object
            if obj:
                obj_schema = self.get_schema_for_child(obj)
                return obj_schema
        except:  # referenced object got deleted, ignore
            return {}

    def get_schema_for_array(self, array):
        array_schema = self.add_title_and_description({"type": "array"}, array)
        array_schema = add_interninformation(array_schema, array)
        if array.required_choice == "required":
            array_schema["minItems"] = 1
        array_schema["items"] = self.get_schema_for_object(array)
        return array_schema

    def get_schema_for_object(self, object):
        complex_schema = {}
        complex_schema["type"] = "object"
        if object.portal_type != "Array":
            complex_schema = self.add_title_and_description(complex_schema, object)
            complex_schema = add_interninformation(complex_schema, object)
        complex_schema["properties"] = {}
        complex_schema["required"] = []
        complex_schema["dependentRequired"] = {}
        complex_schema["allOf"] = []

        children = object.getFolderContents()
        for child in children:
            child_object = child.getObject()
            self.add_child_to_schema(child_object, complex_schema)

        return complex_schema

    def add_dependent_required(self, schema, child_object, child_id):
        dependencies = child_object.dependencies

        # copy 'allOf' and 'dependentRequired' to check that at least one of them changed
        schema_allof_copy = copy.deepcopy(schema["allOf"])
        schema_dependentrequired_copy = copy.deepcopy(schema["dependentRequired"])

        for dep in dependencies:
            try:
                dep = dep.to_object
                if dep.portal_type == "Option":
                    dep_id = self.get_option_name(dep)
                    selection_parent = dep.aq_parent
                    if_then = {
                        "if": {
                            "properties": {
                                create_id(selection_parent): {"const": dep_id}
                            }
                        },
                        "then": {"required": [child_id]},
                    }

                    if self.is_extended_schema:
                        if_then["else"] = create_else_statement(child_object)
                    # if 'allOf' in schema:
                    #     schema['allOf'].append(if_then)
                    # else:
                    #     schema['allOf'] = [if_then]
                    schema["allOf"].append(if_then)
                else:
                    dep_id = create_id(dep)
                    if dep_id in schema["dependentRequired"]:
                        schema["dependentRequired"][dep_id].append(child_id)
                    else:
                        schema["dependentRequired"][dep_id] = [child_id]
            except:
                # dependency got deleted, plone error, ignore this dependency
                continue

        # Check that at least one dependency wasn't deleted so that 'allOf' and/or 'dependentRequired' changed.
        # Otherwise add child_object to required-list of the schema, because it is required and not dependent required, if it has no valid dependencies anymore
        if (
            schema_allof_copy == schema["allOf"]
            and schema_dependentrequired_copy == schema["dependentRequired"]
        ):
            schema["required"].append(child_id)
        return schema

    def get_dependent_options(self, parent_object):
        """
        parent_object: SelectionField
        """

        def add_to_dict(option, dependency, dict):
            parent_key = "SHOWALWAYS"
            if dependency:
                parent_key = create_id(dependency.aq_parent)
                dependency_key = self.get_option_name(dependency)
                option_value = self.get_option_name(option)

                answer_type = (
                    "multi"
                    if dependency.aq_parent.answer_type
                    in ["checkbox", "selectmultiple"]
                    else "single"
                )

                parent_key = f"{answer_type}_{parent_key}"
                if parent_key in dict:
                    if dependency_key in dict[parent_key]:
                        dict[parent_key][dependency_key].append(option_value)
                    else:
                        dict[parent_key][dependency_key] = [option_value]
                else:
                    dict[parent_key] = {}
                    dict[parent_key][dependency_key] = [option_value]
            else:
                dict["SHOWALWAYS"].append(self.get_option_name(option))

        allof_list = []
        options = parent_object.getFolderContents()
        parent_object_id = create_id(parent_object)
        dependency_dict = {"SHOWALWAYS": []}
        for option in options:
            if option.portal_type == "Option":
                option = option.getObject()
                if check_for_dependencies(option):
                    dependencies = option.dependencies
                    for dep in dependencies:
                        try:
                            add_to_dict(option, dep.to_object, dependency_dict)
                        except:
                            # dependency got deleted, plone error, ignore this dependency
                            continue

                else:
                    add_to_dict(option, None, dependency_dict)

        if dependency_dict["SHOWALWAYS"]:
            showalways_list = [entry for entry in dependency_dict["SHOWALWAYS"]]
        else:
            showalways_list = []

        possibilities = []

        for selectionfield_id in dependency_dict:
            if selectionfield_id == "SHOWALWAYS":
                continue
            if selectionfield_id.startswith("multi_"):
                # possibilities.append([[(selectionfield_id, None)], [selectionfield_id]])
                subsets = []
                for r in range(len(dependency_dict[selectionfield_id]) + 1):
                    subsets.extend(
                        itertools.combinations(dependency_dict[selectionfield_id], r)
                    )
                possibilities.append(
                    [list((selectionfield_id, sub)) for sub in subsets]
                )
            else:
                possibilities.append(
                    [[selectionfield_id, None]]
                    + [
                        [selectionfield_id, option_id]
                        for option_id in dependency_dict[selectionfield_id]
                    ]
                )
        if possibilities:
            all_combinations = list(itertools.product(*possibilities))
        else:
            return []

        for combination in all_combinations:
            if_dict = {"properties": {}, "required": []}
            then_enum = dependency_dict["SHOWALWAYS"][:]
            for sublist in combination:
                if sublist[1] is None or sublist[1] == ():
                    continue
                selectionfield_id = sublist[0]
                selectionfield_id_clean = selectionfield_id.replace(
                    "multi_", ""
                ).replace("single_", "")

                if selectionfield_id.startswith("multi_"):
                    if_dict["properties"][selectionfield_id_clean] = {
                        "contains": {"enum": [o for o in sublist[1]]}
                    }
                    for o in sublist[1]:
                        then_enum.extend(dependency_dict[selectionfield_id][o])
                else:
                    if_dict["properties"][selectionfield_id_clean] = {
                        "const": sublist[1]
                    }
                    then_enum.extend(dependency_dict[selectionfield_id][sublist[1]])
                if_dict["required"].append(selectionfield_id_clean)
            if len(then_enum) > len(dependency_dict["SHOWALWAYS"]):
                if selectionfield_id.startswith("multi_"):
                    then_enum = {"items": {"enum": list(set(then_enum))}}
                else:
                    then_enum = {"enum": list(set(then_enum))}
                allof_list.append(
                    {
                        "if": if_dict,
                        "then": {"properties": {parent_object_id: then_enum}},
                    }
                )
        return allof_list

    # left over of duplicate check. method not deleted in case of other stuff with ids in the future
    def create_and_check_id(self, object):
        id = create_id(object)
        if id not in self.ids:
            self.ids.add(id)
        return id

    def get_option_name(self, option):
        parent_selectionfield = option.aq_parent
        if parent_selectionfield.use_id_in_schema:
            return create_id(option)
        else:
            return option.title

    """
    create base schema for a field, selectionfield or an uploadfield
    """

    def create_base_schema__field(self, schema, child):
        base_schema = self.add_title_and_description(schema, child)
        # base_schema = add_userhelptext(base_schema, child)
        base_schema = add_interninformation(base_schema, child)
        return base_schema

    def add_title_and_description(self, schema, child):
        schema["title"] = get_title(child, self.request)
        description = get_description(child, self.request)
        if description:
            schema["description"] = description

        return schema


def check_for_dependencies(child_object):
    if child_object.dependencies is not None and child_object.dependencies != []:
        return True
    else:
        return False


def add_interninformation(schema, child):
    if hasattr(child, "intern_information") and child.intern_information:
        schema["comment"] = child.intern_information
    return schema


def create_else_statement(child_object):
    if child_object.portal_type == "Field":
        if child_object.answer_type in string_type_fields:
            return {"properties": {create_id(child_object): {"maxLength": 0}}}
