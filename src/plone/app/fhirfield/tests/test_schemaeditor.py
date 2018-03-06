# _*_ coding: utf-8 _*_
from .schema import ITestOrganization
from plone.app.fhirfield.testing import PLONE_APP_FHIRFIELD_FUNCTIONAL_TESTING
from plone.app.fhirfield.testing import PLONE_APP_FHIRFIELD_INTEGRATION_TESTING
from plone.app.testing import SITE_OWNER_NAME
from plone.app.testing import SITE_OWNER_PASSWORD
from plone.schemaeditor.interfaces import IFieldFactory
from plone.testing import z2
from zope.component import getUtilitiesFor
from zope.component import queryUtility
from zope.schema import getFields

import time
import unittest


___author__ = 'Md Nazrul Islam<email2nazrul@gmail.com>'


class SchemaeditorIntegrationTest(unittest.TestCase):
    """ """
    layer = PLONE_APP_FHIRFIELD_INTEGRATION_TESTING

    def setUp(self):
        """ """
        self.portal = self.layer['portal']
        self.request = self.layer['request']

    def test_editor(self):
        """ """
        fhir_field = getFields(ITestOrganization)['resource']
        # Test: available as adapter
        field_factory = queryUtility(IFieldFactory, name='plone.app.fhirfield.field.FhirResource')

        self.assertIsNotNone(field_factory)
        fhir_field2 = field_factory(
            title=u'Fhir Resource Field',
            model='fhirclient.models.organization.Organization')

        self.assertEqual(fhir_field.model, fhir_field2.model)
        self.assertEqual(fhir_field, fhir_field2)

        field_list = [x for x in getUtilitiesFor(IFieldFactory) if x[0] == 'plone.app.fhirfield.field.FhirResource']
        self.assertEqual(1, len(field_list))


class SchemaeditorFunctionalTest(unittest.TestCase):
    """ """
    layer = PLONE_APP_FHIRFIELD_FUNCTIONAL_TESTING

    def setUp(self):
        """ """
        self.portal = self.layer['portal']
        self.portal_url = self.portal.absolute_url()
        self.browser = z2.Browser(self.layer['app'])
        self.error_setup()

    def error_setup(self):
        """ """
        self.browser.handleErrors = False
        self.portal.error_log._ignored_exceptions = ()

        def raising(self, info):
            import traceback
            traceback.print_tb(info[2])
            print (info[1])

        from Products.SiteErrorLog.SiteErrorLog import SiteErrorLog
        SiteErrorLog.raising = raising

    def login_as_admin(self):
        """ Perform through-the-web login."""

        # Go admin
        browser = self.browser
        browser.open(self.portal_url + '/login_form')
        browser.getControl(name='__ac_name').value = SITE_OWNER_NAME
        browser.getControl(name='__ac_password').value = SITE_OWNER_PASSWORD
        browser.getControl(name='submit').click()

    def test_schemaeditor(self):
        """" """
        self.login_as_admin()

        browser = self.browser
        browser.open(self.portal_url + '/dexterity-types/@@add-type?ajax_load={0!s}'.format(time.time()))

        browser.getControl(name='form.widgets.title').value = 'test organization'
        browser.getControl(name='form.widgets.id').value = 'testorganization'
        browser.getControl(name='form.widgets.description').value = 'Test Organization Content Type'
        browser.getControl(name='form.buttons.add').click()
        # There must be form error! as required title is missing so url is unchanged

        # Let's fullfill required
        browser.open(
            '{0}/dexterity-types/testorganization/@@add-field?ajax_load={1}'.format(
                self.portal_url,
                time.time(),
                ),
            )
        # Make sure available in select list!
        self.assertIn('FHIR Resource Field', browser.contents)
