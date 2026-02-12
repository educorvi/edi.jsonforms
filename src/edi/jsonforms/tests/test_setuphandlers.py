# -*- coding: utf-8 -*-
"""Tests for setuphandlers."""
from edi.jsonforms.setuphandlers import HiddenProfiles
from edi.jsonforms.setuphandlers import post_install
from edi.jsonforms.setuphandlers import uninstall
from edi.jsonforms.testing import EDI_JSONFORMS_INTEGRATION_TESTING
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID

import unittest


class SetupHandlersTest(unittest.TestCase):
    """Test setuphandlers."""

    layer = EDI_JSONFORMS_INTEGRATION_TESTING

    def setUp(self):
        """Custom shared utility setup for tests."""
        self.portal = self.layer['portal']
        setRoles(self.portal, TEST_USER_ID, ['Manager'])

    def test_hidden_profiles_returns_uninstall_profile(self):
        """Test that HiddenProfiles hides the uninstall profile."""
        hidden = HiddenProfiles()
        profiles = hidden.getNonInstallableProfiles()
        
        self.assertIn('edi.jsonforms:uninstall', profiles)

    def test_hidden_profiles_returns_upgrades_product(self):
        """Test that HiddenProfiles hides the upgrades product."""
        hidden = HiddenProfiles()
        products = hidden.getNonInstallableProducts()
        
        self.assertIn('edi.jsonforms.upgrades', products)

    def test_post_install_callable(self):
        """Test that post_install is callable."""
        # Should not raise an error
        post_install(self.portal)

    def test_uninstall_callable(self):
        """Test that uninstall is callable."""
        # Should not raise an error
        uninstall(self.portal)
