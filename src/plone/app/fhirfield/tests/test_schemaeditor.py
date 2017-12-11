# _*_ coding: utf-8 _*_
from .schema import ITestOrganization
from plone.app.fhirfield.testing import PLONE_APP_FHIRFIELD_INTEGRATION_TESTING
from plone.schemaeditor.interfaces import IFieldFactory
from zope.component import queryUtility
from zope.component import queryUtilityFor
from zope.schema import getFields

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

        field_list = [x for x in queryUtilityFor(IFieldFactory) if x[0] == 'plone.app.fhirfield.field.FhirResource']
        self.assertEqual(1, len(field_list))
