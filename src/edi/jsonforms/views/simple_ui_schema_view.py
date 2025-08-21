# -*- coding: utf-8 -*-

from edi.jsonforms import _
from Products.Five.browser import BrowserView
import json

from edi.jsonforms.views.common import *


class SimpleUiSchemaView(BrowserView):
    """
    Generate a simplified UI schema with flattened field structure.
    Output format uses ui:* prefixed properties for each field.
    """

    def __init__(self, context, request):
        super().__init__(context, request)
        self.ui_schema = {}
        self.processed_fields = set()  # Track processed fields to avoid duplicates
        self.field_dependencies = {}  # Cache of field dependencies

    def __call__(self):
        self.get_schema()
        return json.dumps(self.ui_schema, ensure_ascii=False, indent=2)

    def get_schema(self):
        """Generate the complete UI schema by processing all form children."""
        form = self.context
        self.ui_schema = {}
        self.processed_fields = set()
        self.field_dependencies = {}

        # First pass: collect all fields and their dependencies
        self.collect_dependencies(form)

        # Second pass: process fields into UI schema
        children = form.getFolderContents()
        for child in children:
            child_object = child.getObject()
            if check_show_condition_in_request(self.request, child_object.show_condition, child_object.negate_condition):
                self.process_child(child_object)

        return self.ui_schema

    def process_child(self, child_object, parent_id=None):
        """Process a single child object and add it to the UI schema."""
        child_type = child_object.portal_type

        if child_type == 'Field':
            self.add_field_to_schema(child_object, parent_id)
        elif child_type == 'SelectionField':
            self.add_selection_field_to_schema(child_object, parent_id)
        elif child_type == 'UploadField':
            self.add_upload_field_to_schema(child_object, parent_id)
        elif child_type == 'Array':
            self.add_array_to_schema(child_object, parent_id)
        elif child_type == 'Complex':
            self.add_complex_to_schema(child_object, parent_id)
        elif child_type == 'Fieldset':
            self.add_fieldset_to_schema(child_object, parent_id)
        # Skip Helptext and other non-input types for now

    def add_field_to_schema(self, field, parent_id=None):
        """Add a regular field to the UI schema."""
        field_id = create_hierarchical_id(field, parent_id) if parent_id else create_id(field)
        if field_id in self.processed_fields:
            return
        
        self.processed_fields.add(field_id)
        field_schema = self.create_base_field_schema(field, parent_id)

        # Map answer type to widget
        answer_type = field.answer_type
        if answer_type == 'textarea':
            field_schema['ui:widget'] = 'textarea'
        elif answer_type == 'password':
            field_schema['ui:widget'] = 'password'
        elif answer_type == 'boolean':
            field_schema['ui:widget'] = 'checkbox'
        elif answer_type in ['date', 'datetime-local', 'time']:
            field_schema['ui:widget'] = answer_type
        # For text, email, tel, url, number, integer - use default input

        # Add placeholder for applicable field types
        if answer_type in ['text', 'textarea', 'password', 'tel', 'url', 'email']:
            placeholder = get_placeholder(field, self.request)
            if placeholder:
                field_schema['ui:placeholder'] = placeholder

        # Add unit for number fields
        if answer_type in ['number', 'integer']:
            unit = get_unit(field, self.request)
            if unit:
                field_schema['ui:unit'] = unit

        self.ui_schema[field_id] = field_schema

    def add_selection_field_to_schema(self, selection_field, parent_id=None):
        """Add a selection field to the UI schema."""
        field_id = create_hierarchical_id(selection_field, parent_id) if parent_id else create_id(selection_field)
        if field_id in self.processed_fields:
            return
            
        self.processed_fields.add(field_id)
        field_schema = self.create_base_field_schema(selection_field, parent_id)

        answer_type = selection_field.answer_type
        if answer_type == 'radio':
            field_schema['ui:widget'] = 'radio'
        elif answer_type in ['checkbox', 'selectmultiple']:
            field_schema['ui:widget'] = 'checkboxes'
        elif answer_type == 'select':
            field_schema['ui:widget'] = 'select'

        # Add options
        options = []
        for option in selection_field.getFolderContents():
            option_obj = option.getObject()
            if selection_field.use_id_in_schema:
                value = create_id(option_obj)
            else:
                value = option.Title
            
            options.append({
                "value": value,
                "label": option.Title
            })
        
        if options:
            field_schema['ui:options'] = options

        self.ui_schema[field_id] = field_schema

    def add_upload_field_to_schema(self, upload_field, parent_id=None):
        """Add an upload field to the UI schema."""
        field_id = create_hierarchical_id(upload_field, parent_id) if parent_id else create_id(upload_field)
        if field_id in self.processed_fields:
            return
            
        self.processed_fields.add(field_id)
        field_schema = self.create_base_field_schema(upload_field, parent_id)

        field_schema['ui:widget'] = 'file'
        
        if upload_field.answer_type == 'file-multi':
            field_schema['ui:multiple'] = True

        if upload_field.accepted_file_types:
            field_schema['ui:accept'] = upload_field.accepted_file_types

        self.ui_schema[field_id] = field_schema

    def add_array_to_schema(self, array, parent_id=None):
        """Add an array field to the UI schema."""
        field_id = create_hierarchical_id(array, parent_id) if parent_id else create_id(array)
        if field_id in self.processed_fields:
            return
            
        self.processed_fields.add(field_id)
        field_schema = self.create_base_field_schema(array, parent_id)
        field_schema['ui:widget'] = 'array'

        # Process children of the array with array ID as parent context
        children = array.getFolderContents()
        for child in children:
            child_object = child.getObject()
            if check_show_condition_in_request(self.request, child_object.show_condition, child_object.negate_condition):
                self.process_child(child_object, field_id)

        self.ui_schema[field_id] = field_schema

    def add_complex_to_schema(self, complex_obj, parent_id=None):
        """Add a complex object to the UI schema."""
        field_id = create_hierarchical_id(complex_obj, parent_id) if parent_id else create_id(complex_obj)
        if field_id in self.processed_fields:
            return
            
        self.processed_fields.add(field_id)
        field_schema = self.create_base_field_schema(complex_obj, parent_id)
        field_schema['ui:widget'] = 'object'

        # Process children of the complex object with complex ID as parent context
        children = complex_obj.getFolderContents()
        for child in children:
            child_object = child.getObject()
            if check_show_condition_in_request(self.request, child_object.show_condition, child_object.negate_condition):
                self.process_child(child_object, field_id)

        self.ui_schema[field_id] = field_schema

    def add_fieldset_to_schema(self, fieldset, parent_id=None):
        """Add fieldset children to the UI schema (fieldset itself is grouping, not a field)."""
        # Process children of the fieldset - fieldsets are transparent, so pass parent_id through
        children = fieldset.getFolderContents()
        for child in children:
            child_object = child.getObject()
            if check_show_condition_in_request(self.request, child_object.show_condition, child_object.negate_condition):
                self.process_child(child_object, parent_id)

    def create_base_field_schema(self, field_obj, parent_id=None):
        """Create the base schema structure for any field."""
        field_schema = {}

        # Title
        title = get_title(field_obj, self.request)
        if title:
            field_schema['ui:title'] = title

        # Description
        description = get_description(field_obj, self.request)
        if description:
            field_schema['ui:description'] = description

        # Help text
        help_text = get_user_helptext(field_obj, self.request)
        if help_text:
            field_schema['ui:help'] = help_text

        # Column layout (always full width to match your format)
        field_schema['ui:column'] = 'col-md-12'

        # Add mask configuration if applicable (example implementation)
        if hasattr(field_obj, 'pattern') and field_obj.pattern:
            # Convert regex pattern to mask format - this is a simple example
            # You might want to customize this based on your specific needs
            field_schema['ui:mask'] = {
                "mask": "99-9999",  # Example mask
                "mask_placeholder": "#"
            }

        # Add custom attributes (includes conditions and condition targets)
        attributes = self.get_field_attributes(field_obj, parent_id)
        if attributes:
            field_schema['ui:attributes'] = attributes

        return field_schema

    def get_field_conditions(self, field_obj):
        """Convert field dependencies to ui:conditions format."""
        if not hasattr(field_obj, 'dependencies') or not field_obj.dependencies:
            return []

        conditions = []
        for dep in field_obj.dependencies:
            try:
                dep_obj = dep.to_object
                dep_id = create_id(dep_obj)
                
                if dep_obj.portal_type == 'Option':
                    # For option dependencies, check if parent selection field equals this option
                    selection_parent = dep_obj.aq_parent
                    selection_id = create_id(selection_parent)
                    option_value = get_title(dep_obj, self.request) if hasattr(dep_obj, 'title') else dep_obj.Title
                    
                    condition = {
                        "field": selection_id,
                        "operator": "equals",
                        "value": option_value
                    }
                    conditions.append(condition)
                else:
                    # For other field dependencies, check if field has a value
                    condition = {
                        "field": dep_id,
                        "operator": "not_empty",
                        "value": True
                    }
                    conditions.append(condition)
            except:
                # Skip invalid dependencies
                continue

        return conditions

    def get_field_attributes(self, field_obj, parent_id=None):
        """Generate ui:attributes for the field, including conditions and condition targets."""
        attributes = {}
        field_id = create_hierarchical_id(field_obj, parent_id) if parent_id else create_id(field_obj)
        
        # Check if this field has dependencies (conditions)
        if hasattr(field_obj, 'dependencies') and field_obj.dependencies:
            conditions = []
            for dep in field_obj.dependencies:
                try:
                    dep_obj = dep.to_object
                    if dep_obj.portal_type == 'Option':
                        # For option dependencies, check if parent selection field equals this option
                        selection_parent = dep_obj.aq_parent
                        selection_id = self._get_hierarchical_id_for_dependency(selection_parent)
                        option_value = get_title(dep_obj, self.request) if hasattr(dep_obj, 'title') else dep_obj.Title
                        
                        condition_str = f"{{'field': '{selection_id}', 'operator': 'equals', 'value': '{option_value}'}}"
                        attributes['data-conditions'] = condition_str
                        attributes['data-condition-logic'] = 'and'
                        break  # Take first condition for now
                except:
                    continue
        
        # Add data-condition-target attribute if this field has dependents
        dependent_fields = self.find_dependent_fields(field_obj, parent_id)
        if dependent_fields:
            attributes['data-condition-target'] = ','.join(dependent_fields)
        
        return attributes

    def collect_dependencies(self, container, parent_id=None):
        """Recursively collect all field dependencies in the form."""
        children = container.getFolderContents()
        
        # Get the current container's ID to use as parent context for children
        current_container_id = create_id(container) if parent_id is None else create_hierarchical_id(container, parent_id)
        
        for child in children:
            child_object = child.getObject()
            if not check_show_condition_in_request(self.request, child_object.show_condition, child_object.negate_condition):
                continue
                
            # Use hierarchical ID for the child based on parent context
            if container.portal_type in ['Array', 'Complex']:
                child_id = create_hierarchical_id(child_object, current_container_id)
            else:
                child_id = create_hierarchical_id(child_object, parent_id) if parent_id else create_id(child_object)
            
            # Check if this field has dependencies
            if hasattr(child_object, 'dependencies') and child_object.dependencies:
                for dep in child_object.dependencies:
                    try:
                        dep_obj = dep.to_object
                        if dep_obj.portal_type == 'Option':
                            # For option dependencies, the dependency is on the parent selection field
                            selection_parent = dep_obj.aq_parent
                            dep_id = self._get_hierarchical_id_for_dependency(selection_parent)
                        else:
                            dep_id = self._get_hierarchical_id_for_dependency(dep_obj)
                        
                        # Track that child_id depends on dep_id
                        if dep_id not in self.field_dependencies:
                            self.field_dependencies[dep_id] = []
                        self.field_dependencies[dep_id].append(child_id)
                    except:
                        continue
            
            # Recursively process container fields
            if child_object.portal_type in ['Array', 'Complex', 'Fieldset']:
                if child_object.portal_type == 'Fieldset':
                    # Fieldsets are transparent, pass through parent context
                    self.collect_dependencies(child_object, parent_id)
                else:
                    # Arrays and complex objects create new parent context
                    self.collect_dependencies(child_object, child_id)

    def _get_hierarchical_id_for_dependency(self, obj):
        """Get hierarchical ID for a dependency object by walking up the parent chain."""
        # Walk up the parent chain to build the hierarchical ID
        parent = obj.aq_parent
        parent_chain = []
        
        # Build chain of parents until we reach Form
        current = parent
        while current.portal_type != 'Form':
            if current.portal_type != 'Fieldset':  # Skip fieldsets as they're transparent
                parent_chain.append(current)
            current = current.aq_parent
        
        # Build hierarchical ID from the chain
        if not parent_chain:
            return create_id(obj)
        
        # Start with the topmost non-fieldset parent
        hierarchical_id = create_id(obj)
        for parent_obj in reversed(parent_chain):
            hierarchical_id = create_hierarchical_id(obj, create_id(parent_obj))
            obj = parent_obj  # Update obj for next iteration
        
        return hierarchical_id

    def find_dependent_fields(self, field_obj, parent_id=None):
        """Find fields that depend on this field."""
        # Use hierarchical ID for the field lookup
        if parent_id:
            field_id = create_hierarchical_id(field_obj, parent_id)
        else:
            field_id = self._get_hierarchical_id_for_dependency(field_obj)
        
        return self.field_dependencies.get(field_id, [])