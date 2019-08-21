# _*_ coding: utf-8 _*_
import unittest

from collective.elasticsearch.es import ElasticSearchCatalog
from fhirpath.enums import FHIR_VERSION
from fhirpath.interfaces import IEngine
from fhirpath.interfaces import IFhirSearch  # noqa
from fhirpath.interfaces import ISearchContextFactory  # noqa
from fhirpath.providers.interfaces import IElasticsearchEngineFactory
from plone import api
from plone.app.fhirfield.testing import PLONE_APP_FHIRFIELD_INTEGRATION_TESTING
from zope.component import queryMultiAdapter


__author__ = "Md Nazrul Islam <email2nazrul@gmail.com>"


class FhirpathPloneUtilitiesIntegrationTest(unittest.TestCase):
    """ """

    layer = PLONE_APP_FHIRFIELD_INTEGRATION_TESTING

    def setUp(self):
        """ """
        self.portal = self.layer["portal"]

    def get_es_catalog(self):
        """ """
        return ElasticSearchCatalog(api.portal.get_tool("portal_catalog"))

    def test_engine_creation(self):
        """ """
        factory = queryMultiAdapter(
            (self.get_es_catalog(),), IElasticsearchEngineFactory
        )
        self.assertIsNotNone(factory)
        engine = factory(fhir_version=FHIR_VERSION.STU3)
        self.assertTrue(IEngine.providedBy(engine))
