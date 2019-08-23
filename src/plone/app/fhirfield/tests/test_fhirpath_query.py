# _*_ coding: utf-8 _*_
from collective.elasticsearch.es import ElasticSearchCatalog
from fhirpath.enums import FHIR_VERSION
from fhirpath.enums import SortOrderType
from fhirpath.fql import Q_
from fhirpath.fql import T_
from fhirpath.fql import sort_
from fhirpath.providers.interfaces import IElasticsearchEngineFactory
from plone import api
from zope.component import queryMultiAdapter

from .base import BaseFunctionalTesting


__author__ = "Md Nazrul Islam <email2nazrul@gmail.com>"


class FhirPathPloneQueryFunctionalTest(BaseFunctionalTesting):
    """ """

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

    def test_iter_result(self):
        """ """
        self.load_contents()
        engine = self.get_engine()
        builder = Q_(resource="Organization", engine=engine)
        builder = (
            builder.where(T_(
                "Organization.meta.profile",
                "http://hl7.org/fhir/Organization"))
            .sort(sort_("Organization.meta.lastUpdated", SortOrderType.DESC))
        )

        for resource in builder(async_result=False):
            assert resource.__class__.__name__ == "OrganizationModel"
