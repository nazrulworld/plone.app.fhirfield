# _*_ coding: utf-8 _*_
from . import BASE_TEST_PATH
from . import FHIR_FIXTURE_PATH
from .schema import ITestOrganization
from plone.app.fhirfield import FhirResource
from plone.app.fhirfield import handler
from plone.app.fhirfield.testing import PLONE_APP_FHIRFIELD_INTEGRATION_TESTING
from plone.supermodel import model
from plone.supermodel import serializeSchema
from plone.supermodel.interfaces import IFieldExportImportHandler
from plone.supermodel.interfaces import IToUnicode
from zope.component import queryMultiAdapter
from zope.component import queryUtility
from zope.schema import getFields

import os
import unittest


___author__ = 'Md Nazrul Islam<email2nazrul@gmail.com>'


class HandlerIntegrationTest(unittest.TestCase):
    """ """
    layer = PLONE_APP_FHIRFIELD_INTEGRATION_TESTING

    def setUp(self):
        """ """
        self.portal = self.layer['portal']
        self.request = self.layer['request']

    def test_handler(self):
        """ """
        with open(os.path.join(FHIR_FIXTURE_PATH, 'Organization.json'), 'r') as f:
            fhir_str = f.read()

        fhir_field = getFields(ITestOrganization)['resource']
        # Test: available as adapter
        resource_handler = queryMultiAdapter((fhir_field, ), IToUnicode)

        self.assertIsNotNone(resource_handler)
        self.assertIsInstance(resource_handler, handler.FhirResourceToUnicode)
        self.assertIsInstance(resource_handler.context, FhirResource)

        fhir_value = fhir_field.fromUnicode(fhir_str)
        self.assertIsInstance(resource_handler.toUnicode(fhir_value), unicode)

        # Test: available as Uitility
        fhir_hanlder_util = queryUtility(IFieldExportImportHandler, name='plone.app.fhirfield.field.FhirResource')
        self.assertIsNotNone(fhir_hanlder_util)
        self.assertEqual(fhir_hanlder_util, handler.FhirResourceHandler)

        class ITestPatient(model.Schema):
            model.load(os.path.join(BASE_TEST_PATH, 'schema', 'patient.xml'))

        fhir_field2 = getFields(ITestOrganization)['resource']
        self.assertEqual(fhir_field2.__class__, fhir_field.__class__)

        xml_schema = serializeSchema(ITestOrganization)
        self.assertIn('<field name="resource" type="plone.app.fhirfield.field.FhirResource">', xml_schema)
