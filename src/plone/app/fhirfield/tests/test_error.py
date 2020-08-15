# _*_ coding: utf-8 _*_
import unittest

from plone.app.fhirfield.compat import FhirFieldValidationError
from plone.app.fhirfield.field import FhirResource
from plone.app.fhirfield.testing import PLONE_APP_FHIRFIELD_INTEGRATION_TESTING
from z3c.form.interfaces import IErrorViewSnippet
from z3c.form.interfaces import IValue
from zope.component import getMultiAdapter


__author__ = "Md Nazrul Islam <email2nazrul@gmail.com>"


class ErrorMessageTest(unittest.TestCase):

    """ """

    layer = PLONE_APP_FHIRFIELD_INTEGRATION_TESTING

    def setUp(self):
        """ """
        self.portal = self.layer["portal"]
        self.request = self.layer["request"]

    def test_custom_error_value(self):
        """ """
        field = FhirResource(
            title="", fhir_release="STU3", resource_type="Organization"
        )
        error = FhirFieldValidationError(("Error 1", "Error 2"))
        value = getMultiAdapter(
            (error, self.request, None, field, None, None), IValue, name="message"
        )
        self.assertEqual(value.func.__name__, "extract_error_message")

    def test_custom_error_view(self):
        """ """
        error = FhirFieldValidationError(("Error 1", "Error 2"))
        field = FhirResource(
            title="", fhir_release="STU3", resource_type="Organization"
        )
        view = getMultiAdapter(
            (error, self.request, None, field, None, None), IErrorViewSnippet
        )
        self.assertEqual(view.__class__.__name__, "FhirFieldErrorViewSnippet")
        # Let's prepare message
        view.update()

        self.assertEqual(
            view.render().strip().replace(" ", "").replace("\n", ""),
            '<divclass="error"><code>["Error1","Error2"]</code></div>',
        )

        # test with string value
        error = FhirFieldValidationError("I am string")
        view = getMultiAdapter(
            (error, self.request, None, field, None, None), IErrorViewSnippet
        )
        # Let's prepare message
        view.update()
        self.assertEqual(
            view.render().strip().replace(" ", "").replace("\n", ""),
            '<divclass="error">Iamstring</div>',
        )
