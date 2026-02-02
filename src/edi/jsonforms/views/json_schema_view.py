# -*- coding: utf-8 -*-

from Products.Five.browser import BrowserView

import copy
import itertools
import json

from edi.jsonforms.views.common import *

from edi.jsonforms.content.option_list import get_keys_and_values_for_options_list

from plone.base.utils import safe_hasattr


class JsonSchemaView(BrowserView):
    is_extended_schema = False  # True if schema is generated for an api call and not for the usual form view
    content_types_without_schema = ["Helptext", "Button Handler"]
    is_single_view = False

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
        self.prepare_objects(form)  # traverse all objects and set parent_dependencies

        children = form.getFolderContents()
        for child in children:
            self.add_child_to_schema(child.getObject(), self.jsonschema)

        if "allOf" in self.jsonschema and len(self.jsonschema["allOf"]) == 0:
            del self.jsonschema["allOf"]

        return self.jsonschema

    def set_json_base_schema(self):
        self.jsonschema = {"type": "object"}
        self.jsonschema["properties"] = {}
        self.jsonschema["required"] = []
        self.jsonschema["dependentRequired"] = {}
        self.jsonschema["allOf"] = []
        self.ids = set()

    def prepare_objects(self, obj, parent_dependencies=None):
        """
        Prepare objects before creating the schema.
        Traverse all objects and set parent_dependencies as a flat list of dependencies collected from all ancestor objects.
        Skip Option and OptionList.
        """
        if parent_dependencies is None:
            parent_dependencies = []

        if obj.portal_type != "Form":
            obj.parent_dependencies = copy.copy(parent_dependencies)
            if safe_hasattr(obj, "dependencies") and obj.dependencies:
                parent_dependencies = parent_dependencies + obj.dependencies

        if hasattr(obj, "getFolderContents"):
            for child in obj.getFolderContents():
                child = child.getObject()
                if child.portal_type not in ["Option", "OptionList"]:
                    self.prepare_objects(child, parent_dependencies)

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
            if self.check_for_dependencies(child_object):
                self.add_dependent_required(schema, child_object)
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

    def get_values_for_selectionfield(
        self, selectionfield, option_optionlist, ignore_conditions=False
    ):
        """
        selectionfield: SelectionField, is used to check use_id_in_schema
        option_optionlist: Option or OptionList
        returns the option or optionlist depending on show_condition and dependencies
        if ignore_conditions is True, show_condition and dependencies are ignored
        """
        o = option_optionlist
        if safe_hasattr(o, "getObject"):
            o = o.getObject()
        options_list = []
        if o.portal_type == "Option":
            if ignore_conditions:
                options_list.append(self.get_option_name(o))
                return options_list

            show = True
            if safe_hasattr(o, "show_condition"):
                negate_condition = getattr(o, "negate_condition", False)
                show = check_show_condition_in_request(
                    self.request, o.show_condition, negate_condition
                )
            if show and not self.check_for_dependencies(o):
                options_list.append(self.get_option_name(o))
            # dependencies of options are handled in add_child_to_schema
        elif o.portal_type == "OptionList":
            keys, vals = get_keys_and_values_for_options_list(o)
            if selectionfield.use_id_in_schema:
                local_options_list = keys
            else:
                local_options_list = vals
            options_list.extend(local_options_list)
        return options_list

    def get_schema_for_selectionfield(self, selectionfield):
        selectionfield_schema = self.create_base_schema__field({}, selectionfield)
        answer_type = selectionfield.answer_type
        options = selectionfield.getFolderContents()

        options_list = []
        for o in options:
            options_list.extend(
                self.get_values_for_selectionfield(
                    selectionfield, o, self.is_single_view
                )
            )

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

        if "allOf" in complex_schema and len(complex_schema["allOf"]) == 0:
            del complex_schema["allOf"]

        return complex_schema

    def add_dependent_required(self, parent_schema, child_object):
        """
        schema: dict - schema where dependentRequired and/or allOf should be added
        child_object: object - object which is dependently required (or its ancestors have dependencies)
        """
        schema = self.jsonschema  # TODO make this dependent on schema parameter? (if present take schema, change calls accordingly) (at the end of this function the current schema is needed as backup in case all dependencies are invalid)
        dependencies = copy.copy(child_object.dependencies)
        dependencies.extend(getattr(child_object, "parent_dependencies", []))

        # copy 'allOf' and 'dependentRequired' to check that at least one of them changed
        schema_allof_copy = copy.deepcopy(schema["allOf"])
        schema_dependentrequired_copy = copy.deepcopy(schema["dependentRequired"])

        for dep in dependencies:
            try:
                dep = dep.to_object
            except:
                # dependency got deleted, plone error, ignore this dependency
                continue

            if dep.portal_type == "Option":
                dep_path = self.get_path(dep.aq_parent)
            else:
                dep_path = self.get_path(dep)

            def create_statement(obj, obj_path) -> dict:
                """
                creates hiearchy of path as a statement (use in if or then)
                if portal_type of obj is not Option and only one 'properties' in path, no 'properties' key is created
                """
                props = obj_path.split("/")
                if props.count("properties") == 1 and obj.portal_type != "Option":
                    statement = {"required": [props[-1]]}
                else:
                    statement = {}
                    cur_statement = statement

                    for i, p in enumerate(props):
                        if p == "properties" and (
                            i < len(props) - 2
                            and obj.portal_type != "Option"
                            or i < len(props) - 1
                            and obj.portal_type == "Option"
                        ):
                            cur_statement[p] = {}
                            cur_statement["required"] = [props[i + 1]]
                            cur_statement = cur_statement[p]
                        elif i < len(props) - 2:
                            cur_statement[p] = {}
                            cur_statement = cur_statement[p]
                        else:  # last element
                            if obj.portal_type == "Option":
                                cur_statement[p] = {"const": get_option_name(obj)}
                            else:
                                cur_statement["required"] = [props[-1]]
                return statement

            if_statement = {"if": create_statement(dep, dep_path)}
            then_statement = {
                "then": create_statement(child_object, self.get_path(child_object))
            }
            if self.is_extended_schema:
                if_statement["else"] = create_else_statement(child_object)
            if_then = {**if_statement, **then_statement}
            schema["allOf"].append(if_then)
        # Check that at least one dependency wasn't deleted so that 'allOf' and/or 'dependentRequired' changed.
        # Otherwise add child_object to required-list of the schema, because it is required and not dependent required, if it has no valid dependencies anymore
        if (
            schema_allof_copy == schema["allOf"]
            and schema_dependentrequired_copy == schema["dependentRequired"]
        ):
            parent_schema["required"].append(create_id(child_object))
        return

    def get_dependent_options(self, parent_object):
        if self.is_single_view:
            return []
        dependency_option_order = {}
        """
        parent_object: SelectionField
        """

        def add_to_dict(option, dependency, dict):
            parent_key = "SHOWALWAYS"
            if dependency:
                parent_key = create_id(dependency.aq_parent)
                dependency_key = self.get_option_name(dependency)
                option_value = self.get_option_name(option)

                # todo: refactor isMultiField into seperat method and call here and below
                answer_type = (
                    "multi"
                    if dependency.aq_parent.answer_type
                    in ["checkbox", "selectmultiple"]
                    else "single"
                )

                parent_key = f"{answer_type}_{parent_key}"
                if parent_key not in dependency_option_order:
                    dependency_option_order[parent_key] = self._get_option_order_map(
                        dependency.aq_parent
                    )
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
        parent_option_order = self._get_option_order_map(parent_object)

        for option in options:
            if option.portal_type == "Option":
                option = option.getObject()
                if self.check_for_dependencies(option):
                    dependencies = option.dependencies
                    for dep in dependencies:
                        try:
                            add_to_dict(option, dep.to_object, dependency_dict)
                        except:
                            # dependency got deleted, plone error, ignore this dependency
                            continue

                else:
                    add_to_dict(option, None, dependency_dict)

        # if dependency_dict["SHOWALWAYS"]:
        #     showalways_list = [entry for entry in dependency_dict["SHOWALWAYS"]]
        # else:
        #     showalways_list = []

        possibilities = []

        for selectionfield_id in dependency_dict:
            if selectionfield_id == "SHOWALWAYS":
                continue
            if selectionfield_id.startswith("multi_"):
                # possibilities.append([[(selectionfield_id, None)], [selectionfield_id]])
                # selectionfield_options = []
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
                selectionfield_id_clean = selectionfield_id.split("_", 1)[1]

                if selectionfield_id.startswith("multi_"):
                    const_values = list(sublist[1])
                    order_map = dependency_option_order.get(selectionfield_id)
                    if order_map:
                        const_values.sort(
                            key=lambda value: order_map.get(value, len(order_map))
                        )
                    if_dict["properties"][selectionfield_id_clean] = {
                        "const": const_values
                        # "contains": {"enum": const_values}
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
                # todo: see todo above
                ordered_then_enum = self._order_values(then_enum, parent_option_order)
                if option.aq_parent.answer_type in ["checkbox", "selectmultiple"]:
                    then_enum = {"items": {"enum": ordered_then_enum}}
                else:
                    then_enum = {"enum": ordered_then_enum}
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
        return get_option_name(option)

    def get_path(self, obj, without_root=False):
        """
        get the path of an object in the json schema (leaves out fieldsets)
        e.g. properties/object1/properties/selectionfield1/properties/option1
        """
        path = create_id(obj)
        while obj.aq_parent.portal_type != "Form":
            obj = obj.aq_parent
            if obj.portal_type != "Fieldset":
                path = create_id(obj) + "/properties/" + path
        return "properties/" + path

    def _get_option_order_map(self, selectionfield):
        order_map = {}
        index = 0
        for option in selectionfield.getFolderContents():
            if option.portal_type != "Option":
                continue
            option_obj = option.getObject()
            order_map[self.get_option_name(option_obj)] = index
            index += 1
        return order_map

    def _order_values(self, values, order_map):
        deduped = []
        seen = set()
        for idx, value in enumerate(values):
            if value in seen:
                continue
            seen.add(value)
            deduped.append((value, idx))
        if not order_map:
            return [value for value, _ in deduped]
        deduped.sort(key=lambda item: (order_map.get(item[0], len(order_map)), item[1]))
        return [value for value, _ in deduped]

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

    def check_for_dependencies(self, child_object):
        if self.is_single_view:  # if form-element-view, ignore all dependencies
            return False
        elif safe_hasattr(child_object, "dependencies") and child_object.dependencies:
            return True
        elif (
            safe_hasattr(child_object, "parent_dependencies")
            and child_object.parent_dependencies
            and child_object.portal_type not in ["Option", "OptionList"]
        ):
            return True
        else:
            return False


def get_option_name(option):
    parent_selectionfield = option.aq_parent
    if parent_selectionfield.use_id_in_schema:
        return create_id(option)
    else:
        return option.title


def add_interninformation(schema, child):
    if hasattr(child, "intern_information") and child.intern_information:
        schema["comment"] = child.intern_information
    return schema


def create_else_statement(child_object):
    if child_object.portal_type == "Field":
        if child_object.answer_type in string_type_fields:
            return {"properties": {create_id(child_object): {"maxLength": 0}}}
