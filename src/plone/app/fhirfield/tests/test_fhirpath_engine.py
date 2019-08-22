# _*_ coding: utf-8 _*_
import unittest

from collective.elasticsearch.es import ElasticSearchCatalog
from fhirpath.enums import FHIR_VERSION
from fhirpath.interfaces import IEngine
from fhirpath.interfaces import IFhirSearch  # noqa
from fhirpath.interfaces import ISearchContext
from fhirpath.interfaces import ISearchContextFactory  # noqa
from fhirpath.providers.interfaces import IElasticsearchEngineFactory
from plone import api
from plone.app.fhirfield.testing import PLONE_APP_FHIRFIELD_INTEGRATION_TESTING
from zope.component import queryMultiAdapter


__author__ = "Md Nazrul Islam <email2nazrul@gmail.com>"


class FhirpathPloneEngineIntegrationTest(unittest.TestCase):
    """ """

    layer = PLONE_APP_FHIRFIELD_INTEGRATION_TESTING

    def setUp(self):
        """ """
        self.portal = self.layer["portal"]

    def get_es_catalog(self):
        """ """
        return ElasticSearchCatalog(api.portal.get_tool("portal_catalog"))

    def get_engine(self):
        """ """
        factory = queryMultiAdapter(
            (self.get_es_catalog(),), IElasticsearchEngineFactory
        )
        engine = factory(fhir_version=FHIR_VERSION.STU3)
        return engine

    def test_calculate_field_index_name(self):
        """ """
        engine = self.get_engine()
        index_field_name = engine.calculate_field_index_name("Organization")
        self.assertEqual(index_field_name, "organization_resource")
