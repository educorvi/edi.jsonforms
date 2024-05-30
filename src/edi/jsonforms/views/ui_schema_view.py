# -*- coding: utf-8 -*-

from edi.jsonforms import _
from Products.Five.browser import BrowserView
import json

from edi.jsonforms.views.common import possibly_required_types, create_id



class UiSchemaView(BrowserView):
    uischema = {}

    # needed to put scopes in showOn-properties without having to compute them
    lookup_scopes = {}

    def __call__(self):
        form = self.context
        self.uischema['type'] = 'VerticalLayout'
        children = form.getFolderContents()
        self.uischema['elements'] = []

        for child in children:
            child_object = child.getObject()

            # add children to the schema
            self.uischema['elements'].append(self.get_schema_for_child(child_object, '#/properties/'))

        self.msg = json.dumps(self.uischema)
        return self.index()

    def get_schema_for_child(self, child, scope):
        type = child.portal_type

        if type == 'Field':
            return self.get_schema_for_field(child, scope)
        elif type == 'SelectionField':
            return self.get_schema_for_selectionfield(child, scope)
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
            field_schema['format'] = 'password'
        elif answer_type == 'tel':
            field_schema['format'] = 'tel'
        elif answer_type == 'url':
            field_schema['format'] = 'url'
        elif answer_type == 'email':
            field_schema['format'] = 'email'
        elif answer_type == 'date':
            field_schema['format'] = 'date'
        elif answer_type == 'datetime-local':
            field_schema['format'] = 'date-time'
        elif answer_type == 'time':
            field_schema['format'] = 'time'
        elif answer_type == 'number':
            pass
            # TODO
        elif answer_type == 'integer':
            pass
            # TODO
        elif answer_type == 'boolean':
            pass
            # TODO
        return field_schema

    def get_schema_for_selectionfield(self, selectionfield, scope):
        selectionfield_schema = self.get_base_schema(selectionfield, scope)

        answer_type = selectionfield.answer_type
        if answer_type == 'radio':
            selectionfield_schema['options'] = {
                'radiobuttons': True,
                'stacked': True
            }
        elif answer_type in ['checkbox', 'selectmultiple']:
            selectionfield_schema['options'] = {'stacked': True}
        elif answer_type == 'select':
            pass # nothing
        elif answer_type in ['file', 'file-multi']:
            selectionfield_schema['options'] = {'acceptedFileType': '*'}

        return selectionfield_schema

    def get_schema_for_array(self, array, scope):
        # TODO elements? and compute scope properly

        # save scope in lookup_scopes
        array_id = array.id + array.UID()
        array_scope = scope + array_id
        self.lookup_scopes[array_id] = array_scope

        return self.create_group(array, array_scope + '/properties/')

    def get_schema_for_object(self, complex, scope):
        # save scope in lookup_scopes
        complex_id = complex.id + complex.UID()
        complex_scope = scope + complex_id
        self.lookup_scopes[complex_id] = complex_scope

        return self.create_group(complex, complex_scope + '/properties/')

    def get_schema_for_fieldset(self, fieldset, scope):
        return self.create_group(fieldset, scope)


    def get_base_schema(self, child, scope):
        child_id = create_id(child.id, child.UID())
        child_scope = scope + child_id
        base_schema = {
            'type': 'Control',
            'scope': child_scope,
        }
        self.lookup_scopes[child_id] = child_scope

        # add showOn dependencies
        if child.dependent_from_object:
            base_schema['showOn'] = self.create_showon_properties(child)

        return base_schema

    def create_group(self, group, scope):
        group_schema = {
            'type': 'Group',
            'label': group.title,
        }

        if group.dependent_from_object:
            group_schema['showOn'] = self.create_showon_properties(group)

        group_schema['elements'] = []
        children = group.getFolderContents()
        for child in children:
            child_object = child.getObject()
            group_schema['elements'].append(self.get_schema_for_child(child_object, scope))

        return group_schema

    def create_showon_properties(self, child):
        showOn = {
            'type': 'EQUALS',
            'scope': '',
            'referenceValue': ''
        }

        dependent_from = child.dependent_from_object.to_object
        dependent_id = create_id(dependent_from.id, dependent_from.UID())
        if dependent_from.portal_type not in ['Option', 'Field']:
            return {}
        elif dependent_from.portal_type == 'Option':
            parent = dependent_from.aq_parent
            dependent_id = create_id(parent.id, parent.UID())

        scope = self.lookup_scopes.get(dependent_id)
        if scope is None:
            scope = dependent_id
            parent = dependent_from.aq_parent
            if dependent_from.portal_type == 'Option':
                parent = parent.aq_parent

            while parent.portal_type != 'Form':
                if parent.portal_type != 'Fieldset':
                    scope = create_id(parent.id, parent.UID()) + '/properties/' + scope
                parent = parent.aq_parent

            scope = '#/properties/' + scope

        showOn['scope'] = scope

        if dependent_from.portal_type == 'Field':
            if dependent_from.answer_type == 'boolean':
                # TODO change
                showOn['type'] = 'NOT_EQUALS'
            else:
                showOn['type'] = 'NOT_EQUALS'
        elif dependent_from.portal_type == 'Option':
            showOn['referenceValue'] = dependent_from.title

        return showOn
