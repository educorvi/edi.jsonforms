# Endpoints

## View Methods (relevant for vue json form component)
- json-schema-view
- ui-schema-view

## API endpoints
- @json-schema (includes else-statement in the allOf attribute)

# Possible form types

## Field types

### Field
 - attributes of a field
   - title (required)
   - description
   - choice if the field is required (required)
   - answer type (required)
     - possible answer types: Textline, Textarea, Password, Telephone, URL, Email, Date, Date and time, Time, Decimal number, Whole number, Checkbox (yes/no)
   - intern information (for developers)
   - user helptext
   - dependencies and their connection type (and, or)
   - minimum (possible for number, integer, textline, textarea, password)
   - maximum (possible for same answer types)
   - unit (possible for number, integer)
   - placeholder (possible for textline, textarea, password)
   - pattern (possible for textline, textarea)

### Selection-field
 - attributes of a selection-field
   - title (required)
   - description
   - choice if the field is required (required)
   - answer type (required)
     - possible answer types: Radiobuttons (single selection), Checkboxes (multi-selection), Selection (single selection), Selection (multi-selection)
   - intern information (for developers)
   - user helptext
   - dependencies and their connection type (and, or)

### Upload-field
 - attributes of an upload-field
   - title (required)
   - description
   - choice if the field is required (required)
   - answer type (required)
     - possible answer types: File upload (single upload), File upload (multi-upload)
   - intern information (for developers)
   - user helptext
   - dependencies and their connection type (and, or)
   - accepted file types
     - possible accepted file types: jpg, png, pdf, gif, docx

## Container types

### Fieldset
 - title
 - description
 - dependencies and their connection type (and, or)
 - intern information (for developers)

### Complex
 - title
 - description
 - dependencies and their connection type (and, or)
 - intern information (for developers)

### Array
 - title
 - description
 - dependencies and their connection type (and, or)
 - intern information (for developers)
 - choice if the field is required (required)


## Additional Features

### Show Conditions
 - one can specify that a field etc. is only shown if ?fork=condition is specified in the url
 - it has to be specified in the attribute "Condition for showing this field" in the tab "Additional Information"

### Override Options
 - the add-on edi.jsonforms.override must be installed
 - attributes can be overriden by specifying new values in the tab "Override Options". These only override the original attribute if ?fork=condition is specified in the url
 - attributes that can be overridden:
   - title
   - description
   - hint/helptext for the user
   - unit (in case a unit is possible)
   - placeholder (in case a placeholder is possible)