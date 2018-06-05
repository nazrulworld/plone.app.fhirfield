# -*- coding: utf-8 -*-
# @Date    : 2018-05-20 10:26:23
# @Author  : Md Nazrul Islam (email2nazrul@gmail.com)
# @Link    : http://nazrul.me/
# @Version : $Id$
# Example standard query https://smilecdr.com/docs/current/tutorial_and_tour/fhir_search_queries.html
# https://github.com/FirelyTeam/RonFHIR
# All imports here
from . import FHIR_FIXTURE_PATH
from collective.elasticsearch.es import ElasticSearchCatalog
from DateTime import DateTime
from plone import api
from plone.app.fhirfield.testing import PLONE_APP_FHIRFIELD_WITH_ES_FUNCTIONAL_TESTING
from plone.app.testing import SITE_OWNER_NAME
from plone.app.testing import SITE_OWNER_PASSWORD
from plone.testing import z2

import json
import os
import six
import unittest


__author__ = 'Md Nazrul Islam (email2nazrul@gmail.com)'


class ElasticSearchFhirIndexFunctionalTest(unittest.TestCase):
    """ """
    layer = PLONE_APP_FHIRFIELD_WITH_ES_FUNCTIONAL_TESTING

    def setUp(self):
        """ """
        self.portal = self.layer['portal']
        self.portal_url = api.portal.get_tool('portal_url')()
        self.portal_catalog_url = api.portal.get_tool('portal_catalog').absolute_url()

        self.anon_browser = z2.Browser(self.layer['app'])
        self.error_setup(self.anon_browser)

        self.admin_browser = z2.Browser(self.layer['app'])
        self.admin_browser.addHeader('Authorization',
                                     'Basic {0}:{1}'.format(SITE_OWNER_NAME,
                                                            SITE_OWNER_PASSWORD))
        self.error_setup(self.admin_browser)

    def error_setup(self, browser):
        """ """
        browser.handleErrors = False
        self.portal.error_log._ignored_exceptions = ()

        def raising(self, info):
            import traceback
            traceback.print_tb(info[2])
            six.print_(info[1])

        from Products.SiteErrorLog.SiteErrorLog import SiteErrorLog
        SiteErrorLog.raising = raising

    def test_resource_index_created(self):
        """resource is attribute of TestOrganization content
        that is indexed as FhirOrganizationIndex"""
        self.admin_browser.open(self.portal_catalog_url + '/manage_catalogIndexes')

        self.assertIn('FhirOrganizationIndex',
                      self.admin_browser.contents)
        self.assertIn('resource',
                      self.admin_browser.contents)

    def test_content_object_index(self):
        """Test indexes added for newly inserted indexes"""

        self.admin_browser.open(self.portal_url + '/++add++TestOrganization')

        self.admin_browser.getControl(name='form.widgets.IBasic.title').value = 'Test Hospital'

        with open(os.path.join(FHIR_FIXTURE_PATH, 'Organization.json'), 'r') as f:
            self.admin_browser.getControl(name='form.widgets.resource').value = f.read()

        self.admin_browser.getControl(name='form.buttons.save').click()
        self.assertIn('Item created', self.admin_browser.contents)
        self.assertIn('testorganization/view', self.admin_browser.url)

        # Let's check one item should be for resource item
        self.admin_browser.open(self.portal_catalog_url + '/Indexes/resource/manage_main')

        self.assertIn('Objects indexed: 1', self.admin_browser.contents)
        self.assertIn('Distinct values: 1', self.admin_browser.contents)
        """http://localhost:9200/_stats"""

    def test_content_object_index_to_es(self):
        """We will need to make sure that elastic server is taking responsibilities
        for indexing, querying"""
        # first we making sure to transfer handler
        self.admin_browser.open(self.portal_url + '/@@elastic-controlpanel')

        self.admin_browser.getControl(name='form.widgets.enabled:list').value = [True]
        self.admin_browser.getControl(name='form.buttons.save').click()

        form = self.admin_browser.getForm(action=self.portal_catalog_url + '/@@elastic-convert')
        form.getControl(name='convert').click()

        self.admin_browser.open(self.portal_url + '/++add++TestOrganization')

        self.admin_browser.getControl(name='form.widgets.IBasic.title').value = 'Test Hospital'

        with open(os.path.join(FHIR_FIXTURE_PATH, 'Organization.json'), 'r') as f:
            self.admin_browser.getControl(name='form.widgets.resource').value = f.read()
        self.admin_browser.getControl(name='form.buttons.save').click()
        self.assertIn('Item created', self.admin_browser.contents)

        es = ElasticSearchCatalog(api.portal.get_tool('portal_catalog'))
        number_of_index = es.connection.indices.\
            stats(index=es.index_name)['indices'][es.index_name + '_1']['total']['indexing']['index_total']

        # should one index
        self.assertEqual(number_of_index, 1)

    def test_catalog_search_raw_es_query(self):
        """We will need to make sure that elastic server is taking responsibilities
        for indexing, querying"""
        # first we making sure to transfer handler
        self.admin_browser.open(self.portal_url + '/@@elastic-controlpanel')
        self.admin_browser.getControl(name='form.widgets.es_only_indexes').value = 'Description\nSearchableText\nTitle\nresource'
        self.admin_browser.getControl(name='form.widgets.enabled:list').value = [True]
        self.admin_browser.getControl(name='form.buttons.save').click()

        form = self.admin_browser.getForm(action=self.portal_catalog_url + '/@@elastic-convert')
        form.getControl(name='convert').click()

        self.admin_browser.open(self.portal_url + '/++add++TestOrganization')

        self.admin_browser.getControl(name='form.widgets.IBasic.title').value = 'Test Hospital'

        with open(os.path.join(FHIR_FIXTURE_PATH, 'Organization.json'), 'r') as f:
            self.admin_browser.getControl(name='form.widgets.resource').value = f.read()
        self.admin_browser.getControl(name='form.buttons.save').click()
        self.assertIn('Item created', self.admin_browser.contents)

        self.admin_browser.open(self.portal_url + '/++add++TestOrganization')
        self.admin_browser.getControl(name='form.widgets.IBasic.title').value = 'Hamid Patuary University'
        with open(os.path.join(FHIR_FIXTURE_PATH, 'Organization.json'), 'r') as f:
            json_value = json.load(f)
            json_value['id'] = 'f002'
            json_value['name'] = 'Hamid Patuary University'
            self.admin_browser.getControl(name='form.widgets.resource').value = json.dumps(json_value)
        self.admin_browser.getControl(name='form.buttons.save').click()
        self.assertIn('Item created', self.admin_browser.contents)

        es = ElasticSearchCatalog(api.portal.get_tool('portal_catalog'))

        number_of_index = es.connection.indices.\
            stats(index=es.index_name)['indices'][es.index_name + '_1']['total']['indexing']['index_total']

        # should two indexes now
        self.assertEqual(number_of_index, 2)
        # Let's search
        # https://www.elastic.co/guide/en/elasticsearch/guide/current/nested-objects.html
        # https://www.elastic.co/guide/en/elasticsearch/guide/current/nested-query.html
        portal_catalog = api.portal.get_tool('portal_catalog')
        resource_query = [
                            # {"match": {"resource.name": "Burgers University Medical Center"}},
                            {"match": {"resource.name": "Hamid Patuary University"}},
                            {"nested": {
                                "path": "resource.identifier",
                                "query": {
                                    "bool": {
                                        "must": [
                                            {"match": {"resource.identifier.system": "urn:oid:2.16.840.1.113883.2.4.6.1"}}
                                        ]
                                    }
                                }
                            }
                            }
                        ]
        res = portal_catalog.unrestrictedSearchResults(resource=resource_query)
        print res
        resource_query = [
            {"range": {"resource.meta.lastUpdated": {"lt": DateTime().ISO8601()}}}
        ]
        res = portal_catalog.unrestrictedSearchResults(resource=resource_query)
        import pdb;pdb.set_trace()

    def tearDown(self):
        """ """
        es = ElasticSearchCatalog(api.portal.get_tool('portal_catalog'))
        es.connection.indices.delete(index='_all')