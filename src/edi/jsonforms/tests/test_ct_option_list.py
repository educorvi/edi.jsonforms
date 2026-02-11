# -*- coding: utf-8 -*-
"""Tests for OptionList content type."""
from edi.jsonforms.content.option_list import IOptionList
from edi.jsonforms.content.option_list import get_keys_and_values_for_options_list
from edi.jsonforms.testing import EDI_JSONFORMS_INTEGRATION_TESTING
from plone import api
from plone.api.exc import InvalidParameterError
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from plone.dexterity.interfaces import IDexterityFTI
from unittest.mock import Mock, patch
from zope.component import createObject
from zope.component import queryUtility

import json
import unittest


class OptionListIntegrationTest(unittest.TestCase):
    """Test OptionList content type."""

    layer = EDI_JSONFORMS_INTEGRATION_TESTING

    def setUp(self):
        """Custom shared utility setup for tests."""
        self.portal = self.layer['portal']
        setRoles(self.portal, TEST_USER_ID, ['Manager'])
        self.parent = self.portal

    def test_ct_option_list_schema(self):
        """Test that OptionList schema is properly defined."""
        fti = queryUtility(IDexterityFTI, name='OptionList')
        schema = fti.lookupSchema()
        self.assertEqual(IOptionList, schema)

    def test_ct_option_list_fti(self):
        """Test that OptionList FTI exists."""
        fti = queryUtility(IDexterityFTI, name='OptionList')
        self.assertTrue(fti)

    def test_ct_option_list_factory(self):
        """Test that OptionList can be created via factory."""
        fti = queryUtility(IDexterityFTI, name='OptionList')
        factory = fti.factory
        obj = createObject(factory)

        self.assertTrue(
            IOptionList.providedBy(obj),
            u'IOptionList not provided by {0}!'.format(obj),
        )

    def test_ct_option_list_adding(self):
        """Test adding OptionList content."""
        setRoles(self.portal, TEST_USER_ID, ['Contributor'])
        obj = api.content.create(
            container=self.portal,
            type='OptionList',
            id='option_list',
            title='Test Option List'
        )

        self.assertTrue(
            IOptionList.providedBy(obj),
            u'IOptionList not provided by {0}!'.format(obj.id),
        )

        parent = obj.__parent__
        self.assertIn('option_list', parent.objectIds())

        # Check that deleting the object works too
        api.content.delete(obj=obj)
        self.assertNotIn('option_list', parent.objectIds())

    def test_get_options_returns_local_options(self):
        """Test that get_options returns local options when no URL is set."""
        obj = api.content.create(
            container=self.portal,
            type='OptionList',
            id='option_list',
            title='Test Option List'
        )
        
        test_options = ['option1', 'option2', 'id1:value1']
        obj.options = test_options
        
        result = obj.get_options()
        
        self.assertEqual(result, test_options)

    @patch('requests.get')
    def test_get_options_fetches_from_url(self, mock_get):
        """Test that get_options fetches from external URL."""
        obj = api.content.create(
            container=self.portal,
            type='OptionList',
            id='option_list',
            title='Test Option List'
        )
        
        # Set up URL
        obj.url = 'https://example.com/api/options'
        obj.timeout = 3
        
        # Mock the response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = json.dumps([
            {'id': '1', 'name': 'Option 1'},
            {'id': '2', 'name': 'Option 2'}
        ])
        mock_get.return_value = mock_response
        
        result = obj.get_options()
        
        # Should return formatted options
        self.assertIsInstance(result, list)
        self.assertGreater(len(result), 0)

    @patch('requests.get')
    def test_get_options_handles_request_error(self, mock_get):
        """Test that get_options handles request errors gracefully."""
        obj = api.content.create(
            container=self.portal,
            type='OptionList',
            id='option_list',
            title='Test Option List'
        )
        
        obj.url = 'https://example.com/api/options'
        obj.timeout = 3
        
        # Mock a request exception
        import requests
        mock_get.side_effect = requests.RequestException('Connection error')
        
        result = obj.get_options()
        
        # Should return empty list on error
        self.assertEqual(result, [])

    @patch('requests.get')
    def test_get_options_handles_non_200_status(self, mock_get):
        """Test that get_options handles non-200 status codes."""
        obj = api.content.create(
            container=self.portal,
            type='OptionList',
            id='option_list',
            title='Test Option List'
        )
        
        obj.url = 'https://example.com/api/options'
        obj.timeout = 3
        
        # Mock a 404 response
        mock_response = Mock()
        mock_response.status_code = 404
        mock_get.return_value = mock_response
        
        result = obj.get_options()
        
        # Should return empty list on non-200 status
        self.assertEqual(result, [])

    @patch('requests.get')
    def test_get_options_handles_invalid_json(self, mock_get):
        """Test that get_options handles invalid JSON responses."""
        obj = api.content.create(
            container=self.portal,
            type='OptionList',
            id='option_list',
            title='Test Option List'
        )
        
        obj.url = 'https://example.com/api/options'
        obj.timeout = 3
        
        # Mock an invalid JSON response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = 'not valid json'
        mock_get.return_value = mock_response
        
        result = obj.get_options()
        
        # Should return empty list on invalid JSON
        self.assertEqual(result, [])

    @patch('requests.get')
    def test_get_options_with_api_key(self, mock_get):
        """Test that get_options sends API key in headers."""
        obj = api.content.create(
            container=self.portal,
            type='OptionList',
            id='option_list',
            title='Test Option List'
        )
        
        obj.url = 'https://example.com/api/options'
        obj.timeout = 3
        obj.api_key_name = 'Authorization'
        obj.api_key = 'Bearer test-token'
        
        # Mock the response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = json.dumps([{'id': '1', 'name': 'Option 1'}])
        mock_get.return_value = mock_response
        
        obj.get_options()
        
        # Check that the API key was sent in headers
        mock_get.assert_called_once()
        call_args = mock_get.call_args
        headers = call_args.kwargs.get('headers', {})
        self.assertIn('Authorization', headers)
        self.assertEqual(headers['Authorization'], 'Bearer test-token')

    @patch('requests.get')
    def test_get_options_with_mapping(self, mock_get):
        """Test that get_options uses id and value mappings."""
        obj = api.content.create(
            container=self.portal,
            type='OptionList',
            id='option_list',
            title='Test Option List'
        )
        
        obj.url = 'https://example.com/api/options'
        obj.timeout = 3
        obj.id_mapping = 'id'
        obj.value_mapping = 'name'
        
        # Mock the response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = json.dumps([
            {'id': '1', 'name': 'Option 1'},
            {'id': '2', 'name': 'Option 2'}
        ])
        mock_get.return_value = mock_response
        
        result = obj.get_options()
        
        # Should format options using mappings
        self.assertIsInstance(result, list)
        self.assertGreater(len(result), 0)
        # Check format is "id:value"
        for option in result:
            self.assertIn(':', option)

    def test_get_keys_and_values_for_options_list(self):
        """Test get_keys_and_values_for_options_list utility function."""
        obj = api.content.create(
            container=self.portal,
            type='OptionList',
            id='option_list',
            title='Test Option List'
        )
        
        obj.options = ['key1:value1', 'key2:value2', 'simple_option']
        
        keys, values = get_keys_and_values_for_options_list(obj)
        
        self.assertEqual(keys, ['key1', 'key2', 'simple_option'])
        self.assertEqual(values, ['value1', 'value2', 'simple_option'])

    def test_get_keys_and_values_handles_colon_in_value(self):
        """Test that get_keys_and_values handles colons in values."""
        obj = api.content.create(
            container=self.portal,
            type='OptionList',
            id='option_list',
            title='Test Option List'
        )
        
        obj.options = ['key1:value:with:colons', 'key2:value2']
        
        keys, values = get_keys_and_values_for_options_list(obj)
        
        self.assertEqual(keys, ['key1', 'key2'])
        self.assertEqual(values, ['value:with:colons', 'value2'])
