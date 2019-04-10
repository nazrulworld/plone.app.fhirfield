# _*_ coding: utf-8 _*_
from __future__ import print_function  # noqa: I001
from . import FHIR_FIXTURE_PATH
from .schema import IFFOrganization
from plone.app.fhirfield import widget
from plone.app.fhirfield.testing import PLONE_APP_FHIRFIELD_FUNCTIONAL_TESTING
from plone.app.fhirfield.testing import PLONE_APP_FHIRFIELD_INTEGRATION_TESTING
from plone.app.fhirfield.value import FhirResourceValue
from plone.app.testing import SITE_OWNER_NAME
from plone.app.testing import SITE_OWNER_PASSWORD
from plone.testing import z2
from z3c.form.interfaces import IDataConverter
from z3c.form.interfaces import IFieldWidget
from z3c.form.interfaces import NOVALUE
from zope.component import queryMultiAdapter
from zope.publisher.browser import TestRequest
from zope.schema import getFields

import json
import os
import unittest


___author__ = "Md Nazrul Islam<email2nazrul@gmail.com>"


class WidgetIntegrationTest(unittest.TestCase):
    """ """

    layer = PLONE_APP_FHIRFIELD_INTEGRATION_TESTING

    def setUp(self):
        """ """
        self.portal = self.layer["portal"]
        self.request = self.layer["request"]

    def test_widget(self):
        """ """
        with open(os.path.join(FHIR_FIXTURE_PATH, "Organization.json"), "r") as f:
            fhir_str = f.read()

        request = TestRequest(form={"organization_resource": fhir_str})
        fhir_widget = widget.FhirResourceWidget(request)
        fhir_widget.name = "organization_resource"
        self.assertTrue(widget.IFhirResourceWidget.providedBy(fhir_widget))
        self.assertIsNone(fhir_widget.value)
        fhir_widget.update()
        self.assertEqual(fhir_widget.value, fhir_str)
        fhir_field = getFields(IFFOrganization)["organization_resource"]

        field_widget = widget.FhirResourceFieldWidget(fhir_field, request)
        self.assertTrue(IFieldWidget.providedBy(field_widget))
        # @TODO: Make sure widget.render() works!

    def test_data_converter(self):
        """ """
        with open(os.path.join(FHIR_FIXTURE_PATH, "Organization.json"), "r") as f:
            fhir_str = f.read()
        request = TestRequest(form={"organization_resource": fhir_str})
        fhir_field = getFields(IFFOrganization)["organization_resource"]
        field_widget = widget.FhirResourceFieldWidget(fhir_field, request)

        converter = queryMultiAdapter((fhir_field, field_widget), IDataConverter)
        self.assertIsNotNone(converter)

        # All Test: toWidgetValue
        fhir_value = converter.toWidgetValue("")
        self.assertFalse(fhir_value)
        self.assertIsInstance(fhir_value, FhirResourceValue)

        fhir_value = converter.toWidgetValue(fhir_str)
        self.assertIn(fhir_value.as_json()["resourceType"], fhir_str)

        try:
            converter.toWidgetValue(("hello", "wrong type"))
            raise AssertionError(
                "Code should not come here! As wrong types data is provided"
            )
        except ValueError as exc:
            self.assertIn("IFhirResourceValue", str(exc))

        # All Test: toFieldValue
        fhir_value = converter.toFieldValue(NOVALUE)
        self.assertFalse(fhir_value)
        self.assertIsInstance(fhir_value, FhirResourceValue)

        fhir_value = converter.toFieldValue(fhir_str)
        self.assertIn(fhir_value.as_json()["resourceType"], fhir_str)

        fhir_value2 = converter.toFieldValue(fhir_value)
        self.assertEqual(fhir_value, fhir_value2)

        try:
            converter.toFieldValue(("hello", "wrong type"))
            raise AssertionError(
                "Code should not come here! As wrong types data is provided"
            )
        except ValueError as exc:
            self.assertIn("IFhirResourceValue", str(exc))

    def test_textarea_data_converter(self):
        """ """
        from z3c.form.browser.textarea import TextAreaWidget

        with open(os.path.join(FHIR_FIXTURE_PATH, "Organization.json"), "r") as f:
            fhir_str = f.read()
        request = TestRequest(form={"organization_resource": fhir_str})
        fhir_field = getFields(IFFOrganization)["organization_resource"]
        field_widget = TextAreaWidget(request)

        converter = queryMultiAdapter((fhir_field, field_widget), IDataConverter)
        self.assertIsNotNone(converter)

        # All Test: toFieldValue
        fhir_value_empty = converter.toFieldValue(NOVALUE)
        self.assertFalse(fhir_value_empty)
        self.assertIsInstance(fhir_value_empty, FhirResourceValue)

        fhir_value = converter.toFieldValue(fhir_str)
        self.assertIn(fhir_value.as_json()["resourceType"], fhir_str)

        fhir_value2 = converter.toFieldValue(fhir_value)
        self.assertEqual(fhir_value, fhir_value2)

        try:
            converter.toFieldValue(("hello", "wrong type"))
            raise AssertionError(
                "Code should not come here! As wrong types data is provided"
            )
        except ValueError as exc:
            self.assertIn("IFhirResourceValue", str(exc))

        # All Test: toWidgetValue
        fhir_value = converter.toWidgetValue("")
        self.assertFalse(fhir_value)
        self.assertEqual("", "")

        fhir_value_1 = converter.toWidgetValue(fhir_str)
        self.assertIn("Organization", fhir_value_1)
        self.assertIn("resourceType", fhir_value_1)

        fhir_value_2 = converter.toWidgetValue(fhir_value2)
        self.assertEqual(json.loads(fhir_value_1), json.loads(fhir_value_2))

        converter.widget.mode = "display"

        fhir_value_3 = converter.toWidgetValue(fhir_value_empty)
        self.assertEqual(fhir_value_3, "")

        try:
            converter.toWidgetValue(("hello", "wrong type"))
            raise AssertionError(
                "Code should not come here! As wrong types data is provided"
            )
        except ValueError as exc:
            self.assertIn("Can not convert", str(exc))


class WidgetFunctionalTest(unittest.TestCase):
    """ """

    layer = PLONE_APP_FHIRFIELD_FUNCTIONAL_TESTING

    def setUp(self):
        """ """
        self.portal = self.layer["portal"]
        self.portal_url = self.portal.absolute_url()
        self.browser = z2.Browser(self.layer["app"])
        self.error_setup()

    def error_setup(self):
        """ """
        self.browser.handleErrors = False
        self.portal.error_log._ignored_exceptions = ()

        def raising(self, info):
            import traceback

            traceback.print_tb(info[2])
            print(info[1])

        from Products.SiteErrorLog.SiteErrorLog import SiteErrorLog

        SiteErrorLog.raising = raising

    def login_as_admin(self):
        """ Perform through-the-web login."""

        # Go admin
        browser = self.browser
        browser.open(self.portal_url + "/login_form")
        browser.getControl(name="__ac_name").value = SITE_OWNER_NAME
        browser.getControl(name="__ac_password").value = SITE_OWNER_PASSWORD
        browser.getControl(name="submit").click()

    def test_widget(self):
        """" """
        self.login_as_admin()

        with open(os.path.join(FHIR_FIXTURE_PATH, "Organization.json"), "r") as f:
            fhir_str = f.read()

        browser = self.browser
        browser.open(self.portal_url + "/++add++FFOrganization")
        # ** CONTROLS
        # for x in browser.getForm(index=1).mech_form.controls: print  x.name
        # form.widgets.IBasic.title
        # form.widgets.IBasic.description
        # form.widgets.IDublinCore.title
        # form.widgets.IDublinCore.description
        # form.widgets.organization_resource
        # form.widgets.IDublinCore.subjects
        # form.widgets.IDublinCore.language:list
        # form.widgets.IDublinCore.language-empty-marker
        # form.widgets.IDublinCore.effective-day
        # form.widgets.IDublinCore.effective-month
        # form.widgets.IDublinCore.effective-year
        # form.widgets.IDublinCore.effective-calendar
        # form.widgets.IDublinCore.effective-hour
        # form.widgets.IDublinCore.effective-minute
        # form.widgets.IDublinCore.effective-timezone
        # form.widgets.IDublinCore.effective-empty-marker
        # form.widgets.IDublinCore.expires-day
        # form.widgets.IDublinCore.expires-month
        # form.widgets.IDublinCore.expires-year
        # form.widgets.IDublinCore.expires-calendar
        # form.widgets.IDublinCore.expires-hour
        # form.widgets.IDublinCore.expires-minute
        # form.widgets.IDublinCore.expires-timezone
        # form.widgets.IDublinCore.expires-empty-marker
        # form.widgets.IDublinCore.creators
        # form.widgets.IDublinCore.contributors
        # form.widgets.IDublinCore.rights
        # form.buttons.save
        # form.buttons.cancel
        browser.getControl(name="form.widgets.organization_resource").value = fhir_str
        browser.getControl(name="form.buttons.save").click()
        # There must be form error! as required title is missing so url is unchanged
        self.assertEqual(
            browser.mech_browser.geturl(), self.portal_url + "/++add++FFOrganization"
        )
        # Test Value exist, even form resubmit
        self.assertEqual(
            json.loads(
                browser.getControl(name="form.widgets.organization_resource").value
            ),
            json.loads(fhir_str),
        )

        # Let's fullfill required
        browser.getControl(
            name="form.widgets.IBasic.title"
        ).value = "hello organization"
        # After solving that problem, this again value assign not need
        browser.getControl(name="form.widgets.organization_resource").value = fhir_str
        browser.getControl(name="form.buttons.save").click()
        # should suceess now and redirect to view page
        self.assertEqual(
            browser.mech_browser.geturl(),
            "http://nohost/plone/fforganization/view",
        )

        # let's try edit
        browser.open("http://nohost/plone/fforganization/edit")
        fhir_str = browser.getControl(name="form.widgets.organization_resource").value

        fhir_json = json.loads(fhir_str)
        fhir_json["text"]["div"] = "<div>modified</div>"
        browser.getControl(
            name="form.widgets.organization_resource"
        ).value = json.dumps(fhir_json)
        browser.getControl(name="form.buttons.save").click()
        # should sucess
        self.assertIn('class="portalMessage info"', browser.contents)
        self.assertIn("Changes saved", browser.contents)
        self.assertEqual(
            browser.mech_browser.geturl(), "http://nohost/plone/fforganization"
        )

    def test_issue_11(self):
        """Better default view for FHIR field in view mode"""
        self.login_as_admin()

        with open(os.path.join(FHIR_FIXTURE_PATH, "Organization.json"), "r") as f:
            fhir_str = f.read()

        browser = self.browser
        browser.open(self.portal_url + "/++add++FFOrganization")
        browser.getControl(name="form.widgets.IBasic.title").value = "Test Hospital"
        # After solving that problem, this again value assign not need
        browser.getControl(name="form.widgets.organization_resource").value = fhir_str
        browser.getControl(name="form.buttons.save").click()
        self.assertIn("Item created", browser.contents)

        view_url = browser.mech_browser.geturl()
        browser.open(view_url)
        contents = browser.contents

        # make sure static resources are injected
        self.assertIn(
            "++plone++plone.app.fhirfield/css/jquery.json-viewer.css", contents
        )
        self.assertIn("++plone++plone.app.fhirfield/js/jquery.json-viewer.js", contents)
        # Make sure json viewer plugin script generated
        self.assertIn("#form-widgets-organization_resource-json-viewer", contents)
