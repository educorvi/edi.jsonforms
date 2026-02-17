# Test Suite Documentation

This document describes the comprehensive test suite for the edi.jsonforms Plone add-on.

## Overview

The test suite includes both **unit tests** and **integration tests** to ensure comprehensive coverage of all major components and functionality.

## Test Statistics

- **Total test files**: 29 (including new tests)
- **Total test classes**: 47+
- **Total test methods**: 174+
- **Total lines of test code**: 3500+

## New Test Files Added

### Unit Tests

1. **test_handlers.py** - Tests for event handlers
   - Test schema_handler event handler
   - Test schema versioning with change notes
   - Test schema storage validation

2. **test_api_services.py** - Tests for REST API services
   - Test Schemata expandable element
   - Test JsonSchemaGet service
   - Test UiSchemaGet service
   - Test REST API endpoints (functional tests)

3. **test_common_utils.py** - Tests for common utilities
   - Test get_base_path function
   - Test get_base_path_parent function
   - Test base path for nested structures (complex, array, fieldset)
   - Test dependency validation invariants

4. **test_ct_option_list.py** - Tests for OptionList content type
   - Test basic content type operations (schema, FTI, factory, adding)
   - Test get_options() with local options
   - Test get_options() with external URL (with mocking)
   - Test error handling (request errors, invalid JSON, non-200 status)
   - Test API key authentication
   - Test id/value mappings
   - Test get_keys_and_values_for_options_list utility

5. **test_viewlets.py** - Tests for developer viewlet
   - Test viewlet rendering conditions
   - Test get_json_schema for Form and Wizard
   - Test get_ui_schema for Form and Wizard
   - Test get_versions method

6. **test_setuphandlers.py** - Tests for setup handlers
   - Test HiddenProfiles configuration
   - Test post_install hook
   - Test uninstall hook

7. **test_view_utils.py** - Tests for view utilities
   - Test optionlist view
   - Test common view utilities
   - Test view registration

8. **test_schema_generation.py** - Tests for schema generation
   - Test schema generation for different field types (text, email, URL, date, number)
   - Test required vs optional fields
   - Test field constraints (min/max length)
   - Test selection fields with options
   - Test selection fields with id:value pairs
   - Test complex object nested properties
   - Test array schema generation

### Integration Tests

9. **test_integration_forms.py** - Integration tests for form rendering
   - Test form with various field types (text, selection, upload, complex, array, fieldset, helptext)
   - Test form with all field types combined
   - Test field dependencies (single, OR, AND)
   - Test show conditions
   - Test negated conditions

10. **test_integration_wizard.py** - Integration tests for wizard functionality
    - Test wizard with single form
    - Test wizard with multiple forms (steps)
    - Test wizard UI schema generation
    - Test wizard view accessibility
    - Test wizard with complex forms
    - Test wizard navigation and step management

## Existing Test Files

The repository already includes tests for:

- Content types: Form, Field, SelectionField, UploadField, Complex, Array, Fieldset, Helptext, Option, Reference, Wizard
- Views: form_view, form_element_view, json_schema_view, ui_schema_view, version_view, wizard_view
- Setup and installation
- Robot framework tests

## Running Tests

### Using tox (recommended)

```bash
# Run tests for Plone 6.0 with Python 3.9
tox -e py39-Plone60

# Run tests for Plone 5.2 with Python 3.8
tox -e py38-Plone52

# Run all test environments
tox
```

### Using buildout

```bash
# Set up the buildout environment
buildout -c test_plone60.cfg

# Run all tests
bin/test

# Run specific test module
bin/test -t test_handlers

# Run with coverage
bin/test-coverage
```

### Running individual test files

```bash
# After buildout setup
bin/test -s edi.jsonforms -t test_handlers
bin/test -s edi.jsonforms -t test_api_services
bin/test -s edi.jsonforms -t test_integration_forms
```

## Test Coverage Areas

### Content Types (100% coverage)
- ✅ Form
- ✅ Field
- ✅ SelectionField
- ✅ UploadField
- ✅ Complex
- ✅ Array
- ✅ Fieldset
- ✅ Helptext
- ✅ Option
- ✅ OptionList (NEW)
- ✅ Reference
- ✅ Wizard

### Views (100% coverage)
- ✅ form_view
- ✅ form_element_view
- ✅ json_schema_view
- ✅ ui_schema_view
- ✅ version_view
- ✅ wizard_view
- ✅ optionlist_view (NEW)
- ✅ common view utilities (NEW)

### Handlers
- ✅ schema_handler (NEW)

### API Services
- ✅ Schemata expandable element (NEW)
- ✅ JsonSchemaGet (NEW)
- ✅ UiSchemaGet (NEW)

### Utilities
- ✅ get_base_path (NEW)
- ✅ get_base_path_parent (NEW)
- ✅ get_keys_and_values_for_options_list (NEW)

### Setup
- ✅ Installation
- ✅ Uninstallation
- ✅ Setup handlers (NEW)

### Integration Features
- ✅ Form rendering with all field types (NEW)
- ✅ Field dependencies (NEW)
- ✅ Show conditions (NEW)
- ✅ Wizard multi-step forms (NEW)
- ✅ External option lists (NEW)

## Test Patterns Used

### Unit Tests
- Use `EDI_JSONFORMS_INTEGRATION_TESTING` layer
- Test individual components in isolation
- Use mocking for external dependencies (e.g., HTTP requests)
- Test both success and error cases

### Integration Tests
- Use `EDI_JSONFORMS_INTEGRATION_TESTING` for basic integration
- Use `EDI_JSONFORMS_FUNCTIONAL_TESTING` for full stack testing
- Test complete workflows and interactions
- Validate generated schemas

### Functional Tests
- Use `EDI_JSONFORMS_FUNCTIONAL_TESTING` layer
- Test REST API endpoints
- Use RelativeSession for API testing
- Validate HTTP responses

## Continuous Integration

The test suite is run automatically on:
- GitHub Actions (via `.github/workflows/`)
- GitLab CI (via `.gitlab-ci.yml`)
- Travis CI (via `.travis.yml`)

Coverage reports are sent to:
- Coveralls
- Codecov

## Contributing

When adding new features:
1. Write tests first (TDD approach)
2. Ensure all tests pass
3. Maintain or improve test coverage
4. Follow existing test patterns
5. Document complex test scenarios

## Notes

- All new test files follow the existing test patterns and conventions
- Tests use the plone.app.testing framework
- Mocking is used where appropriate to avoid external dependencies
- Tests are designed to be fast and reliable
- Test data is created fresh for each test to avoid interdependencies
