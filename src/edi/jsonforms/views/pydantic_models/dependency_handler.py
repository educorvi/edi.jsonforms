import copy
import itertools
from plone.base.utils import safe_hasattr
from typing import Any, Dict, List
from edi.jsonforms.content.selection_field import ISelectionField
from edi.jsonforms.content.common import IFormElement
from edi.jsonforms.views.common import create_id, get_path, string_type_fields
from edi.jsonforms.views.pydantic_models.BaseFormElementModel import (
    BaseFormElementModel,
)
from edi.jsonforms.views.pydantic_models.FormProperties import FormProperties
from edi.jsonforms.views.common import get_option_name
# from plone.base.utils import safe_hasattr

logger = logging.getLogger(__name__)


def check_for_dependencies(model: IFormElement, is_single_view: bool) -> bool:
    """
    returns True if the given model has dependencies that should be checked (if not in single view) and False otherwise
    """
    if is_single_view:  # if form-element-view, ignore all dependencies
        return False
    elif safe_hasattr(model, "dependencies") and model.dependencies:
        return True
    else:
        return False


def get_dependencies_of_closest_ancestor_with_dependencies(
    model: BaseFormElementModel,
) -> List[IFormElement]:
    """
    returns a shallow copy of the dependencies of the closest ancestor with dependencies, if there is no ancestor with dependencies, an empty list is returned
    """
    parent = model.parent
    while parent:
        if safe_hasattr(parent, "dependencies") and parent.dependencies:
            return copy.copy(parent.dependencies)
        parent = parent.parent
    return []


# def add_dependent_required(parent: BaseFormElementModel, child: BaseFormElementModel):
def add_dependent_required(
    formProperties: FormProperties,
    child: BaseFormElementModel,
    is_extended_schema: bool = False,
):
    """
    this method changes dependentRequired or/and allOf of the parent based on the dependencies of the child model
    dependentRequired is changed if the child's dependency is not an Option inside a SelectionField
    allOf is changed if the child's dependency is an Option inside a SelectionField
    :param formProperties: the properties that will be set to the form at the end of generation.
    :param child: the model which is required and dependent on other models
    """
    # schema = self.jsonschema  # TODO make this dependent on schema parameter? (if present take schema, change calls accordingly) (at the end of this function the current schema is needed as backup in case all dependencies are invalid)
    # dependencies = copy.copy(child.get_dependencies())
    # dependencies.extend(getattr(child_object, "parent_dependencies", []))

    # copy 'allOf' and 'dependentRequired' to check that at least one of them changed
    allof_copy = copy.deepcopy(formProperties.allOf)
    dependentrequired_copy = copy.deepcopy(formProperties.dependentRequired)

    for dep in child.get_dependencies():
        try:
            dep = dep.to_object
            if dep is None:
                continue
        except:
            # dependency got deleted, plone error, ignore this dependency
            continue

        if dep.portal_type == "Option":
            dep_path = get_path(dep.aq_parent)
        else:
            dep_path = get_path(dep)

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
            "then": create_statement(child.form_element, get_path(child.form_element))
        }
        if is_extended_schema:
            else_statement = create_else_statement(child.form_element)
            if else_statement:
                if_statement["else"] = else_statement
        if_then = {**if_statement, **then_statement}
        formProperties.update_allOf([if_then])
    # Check that at least one dependency wasn't deleted so that 'allOf' and/or 'dependentRequired' changed.
    # Otherwise add child_object to required-list of the schema, because it is required and not dependent required, if it has no valid dependencies anymore
    if (
        allof_copy == formProperties.allOf
        and dependentrequired_copy == formProperties.dependentRequired
    ):
        formProperties.update_required([child.get_id()])
    return


def _get_option_order_map(selectionfield):
    # TODO what happens to OptionLists?
    order_map = {}
    index = 0
    for option in selectionfield.getFolderContents():
        if option.portal_type != "Option":
            continue
        option_obj = option.getObject()
        order_map[get_option_name(option_obj)] = index
        index += 1
    return order_map


def _order_values(values, order_map):
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


def create_else_statement(child_object: IFormElement) -> dict:
    if child_object.portal_type == "Field":
        if child_object.answer_type in string_type_fields:
            return {"properties": {create_id(child_object): {"maxLength": 0}}}
    return {}


def add_dependent_options(
    selectionfield: ISelectionField,
    is_single_view: bool,
    formProperties: FormProperties,
):
    """
    this method computes the allOf statement for dependent options of a selectionfield and adds it to the form
    """
    if is_single_view:
        return

    formProperties.update_allOf(get_dependent_options(selectionfield, is_single_view))


def get_dependent_options(
    selectionfield: ISelectionField, is_single_view: bool
) -> List[Dict[str, Any]]:
    dependency_option_order = {}

    def add_to_dict(option, dependency, target_dict):
        parent_key = "SHOWALWAYS"
        if dependency:
            parent_key = create_id(dependency.aq_parent)
            dependency_key = get_option_name(dependency)
            option_value = get_option_name(option)

            # todo: refactor isMultiField into seperat method and call here and below
            answer_type = (
                "multi"
                if dependency.aq_parent.answer_type in ["checkbox", "selectmultiple"]
                else "single"
            )

            parent_key = f"{answer_type}_{parent_key}"
            if parent_key not in dependency_option_order:
                dependency_option_order[parent_key] = _get_option_order_map(
                    dependency.aq_parent
                )
            if parent_key in target_dict:
                if dependency_key in target_dict[parent_key]:
                    target_dict[parent_key][dependency_key].append(option_value)
                else:
                    target_dict[parent_key][dependency_key] = [option_value]
            else:
                target_dict[parent_key] = {}
                target_dict[parent_key][dependency_key] = [option_value]
        else:
            target_dict["SHOWALWAYS"].append(get_option_name(option))

    allof_list = []
    options = selectionfield.getFolderContents()
    parent_object_id = create_id(selectionfield)
    dependency_dict = {"SHOWALWAYS": []}
    parent_option_order = _get_option_order_map(selectionfield)

    for option in options:
        if option.portal_type == "Option":
            option = option.getObject()
            if check_for_dependencies(option, is_single_view):
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
            possibilities.append([list((selectionfield_id, sub)) for sub in subsets])
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
                if_dict["properties"][selectionfield_id_clean] = {"const": sublist[1]}
                then_enum.extend(dependency_dict[selectionfield_id][sublist[1]])
            if_dict["required"].append(selectionfield_id_clean)
        if len(then_enum) > len(dependency_dict["SHOWALWAYS"]):
            # todo: see todo above
            ordered_then_enum = _order_values(then_enum, parent_option_order)
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
