# Test Suite for edi.jsonforms

This directory contains comprehensive unit and integration tests for the edi.jsonforms Plone add-on.

## Quick Stats

- **Total test files**: 32
- **New test files added**: 10
- **New test methods added**: 84+
- **Test coverage areas**: Content types, Views, Handlers, API services, Utilities, Integration workflows

## New Test Files

### Unit Tests

| File | Purpose | Test Count |
|------|---------|------------|
| `test_handlers.py` | Event handlers and schema versioning | 3 |
| `test_api_services.py` | REST API services and endpoints | 8 |
| `test_common_utils.py` | Common utility functions and dependencies | 8 |
| `test_ct_option_list.py` | OptionList content type with external API support | 13 |
| `test_viewlets.py` | Developer viewlet functionality | 11 |
| `test_setuphandlers.py` | Setup and installation handlers | 4 |
| `test_view_utils.py` | View utilities and registration | 4 |
| `test_schema_generation.py` | JSON schema generation for all field types | 17 |

### Integration Tests

| File | Purpose | Test Count |
|------|---------|------------|
| `test_integration_forms.py` | Form rendering and field dependencies | 11 |
| `test_integration_wizard.py` | Wizard multi-step functionality | 7 |

## Running Tests

### Quick Start

```bash
# Run all tests
bin/test

# Run specific test file
bin/test -t test_handlers

# Run with coverage
bin/test-coverage
```

### Using tox

```bash
# Run tests for Plone 6.0
tox -e py39-Plone60

# Run all environments
tox
```

## Test Organization

### Test Layers

- **EDI_JSONFORMS_INTEGRATION_TESTING** - Used for most unit and integration tests
- **EDI_JSONFORMS_FUNCTIONAL_TESTING** - Used for full-stack functional tests
- **EDI_JSONFORMS_ACCEPTANCE_TESTING** - Used for robot framework tests

### Test Patterns

All tests follow these patterns:
1. Import the testing layer
2. Create a test class inheriting from `unittest.TestCase`
3. Set the appropriate layer
4. Implement `setUp()` to create test fixtures
5. Write test methods starting with `test_`
6. Clean up is handled automatically by the testing framework

### Example Test

```python
from edi.jsonforms.testing import EDI_JSONFORMS_INTEGRATION_TESTING
from plone import api
from plone.app.testing import setRoles, TEST_USER_ID
import unittest

class MyTest(unittest.TestCase):
    layer = EDI_JSONFORMS_INTEGRATION_TESTING
    
    def setUp(self):
        self.portal = self.layer['portal']
        setRoles(self.portal, TEST_USER_ID, ['Manager'])
        
    def test_something(self):
        # Your test code here
        self.assertTrue(True)
```

## What's Tested

### Content Types ✅
- Form, Field, SelectionField, UploadField
- Complex, Array, Fieldset, Helptext
- Option, OptionList, Reference, Wizard

### Views ✅
- Form views, Schema views, Wizard views
- Form element views, Version views
- Option list views

### Handlers ✅
- Schema handler (versioning on change)

### API Services ✅
- Schemata expandable element
- JSON Schema GET endpoint
- UI Schema GET endpoint

### Utilities ✅
- Base path utilities
- Dependency validation
- Option list processing

### Integration Features ✅
- Complete form rendering
- Field dependencies (OR/AND)
- Show conditions
- Wizard multi-step forms
- External option lists with API auth

## Mocking External Dependencies

External HTTP requests are mocked using `unittest.mock`:

```python
from unittest.mock import Mock, patch

@patch('requests.get')
def test_external_api(self, mock_get):
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.text = json.dumps([...])
    mock_get.return_value = mock_response
    # Test code here
```

## Contributing

When adding new features:

1. **Write tests first** (Test-Driven Development)
2. **Follow existing patterns** for consistency
3. **Test both success and error cases**
4. **Use appropriate test layers**
5. **Mock external dependencies**
6. **Keep tests isolated** - each test should work independently
7. **Use descriptive test names** - `test_field_with_dependency_validates_correctly`

## Coverage Goals

- Maintain >80% code coverage
- All new code must have tests
- All bug fixes must include regression tests
- Integration tests for all major workflows

## See Also

- [TEST_SUITE.md](../../docs/TEST_SUITE.md) - Detailed test suite documentation
- [DEVELOP.rst](../../DEVELOP.rst) - Development guidelines
- [README.rst](../../README.rst) - Project overview
