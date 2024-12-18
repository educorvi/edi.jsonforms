from edi.jsonforms.views.common import create_id
import re


"""
lookup_scopes is a class variable in the ui schema, it gets updated during the computation of the ui schema,
so it saves manual computation time of the scopes
"""
def find_scope(lookup_scopes, object):
    obj_id = create_id(object)
    if object.portal_type not in ['Option', 'Field']:
        return {}
    elif object.portal_type == 'Option':
        parent = object.aq_parent
        obj_id = create_id(parent)

    scope = lookup_scopes.get(obj_id)

    # scope wasn't saved yet, has to be computed manually and then save it
    if scope is None:
        scope = obj_id
        parent = object.aq_parent
        if object.portal_type == 'Option':
            parent = parent.aq_parent
        while parent.portal_type != 'Form':
            if parent.portal_type != 'Fieldset':
                if parent.portal_type == "Array":
                    scope = create_id(parent) + '/items/properties/' + scope
                else:
                    scope = create_id(parent) + '/properties/' + scope
            parent = parent.aq_parent
        scope = '/properties/' + scope
    lookup_scopes[obj_id] = scope

    return scope

"""
replaces /properties/ with 
"""
def transform_scope_to_object_writing_form(scope):
    # convert scope to object writing form:
    # replace 'properties/' from the string with .
    path = re.sub(r'properties/', '', scope)
    # items stays in the path, to check if array exists in path to adapt all rules accordingly
    path = re.sub(r'/items/', '.', path) # TODO temporary until feature for "self" exists

    # replace remaining slashes with dots, but the first / is removed
    # leave /items/ unchanged
    # def replace_slashes(match):
    #     if match.group(0) == '/items/':
    #         return '/items/'
    #     return '.'
    # path = re.sub(r'/items/|/', replace_slashes, path)
    # path = re.sub(r'/items/')
    path = re.sub(r'/', '.', path)

    # remove leading slash if present
    if path.startswith('.'):
        path = path[1:]

    return path

def get_scope(lookup_scopes, object):
    scope = find_scope(lookup_scopes, object)
    return transform_scope_to_object_writing_form(scope)



def create_rule_for_single_select_option(scope, title):
    rule = {
        'type': 'comparison',
        'operation': 'equal',
        'arguments': [
            {
                'type': 'atom',
                'path': scope,
                'default': None
            },
            title
        ]
    }

    return rule

def create_rule_for_multi_select_option(scope, title):
    rule = {
        "type": "exists",
        "array":{
            "type": "atom",
            "path": scope,
            "default": []
        },
        "placeholder": "current_option",
        "rule": {
            "type": "comparison",
            "operation": "equal",
            "arguments": [
                {
                    "type": "atom",
                    "path": "current_option",
                    "default": ""
                },
                title
            ]
        }
    }

    return rule

def create_rule_for_bool(scope):
    rule = {
        'type': 'comparison',
        'operation': 'equal',
        'arguments': [
            {
                'type': 'atom',
                'path': scope,
                'default': False
            },
            True
        ]
    }
    return rule

def create_rule_for_num(scope):
    rule = {
        'type': 'or',
        'arguments': [
            {
                'type': 'comparison',
                'allowDifferentTypes': True,
                'operation': 'greater',
                'arguments': [
                    {
                        'type': 'atom',
                        'path': scope,
                        'default': 0
                    },
                    0
                ]
            },
            {
                'type': 'comparison',
                'allowDifferentTypes': True,
                'operation': 'smaller',
                'arguments': [
                    {
                        'type': 'atom',
                        'path': scope,
                        'default': 0
                    },
                    0
                ]
            }
        ]
    }
    return rule

def create_rule_for_text(scope):
    rule = {
        'type': 'comparison',
        'operation': 'greater',
        'arguments': [
            {
                'type': 'macro',
                'macro': {
                    'type': 'length',
                    'array': {
                        'type': 'atom',
                        'path': scope,
                        'default': ""
                    }
                }
            },
            0
        ]
    }
    return rule

"""
scope: is the scope to the object for which the rule is created in object writing form
full_path: is the scope with / and /properties/ and /items/ (needed for $selfIndices of the rita rules)
"""
def create_rule_within_array(full_path: str, object) -> dict:
    array_rule = {}
    paths = re.split(r'/items', full_path)

    current_path = ""
    current_object_path = ""

    current_rule = {}
    counter = 1
    # go through all paths of arrays (split at '/items')
    for path in paths[:len(paths)-1]:
        current_path += path

        # get path of object beginning at the previous array (or form if parent array)
        if current_object_path != "":
            index = path.rfind('/properties/')
            current_object_path = f"$array_item{str(counter - 1)}.{path[index + len('/properties/'):]}"
        else:
            current_object_path = transform_scope_to_object_writing_form(current_path)

        # create rule for current array
        rule = {
            'type': 'exists',
            'array': {
                'type': 'atom',
                'path': current_object_path,
                'default': []
            },
            'placeholder': '$array_item' + str(counter),
            'indexPlaceholder': '$index' + str(counter),
            'rule': {
                'type': 'and',
                'arguments': [
                    {
                        'type': 'comparison',
                        'operation': 'equal',
                        'arguments': [
                            {
                                'type': 'atom',
                                'path': '$index' + str(counter),
                                'default': -1
                            },
                            {
                                'type': 'atom',
                                'path': '$selfIndices.' + current_path,
                                'default': -1
                            }
                        ]
                    }
                ]
            }
        }

        if array_rule == {}:
            array_rule = rule
            current_rule = rule
        else:
            current_rule['rule']['arguments'].append(rule)
            current_rule = rule

        counter += 1
        current_path += "/items"
    path = paths[-1]

    # add actual rule to array rule structure
    object_id = transform_scope_to_object_writing_form(path)
    object_scope = f"$array_item{str(counter-1)}.{object_id}"
    current_rule['rule']['arguments'].append(get_rule(object_scope, object))

    return array_rule


def create_rule(scope, object):
    rule = {}
    # object with showOn-rule is in an array -> add array rita logic around the actual rule
    if '/items/' in scope:
        rule = create_rule_within_array(scope, object)
    else:
        scope = transform_scope_to_object_writing_form(scope)
        rule = get_rule(scope, object)
        
    return rule

def get_rule(scope, object):
    if object.portal_type == 'Option':
        if object.aq_parent.answer_type in ['radio', 'select']:
            rule = create_rule_for_single_select_option(scope, object.title)
        elif object.aq_parent.answer_type in ['checkbox', 'selectmultiple']:
            rule = create_rule_for_multi_select_option(scope, object.title)
    elif object.portal_type == 'Field':
        if object.answer_type == 'boolean':
            rule = create_rule_for_bool(scope)
        elif object.answer_type in ['number', 'integer']:
            rule = create_rule_for_num(scope)
        else:
            rule = create_rule_for_text(scope)
    return rule


def create_showon_properties(child, lookup_scopes):
    dependencies = child.dependencies
    if len(dependencies) == 1:
        #try:
        dep = dependencies[0].to_object
        scope = find_scope(lookup_scopes, dep)
        showOn = {
            'id': 'ritaRule-' + create_id(child),
            'rule': create_rule(scope, dep)
        }
        # except:
        #     return {}
    else:
        conn = 'or'
        if child.connection_type:
            conn = 'and'

        showOn = {
            'id': 'ritaRule-' + create_id(child),
            'rule': {
                'type': conn,
                'arguments': []
            }
        }

        for dep in dependencies:
            try:
                dep = dep.to_object
                scope = find_scope(lookup_scopes, dep)
                dep_rule = create_rule(scope, dep)

                showOn['rule']['arguments'].append(dep_rule)
            except:
                # dependency got deleted, plone error
                continue

        # check that arguments isn't empty (would mean every dependency was deleted)
        if len(showOn['rule']['arguments']) == 0:
            return {}
        # only one dependency wasn't deleted, transform list of rules to one rule
        elif len(showOn['rule']['arguments']) == 1:
            return {'id': 'ritaRule-' + create_id(child),
                    'rule': showOn['rule']['arguments']}

    return showOn
