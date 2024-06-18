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
   - placeholder (possible for textline, textare, password)
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
