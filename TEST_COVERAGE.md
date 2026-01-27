# Test Coverage Documentation

This document describes the comprehensive test suite for edi.jsonforms.

## Overview

The test suite has been expanded to provide comprehensive coverage of all major components in the edi.jsonforms package. The tests are organized by component type and functionality.

## Test Organization

### Content Type Tests

These tests verify that all Dexterity content types are properly configured and functional:

- `test_ct_array.py` - Tests for Array content type
- `test_ct_complex.py` - Tests for Complex content type
- `test_ct_field.py` - Tests for Field content type
- `test_ct_fieldset.py` - Tests for Fieldset content type
- `test_ct_form.py` - Tests for Form content type
- `test_ct_helptext.py` - Tests for Helptext content type
- `test_ct_option.py` - Tests for Option content type
- **`test_ct_option_list.py`** - NEW: Tests for OptionList content type and utility functions
- `test_ct_reference.py` - Tests for Reference content type
- `test_ct_selection_field.py` - Tests for SelectionField content type
- `test_ct_upload_field.py` - Tests for UploadField content type
- `test_ct_wizard.py` - Tests for Wizard content type

### View Tests

These tests verify that views render correctly and generate valid schemas:

- `test_view_form_element_view.py` - Tests for form element views
- `test_view_form_view.py` - Tests for form views
- `test_view_json_schema_view.py` - Tests for JSON schema generation
- `test_view_ui_schema_view.py` - Tests for UI schema generation
- **`test_ui_schema_tools_view.py`** - NEW: Tests for UI schema tools view
- `test_view_version_view.py` - Tests for version views
- `test_view_wizard_view.py` - Tests for wizard views

### API Service Tests

**`test_api_services.py`** - NEW: Comprehensive tests for REST API services:
- `@json-schema` endpoint
- `@ui-schema` endpoint
- `@schemata` endpoint
- Schema generation with fields
- Extended schema mode

### Handler Tests

**`test_handlers.py`** - NEW: Tests for event handlers:
- Schema handler for versioning
- Change note handling
- Schema preservation during modifications

### Utility Function Tests

**`test_common_utilities.py`** - NEW: Tests for common utility functions:
- `create_id()` function
- `get_base_path()` function
- `get_base_path_parent()` function
- Path resolution in nested structures

### ShowOn Properties Tests

**`test_showon_properties.py`** - NEW: Tests for conditional visibility functionality:
- `find_scope()` function
- `transform_scope_to_object_writing_form()` function
- Scope calculation for nested fields
- Caching behavior

### Viewlet Tests

**`test_viewlets.py`** - NEW: Tests for developer viewlet:
- Viewlet rendering conditions
- JSON schema generation
- UI schema generation
- Version history handling
- Support for both Form and Wizard types

### Integration Tests

**`test_integration_nested_structures.py`** - NEW: Integration tests for complex nested structures:
- Fieldset with fields
- Complex objects with fields
- Arrays with fields
- Deeply nested structures (Fieldset > Complex > Array > Field)
- Multiple nested structures
- Selection fields with options in nested structures

**`test_integration_dependencies.py`** - NEW: Integration tests for dependencies and required fields:
- Required field validation
- Optional field handling
- Multiple required fields
- Required selection fields
- Required upload fields
- Required arrays
- DependentRequired structure
- Field dependencies
- Required fields in nested structures
- Mixed required and optional fields in complex objects

### Edge Case Tests

**`test_edge_cases.py`** - NEW: Tests for edge cases and boundary conditions:
- Empty form schemas
- Fields with empty titles
- Fields with very long titles (1000+ characters)
- Special characters in titles
- Unicode characters in titles
- Selection fields with no options
- Fields with minimum equal to maximum
- Fields with minimum greater than maximum
- Nested empty structures
- Arrays with no items
- Performance with many fields (50+)
- Deeply nested structures (5+ levels)
- Options with empty titles
- Forms with only helptext elements

### Setup Tests

- `test_setup.py` - Tests for package installation and uninstallation
- `test_robot.py` - Robot framework tests

## Test Layers

The test suite uses Plone testing layers:

- `EDI_JSONFORMS_INTEGRATION_TESTING` - For integration tests that require the full Plone stack
- `EDI_JSONFORMS_FUNCTIONAL_TESTING` - For functional tests (where applicable)

## Running Tests

### Run all tests

```bash
tox
```

### Run tests for a specific Python/Plone version

```bash
tox -e py39-Plone60
```

### List all available test environments

```bash
tox -l
```

### Run tests with coverage

Coverage is automatically generated when running tests through tox. After running tests, generate a coverage report:

```bash
tox -e coverage-report
```

## Test Coverage Goals

The expanded test suite aims to achieve:

1. **Content Type Coverage**: All content types have comprehensive tests for:
   - Schema validation
   - FTI (Factory Type Information) registration
   - Factory creation
   - Adding/deleting instances
   - Global addability settings
   - Content type specific functionality

2. **View Coverage**: All views have tests for:
   - View registration
   - Schema generation (JSON and UI)
   - Handling of different field types
   - Nested structures
   - Edge cases

3. **API Coverage**: All REST API endpoints have tests for:
   - Registration
   - Valid response structure
   - Schema generation with content
   - Extended modes

4. **Handler Coverage**: Event handlers are tested for:
   - Correct behavior with events
   - Data preservation
   - Error handling

5. **Utility Coverage**: Utility functions are tested for:
   - Correct output
   - Edge cases
   - Performance
   - Nested structure handling

6. **Integration Coverage**: Complex scenarios are tested including:
   - Multi-level nesting
   - Dependencies between fields
   - Required field handling
   - Schema consistency

7. **Edge Case Coverage**: Unusual inputs and boundary conditions:
   - Empty values
   - Very large values
   - Special characters
   - Unicode support
   - Performance limits

## Continuous Integration

The tests are automatically run on GitHub Actions for multiple Python and Plone versions. See `.github/workflows/` for CI configuration.

## Contributing

When adding new features:

1. Add tests for the new functionality
2. Ensure existing tests still pass
3. Update this documentation if adding new test files
4. Aim for high test coverage (>80%)

## Test Quality Standards

All tests should:

- Have descriptive names explaining what they test
- Include docstrings explaining the test purpose
- Test one specific behavior or condition
- Be independent and not rely on test execution order
- Clean up after themselves
- Use appropriate assertions
- Handle expected failures gracefully
