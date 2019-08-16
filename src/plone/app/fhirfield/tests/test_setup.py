# -*- coding: utf-8 -*-
"""Setup tests for this package."""
import unittest

from plone.app.fhirfield.testing import PLONE_APP_FHIRFIELD_INTEGRATION_TESTING
from Products.CMFPlone.interfaces import INonInstallable
from Products.CMFPlone.utils import get_installer
from zope.component import queryUtility


class TestSetup(unittest.TestCase):
    """Test that plone.app.fhirfield is properly installed."""

    layer = PLONE_APP_FHIRFIELD_INTEGRATION_TESTING

    def setUp(self):
        """Custom shared utility setup for tests."""
        self.portal = self.layer["portal"]
        self.installer = get_installer(self.portal, self.layer["request"])

    def test_product_installed(self):
        """Test if plone.app.fhirfield is installed."""
        self.assertTrue(self.installer.is_product_installed("plone.app.fhirfield"))


class TestUninstall(unittest.TestCase):

    layer = PLONE_APP_FHIRFIELD_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer["portal"]
        self.installer = get_installer(self.portal, self.layer["request"])
        self.installer.uninstall_product("plone.app.fhirfield")

    def test_product_uninstalled(self):
        """Test if plone.app.fhirfield is cleanly uninstalled."""
        self.assertFalse(self.installer.is_product_installed("plone.app.fhirfield"))

    def test_hidden_profiled(self):
        """Test if plone.app.fhirfield hidden profile utility is available"""

        utility = queryUtility(
            INonInstallable, name="plone.app.fhirfield-hiddenprofiles"
        )

        self.assertIsNotNone(utility)
        self.assertIn(
            "plone.app.fhirfield:uninstall", utility.getNonInstallableProfiles()
        )
