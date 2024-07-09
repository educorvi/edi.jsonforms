from edi.jsonforms.views.common import create_id


"""
lookup_scopes is a class variable in the ui schema, it gets updated during the computation of the ui schema,
so it saves manual computation time of the scopes
"""
def get_scope(lookup_scopes, object):
    obj_id = create_id(object)
    if object.portal_type not in ['Option', 'Field']:
        return {}
    elif object.portal_type == 'Option':
        parent = object.aq_parent
        obj_id = create_id(parent)

    scope = lookup_scopes.get(obj_id)

    # scope wasn't saved yet, has to be computed manually
    if scope is None:
        scope = obj_id
        parent = object.aq_parent
        if object.portal_type == 'Option':
            parent = parent.aq_parent
        while parent.portal_type != 'Form':
            if parent.portal_type != 'Fieldset':
                scope = create_id(parent) + '/properties/' + scope
            parent = parent.aq_parent
        scope = '/properties/' + scope

    return scope

def create_rule_for_single_select_option(scope, title):
    rule = {
        'type': 'comparison',
        'operation': 'equal',
        'arguments': [
            {
                'type': 'atom',
                'path': scope
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
            "path": scope
        },
        "placeholder": "current_option",
        "rule": {
            "type": "comparison",
            "operation": "equal",
            "arguments": [
                {
                    "type": "atom",
                    "path": "current_option"
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
                'path': scope
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
                        'path': scope
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
                        'path': scope
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
                        'path': scope
                    }
                }
            },
            0
        ]
    }
    return rule


def create_rule(scope, object):
    rule = {}
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
        dep = dependencies[0].to_object
        scope = get_scope(lookup_scopes, dep)
        showOn = {
            'id': 'ritaRule-' + create_id(child),
            'rule': create_rule(scope, dep)
        }
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
            dep = dep.to_object
            scope = get_scope(lookup_scopes, dep)
            dep_rule = create_rule(scope, dep)

            showOn['rule']['arguments'].append(dep_rule)

    return showOn
