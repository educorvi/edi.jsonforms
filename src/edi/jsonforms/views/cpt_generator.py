# -*- coding: utf-8 -*-

import json
from typing import Dict, Any, List
from edi.jsonforms import _
from Products.Five.browser import BrowserView
from dominate import document
from dominate.tags import div, h1, p, form

from edi.jsonforms.views.common import *


class ChameleonPageTemplateGenerator(BrowserView):
    """
    Generate Chameleon page template using dominate - adapted from uv_pt_generator.
    """

    def __init__(self, context, request):
        super().__init__(context, request)
        self.schema = {}
        self.ui_schema = {}

    def __call__(self):
        """Return the generated template as plain text."""
        template = self.generate_chameleon_template()
        self.request.response.setHeader('Content-Type', 'text/plain; charset=utf-8')
        return template

    def generate_chameleon_template(self) -> str:
        """Generate template using dominate - exact implementation from schema_generator.py"""
        # Load schemas
        self._load_schemas()
        
        # Create the container div
        container = div(cls="container")
        
        # Add header elements
        container.add(h1(**{"tal:content": "view.title"}))
        container.add(p(**{"tal:content": "view.description"}, cls="lead"))
        container.add(p("Die mit einem * (Stern) gekennzeichneten Felder sind Pflichtfelder.", cls="small"))
        
        # Create form with attributes
        form_element = form(
            **{
                "data-async": "true",
                "method": "POST",
                "novalidate": "novalidate",
                "data-upload-url": "${view.upload_url}",
                "data-json-endpoint": "${view.json_endpoint}",
                "enctype": "multipart/form-data",
                "tal:attributes": "action view.action; data-upload-url view.upload_url; class view.triggered and 'X-was-validated' or ''"
            }
        )
        
        properties = self.schema.get("properties", {})
        required_fields = self.schema.get("required", [])

        # Group fields by row based on column classes
        rows = self._group_fields_by_row(properties)
        
        for row_fields in rows:
            row_div = div(cls="row")
            for field_name in row_fields:
                ui_config = self.ui_schema.get(field_name, {})
                column_class = ui_config.get("ui:column", "col-12")
                col_div = div(cls=column_class)
                
                # Handle conditional fields and custom attributes
                field_attributes = {"tal:replace": f"structure form['{field_name}'].render_template(form.widget.item_template)"}
                
                # Add conditions as data attributes
                if "ui:conditions" in ui_config:
                    conditions_data = self._prepare_conditions_data(ui_config)
                    field_attributes.update(conditions_data)
                    # Make sure conditional fields have the right class
                    current_class = col_div.attributes.get('class', '')
                    col_div.attributes['class'] = f"{current_class} conditional-field".strip()
                
                # Add custom attributes
                if "ui:attributes" in ui_config:
                    field_attributes.update(ui_config["ui:attributes"])
                
                field_div = div(**field_attributes)
                col_div.add(field_div)
                row_div.add(col_div)
            form_element.add(row_div)
        
        container.add(form_element)
        return str(container)

    def _load_schemas(self):
        """Load JSON schema and UI schema from the form."""
        form = self.context
        
        # Import the views to get schemas
        from edi.jsonforms.views.json_schema_view import JsonSchemaView
        from edi.jsonforms.views.simple_ui_schema_view import SimpleUiSchemaView
        
        # Get JSON schema
        json_schema_view = JsonSchemaView(form, self.request)
        self.schema = json.loads(json_schema_view())
        
        # Get simple UI schema
        ui_schema_view = SimpleUiSchemaView(form, self.request)
        self.ui_schema = json.loads(ui_schema_view())
    
    def _group_fields_by_row(self, properties: Dict[str, Any]) -> List[List[str]]:
        """Group fields by row based on column classes."""
        rows = []
        current_row = []
        current_row_total = 0
        
        for field_name in properties.keys():
            ui_config = self.ui_schema.get(field_name, {})
            column_class = ui_config.get("ui:column", "col-12")
            
            # Extract column size from Bootstrap class (e.g., "col-md-6" -> 6)
            column_size = self._extract_column_size(column_class)
            
            # If adding this field would exceed 12 columns, start a new row
            if current_row_total + column_size > 12:
                if current_row:
                    rows.append(current_row)
                current_row = [field_name]
                current_row_total = column_size
            else:
                current_row.append(field_name)
                current_row_total += column_size
        
        # Add the last row if it has fields
        if current_row:
            rows.append(current_row)
        
        return rows
    
    def _extract_column_size(self, column_class: str) -> int:
        """Extract column size from Bootstrap class."""
        # Handle classes like "col-md-6", "col-6", "col-lg-4", etc.
        parts = column_class.split("-")
        if len(parts) >= 2:
            try:
                # Try to get the last part as the column size
                return int(parts[-1])
            except ValueError:
                pass
        # Default to 12 if we can't parse
        return 12
    
    def _prepare_conditions_data(self, ui_config: Dict[str, Any]) -> Dict[str, str]:
        """Prepare conditions data for jQuery module."""
        conditions = ui_config.get("ui:conditions", [])
        logic = ui_config.get("ui:condition_logic", "and")
        
        # Convert conditions to JSON string for data attribute (use single quotes to avoid escaping)
        conditions_json = json.dumps({
            "conditions": conditions,
            "logic": logic
        }).replace('"', "'")
        
        return {
            "data-conditions": conditions_json,
            "data-condition-logic": logic
        }