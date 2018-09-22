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
from plone.app.fhirfield.exc import SearchQueryValidationError
from plone.app.fhirfield.indexes.PluginIndexes.FHIRIndex import FhirFieldIndex
from plone.app.fhirfield.indexes.PluginIndexes.FHIRIndex import make_fhir_index_datum  # noqa: E501
from plone.app.fhirfield.testing import IS_TRAVIS
from plone.app.fhirfield.testing import PLONE_APP_FHIRFIELD_WITH_ES_FUNCTIONAL_TESTING  # noqa: E501
from plone.app.testing import SITE_OWNER_NAME
from plone.app.testing import SITE_OWNER_PASSWORD
from plone.testing import z2

import json
import logging
import os
import six
import sys
import time
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
        if not IS_TRAVIS:
            self.enable_event_log()

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

    def enable_event_log(self, loggers=None, plone_log_level='ERROR'):
        """
            :param loggers: dict of loggers. format {'logger name': 'level name'}
            :param plone_log_level: log level of plone. default is ERROR
         """
        defaults = {
            'plone.app.fhirfield': 'INFO',
            'collective.elasticsearch': 'DEBUG',
        }
        from Products.CMFPlone.log import logger

        loggers = loggers or defaults

        for logger_name, level_name in six.iteritems(loggers):
            logging.getLogger(logger_name).setLevel(getattr(logging, level_name.upper()))
        # Plone log level:
        logger.root.setLevel(getattr(logging, plone_log_level.upper()))

        # Enable output when running tests:
        logger.root.addHandler(logging.StreamHandler(sys.stdout))

    def test_resource_index_created(self):
        """resource is attribute of TestOrganization content
        that is indexed as FhirFieldIndex"""
        self.admin_browser.open(self.portal_catalog_url + '/manage_catalogIndexes')

        self.assertIn('FhirFieldIndex',
                      self.admin_browser.contents)
        self.assertIn('organization_resource',
                      self.admin_browser.contents)

    def test_content_object_index(self):
        """Test indexes added for newly inserted indexes"""

        self.admin_browser.open(self.portal_url + '/++add++FFTestOrganization')

        self.admin_browser.getControl(name='form.widgets.IBasic.title').value = 'Test Hospital'

        with open(os.path.join(FHIR_FIXTURE_PATH, 'Organization.json'), 'r') as f:
            self.admin_browser.getControl(name='form.widgets.organization_resource').value = f.read()

        self.admin_browser.getControl(name='form.buttons.save').click()
        self.assertIn('Item created', self.admin_browser.contents)
        self.assertIn('fftestorganization/view', self.admin_browser.url)

        # Let's check one item should be for resource item
        self.admin_browser.open(self.portal_catalog_url + '/Indexes/organization_resource/manage_main')

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

        self.admin_browser.open(self.portal_url + '/++add++FFTestOrganization')

        self.admin_browser.getControl(name='form.widgets.IBasic.title').value = 'Test Hospital'

        with open(os.path.join(FHIR_FIXTURE_PATH, 'Organization.json'), 'r') as f:
            self.admin_browser.getControl(name='form.widgets.organization_resource').value = f.read()
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
        self.convert_to_elasticsearch(['organization_resource'])
        self.admin_browser.open(self.portal_url + '/++add++FFTestOrganization')

        self.admin_browser.getControl(name='form.widgets.IBasic.title').value = 'Test Hospital'

        with open(os.path.join(FHIR_FIXTURE_PATH, 'Organization.json'), 'r') as f:
            self.admin_browser.getControl(name='form.widgets.organization_resource').value = f.read()
        self.admin_browser.getControl(name='form.buttons.save').click()
        self.assertIn('Item created', self.admin_browser.contents)

        self.admin_browser.open(self.portal_url + '/++add++FFTestOrganization')
        self.admin_browser.getControl(name='form.widgets.IBasic.title').value = 'Hamid Patuary University'
        with open(os.path.join(FHIR_FIXTURE_PATH, 'Organization.json'), 'r') as f:
            json_value = json.load(f)
            json_value['id'] = 'f002'
            json_value['name'] = 'Hamid Patuary University'
            self.admin_browser.getControl(name='form.widgets.organization_resource').value = json.dumps(json_value)
        self.admin_browser.getControl(name='form.buttons.save').click()
        self.assertIn('Item created', self.admin_browser.contents)

        es = ElasticSearchCatalog(api.portal.get_tool('portal_catalog'))

        number_of_index = es.connection.indices.\
            stats(index=es.index_name)['indices'][es.index_name + '_1']['total']['indexing']['index_total']

        # should two indexes now
        self.assertEqual(number_of_index, 2)
        # Let's search
        time.sleep(1)
        # https://www.elastic.co/guide/en/elasticsearch/guide/current/nested-objects.html
        # https://www.elastic.co/guide/en/elasticsearch/guide/current/nested-query.html
        portal_catalog = api.portal.get_tool('portal_catalog')
        res = portal_catalog.unrestrictedSearchResults(organization_resource={'_id': 'f001'})

        self.assertEqual(len(res), 1)

    def convert_to_elasticsearch(self, indexes=list()):
        """ """
        default_indexes = ['Description', 'SearchableText',
                           'Title', 'id', 'portal_type']
        if indexes:
            default_indexes.extend(indexes)
        # first we making sure to transfer handler
        self.admin_browser.open(self.portal_url + '/@@elastic-controlpanel')
        self.admin_browser.getControl(name='form.widgets.es_only_indexes').value = '\n'.join(default_indexes)
        self.admin_browser.getControl(name='form.widgets.enabled:list').value = [True]
        self.admin_browser.getControl(name='form.buttons.save').click()

        form = self.admin_browser.getForm(action=self.portal_catalog_url + '/@@elastic-convert')
        form.getControl(name='convert').click()

    def load_contents(self):
        """ """
        self.convert_to_elasticsearch(['organization_resource', 'patient_resource', 'task_resource'])

        self.admin_browser.open(self.portal_url + '/++add++FFTestOrganization')

        self.admin_browser.getControl(name='form.widgets.IBasic.title').value = 'Test Hospital'

        with open(os.path.join(FHIR_FIXTURE_PATH, 'Organization.json'), 'r') as f:
            self.admin_browser.getControl(name='form.widgets.organization_resource').value = f.read()
        self.admin_browser.getControl(name='form.buttons.save').click()
        self.assertIn('Item created', self.admin_browser.contents)

        self.admin_browser.open(self.portal_url + '/++add++FFTestOrganization')
        self.admin_browser.getControl(name='form.widgets.IBasic.title').value = 'Hamid Patuary University'
        with open(os.path.join(FHIR_FIXTURE_PATH, 'Organization.json'), 'r') as f:
            json_value = json.load(f)
            json_value['id'] = 'f002'
            json_value['meta']['lastUpdated'] = '2015-05-28T05:35:56+00:00'
            json_value['meta']['profile'] = ['http://hl7.org/fhir/Organization']
            json_value['name'] = 'Hamid Patuary University'
            self.admin_browser.getControl(name='form.widgets.organization_resource').value = json.dumps(json_value)
        self.admin_browser.getControl(name='form.buttons.save').click()
        self.assertIn('Item created', self.admin_browser.contents)

        self.admin_browser.open(self.portal_url + '/++add++FFTestOrganization')
        self.admin_browser.getControl(name='form.widgets.IBasic.title').value = 'Call trun University'
        with open(os.path.join(FHIR_FIXTURE_PATH, 'Organization.json'), 'r') as f:
            json_value = json.load(f)
            json_value['id'] = 'f003'
            json_value['meta']['lastUpdated'] = DateTime().ISO8601()
            json_value['meta']['profile'] = ['http://hl7.org/fhir/Meta', 'urn:oid:002.160']
            json_value['name'] = 'Call trun University'
            self.admin_browser.getControl(name='form.widgets.organization_resource').value = json.dumps(json_value)
        self.admin_browser.getControl(name='form.buttons.save').click()
        self.assertIn('Item created', self.admin_browser.contents)

        # add patient
        self.admin_browser.open(self.portal_url + '/++add++FFTestPatient')
        self.admin_browser.getControl(name='form.widgets.IBasic.title').value = 'Test Patient'

        with open(os.path.join(FHIR_FIXTURE_PATH, 'Patient.json'), 'r') as f:
            self.admin_browser.getControl(name='form.widgets.patient_resource').value = f.read()

        self.admin_browser.getControl(name='form.buttons.save').click()
        self.assertIn('Item created', self.admin_browser.contents)

        # add tasks
        self.admin_browser.open(self.portal_url + '/++add++FFTestTask')
        with open(os.path.join(FHIR_FIXTURE_PATH, 'ParentTask.json'), 'r') as f:
            json_value = json.load(f)
            self.admin_browser.getControl(name='form.widgets.task_resource')\
                .value = json.dumps(json_value)

            self.admin_browser.getControl(name='form.widgets.IBasic.title')\
                .value = json_value['description']

        self.admin_browser.getControl(name='form.buttons.save').click()
        self.assertIn('Item created', self.admin_browser.contents)

        self.admin_browser.open(self.portal_url + '/++add++FFTestTask')
        with open(os.path.join(FHIR_FIXTURE_PATH, 'SubTask_HAQ.json'), 'r') as f:
            json_value = json.load(f)
            self.admin_browser.getControl(name='form.widgets.task_resource')\
                .value = json.dumps(json_value)

            self.admin_browser.getControl(name='form.widgets.IBasic.title')\
                .value = json_value['description']

        self.admin_browser.getControl(name='form.buttons.save').click()
        self.assertIn('Item created', self.admin_browser.contents)

        self.admin_browser.open(self.portal_url + '/++add++FFTestTask')
        with open(os.path.join(FHIR_FIXTURE_PATH, 'SubTask_CRP.json'), 'r') as f:
            json_value = json.load(f)
            self.admin_browser.getControl(name='form.widgets.task_resource')\
                .value = json.dumps(json_value)

            self.admin_browser.getControl(name='form.widgets.IBasic.title')\
                .value = json_value['description']

        self.admin_browser.getControl(name='form.buttons.save').click()
        self.assertIn('Item created', self.admin_browser.contents)

        # ES indexes to be ready
        time.sleep(1)

    def test_catalogsearch_fhir_date_param(self):
        """ """
        self.load_contents()
        # ************ FIXTURES ARE LOADED **************
        # test:1 equal to
        portal_catalog = api.portal.get_tool('portal_catalog')
        result = portal_catalog(
            organization_resource={'_lastUpdated': '2010-05-28T05:35:56+00:00'})

        # result should contains only item
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].getObject().organization_resource.id, 'f001')

        # test:2 not equal to
        result = portal_catalog(
            organization_resource={'_lastUpdated': 'ne2015-05-28T05:35:56+00:00'})
        # result should contains two items
        self.assertEqual(len(result), 2)

        # test:3 less than
        result = portal_catalog(
            organization_resource={'_lastUpdated': 'lt' + DateTime().ISO8601()},
            portal_type='FFTestOrganization')
        # result should contains three items, all are less than current time
        self.assertEqual(len(result), 3)

        # test:4 less than or equal to
        result = portal_catalog(
            organization_resource={'_lastUpdated': 'le2015-05-28T05:35:56+00:00'})
        # result should contains two items, 2010-05-28T05:35:56+00:00 + 2015-05-28T05:35:56+00:00
        self.assertEqual(len(result), 2)

        # test:5 greater than
        result = portal_catalog(
            organization_resource={'_lastUpdated': 'gt2015-05-28T05:35:56+00:00'})
        # result should contains only item
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].getObject().organization_resource.id, 'f003')

        # test:6 greater than or equal to
        result = portal_catalog(
            organization_resource={'_lastUpdated': 'ge2015-05-28T05:35:56+00:00'})
        # result should contains only item
        self.assertEqual(len(result), 2)

    def test_catalogsearch_fhir_token_param(self):
        """Testing FHIR search token type params, i.e status, active"""
        self.load_contents()
        portal_catalog = api.portal.get_tool('portal_catalog')
        query = {
            'task_resource': {'status': 'ready'},
            'portal_type': 'FFTestTask',
        }
        result = portal_catalog(**query)

        # should be two tasks with having status ready
        self.assertEqual(len(result), 2)

        query = {
            'task_resource': {'status:not': 'ready'},
        }
        result = portal_catalog(**query)

        # should be one task with having status draft
        self.assertEqual(len(result), 1)

        # test with combinition with lastUpdated
        query = {
            'task_resource': {'status': 'ready',
                              '_lastUpdated': 'lt2018-01-15T06:31:18+00:00'},
        }

        result = portal_catalog(**query)

        # should single task now
        self.assertEqual(len(result), 1)

        # ** Test boolen valued token **
        query = {
            'patient_resource': {'active': 'true'},
        }

        result = portal_catalog(**query)

        # only one patient
        self.assertEqual(len(result), 1)

        query = {
            'patient_resource': {'active': 'false'},
        }

        result = portal_catalog(**query)
        self.assertEqual(len(result), 0)

    def test_catalogsearch_fhir_reference_param(self):
        """Testing FHIR search reference type params, i.e subject, owner"""
        self.load_contents()
        patient_id = 'Patient/19c5245f-89a8-49f8-b244-666b32adb92e'
        portal_catalog = api.portal.get_tool('portal_catalog')
        query = {
            'task_resource': {'owner': patient_id},
        }
        result = portal_catalog(**query)

        # should be two tasks with having status ready
        self.assertEqual(len(result), 2)

        query = {
            'task_resource': {'owner': 'Practitioner/619c1ac0-821d-46d9-9d40-a61f2578cadf'},
        }
        result = portal_catalog(**query)
        self.assertEqual(len(result), 1)

        query = {
            'task_resource': {'patient': patient_id},
        }
        result = portal_catalog(**query)

        self.assertEqual(len(result), 3)

        # with compound query
        query = {
            'task_resource': {'patient': patient_id, 'status': 'draft'},
        }
        # should be now only single
        result = portal_catalog(**query)
        self.assertEqual(len(result), 1)

    def test_catalogsearch__profile(self):
        """solve me first: TransportError(400, u'search_phase_execution_exception',
        u'[terms] query does not support [minimum_should_match]') """
        self.load_contents()
        # test:1 URI
        portal_catalog = api.portal.get_tool('portal_catalog')
        result = portal_catalog.unrestrictedSearchResults(
            organization_resource={'_profile': 'http://hl7.org/fhir/Organization'},
        )
        # result should contains two items
        self.assertEqual(len(result), 2)

    def test_catalogsearch_missing_modifier(self):
        """ """
        self.load_contents()
        # add another patient
        self.admin_browser.open(self.portal_url + '/++add++FFTestPatient')
        self.admin_browser.getControl(name='form.widgets.IBasic.title').value = 'Test Patient'

        with open(os.path.join(FHIR_FIXTURE_PATH, 'Patient.json'), 'r') as f:
            data = json.load(f)
            data['id'] = '20c5245f-89a8-49f8-b244-666b32adb92e'
            data['gender'] = None
            self.admin_browser.getControl(name='form.widgets.patient_resource').value = json.dumps(data)

        self.admin_browser.getControl(name='form.buttons.save').click()
        self.assertIn('Item created', self.admin_browser.contents)
        # let's wait a bit
        time.sleep(1)
        # Let's test
        portal_catalog = api.portal.get_tool('portal_catalog')

        result = portal_catalog.unrestrictedSearchResults(
            patient_resource={'gender:missing': 'true'},
        )
        self.assertEqual(1, len(result))
        self.assertIsNone(result[0].getObject().patient_resource.gender)

        result = portal_catalog.unrestrictedSearchResults(
            patient_resource={'gender:missing': 'false'},
        )
        self.assertEqual(1, len(result))
        self.assertIsNotNone(result[0].getObject().patient_resource.gender)

    def test_issue_5(self):
        """https://github.com/nazrulworld/plone.app.fhirfield/issues/5
        FHIR search's modifier `missing` is not working for nested mapping
        """
        self.load_contents()
        # let's wait a bit
        time.sleep(1)

        # ------ Test in Complex Data Type -------------
        # Parent Task has not partOf but each child has partOf referenced to parent
        portal_catalog = api.portal.get_tool('portal_catalog')

        result = portal_catalog.unrestrictedSearchResults(
            task_resource={'part-of:missing': 'false'},
        )
        # should be two
        self.assertEqual(len(result), 2)

        result = portal_catalog.unrestrictedSearchResults(
            task_resource={'part-of:missing': 'true'},
        )
        # should be one (parent Task)
        self.assertEqual(len(result), 1)

    def test_catalogsearch_identifier(self):
        """ """
        self.load_contents()

        portal_catalog = api.portal.get_tool('portal_catalog')
        result = portal_catalog.unrestrictedSearchResults(
            patient_resource={'identifier': '240365-0002'},
        )
        self.assertEqual(len(result), 1)

        # Test with system+value
        portal_catalog = api.portal.get_tool('portal_catalog')
        result = portal_catalog.unrestrictedSearchResults(
            patient_resource={'identifier': 'CPR|240365-0002'},
        )
        self.assertEqual(len(result), 1)

        # Test with system only with pipe sign
        portal_catalog = api.portal.get_tool('portal_catalog')
        result = portal_catalog.unrestrictedSearchResults(
            patient_resource={'identifier': 'UUID|'},
        )
        self.assertEqual(len(result), 1)

        # Test with value only with pipe sign
        portal_catalog = api.portal.get_tool('portal_catalog')
        result = portal_catalog.unrestrictedSearchResults(
            patient_resource={'identifier': '|19c5245f-89a8-49f8-b244-666b32adb92e'},
        )
        self.assertEqual(len(result), 1)

        # Test with empty result
        portal_catalog = api.portal.get_tool('portal_catalog')
        result = portal_catalog.unrestrictedSearchResults(
            patient_resource={'identifier': 'CPR|19c5245f-89a8-49f8-b244-666b32adb92e'},
        )
        self.assertEqual(len(result), 0)

        # Test with text modifier
        portal_catalog = api.portal.get_tool('portal_catalog')
        result = portal_catalog.unrestrictedSearchResults(
            patient_resource={'identifier:text': 'Plone Patient UUID'},
        )
        self.assertEqual(len(result), 1)

    @unittest.skipIf(IS_TRAVIS, 'Ignore for travis for now, fix later')
    def test_identifier_query_validation(self):
        """ """
        self.load_contents()

        portal_catalog = api.portal.get_tool('portal_catalog')
        try:
            portal_catalog.unrestrictedSearchResults(
                patient_resource={'identifier:text': 'Plone|Patient-UUID'},
            )
            raise AssertionError('Code should not come here, as validation error should raise')
        except SearchQueryValidationError as e:
            self.assertIn('Pipe (|) is not allowed', str(e))

        try:
            portal_catalog.unrestrictedSearchResults(
                patient_resource={'identifier': 'Plone|Patient|UUID'},
            )
            raise AssertionError('Code should not come here, as validation error should raise')
        except SearchQueryValidationError as e:
            self.assertIn('Only single Pipe (|)', str(e))

    def test_catalogsearch_array_type_reference(self):
        """Search where reference inside List """
        self.load_contents()

        portal_catalog = api.portal.get_tool('portal_catalog')
        # Search with based on
        result = portal_catalog.unrestrictedSearchResults(
            task_resource={'based-on': 'ProcedureRequest/0c57a6c9-c275-4a0a-bd96-701daf7bd7ce'},
        )
        self.assertEqual(len(result), 1)

        # Search with part-of
        # should be two sub tasks
        result = portal_catalog.unrestrictedSearchResults(
            task_resource={'part-of': 'Task/5df31190-0ed4-45ba-8b16-3c689fc2e686'},
        )
        self.assertEqual(len(result), 2)

    def test_elasticsearch_sorting(self):
        """Search where reference inside List """
        self.load_contents()
        portal_catalog = api.portal.get_tool('portal_catalog')

        # Test ascending order
        result = portal_catalog.unrestrictedSearchResults(
            task_resource={'status:missing': 'false'},
            portal_type='FFTestTask',
            _sort='_lastUpdated',
        )

        self.assertGreater(
            result[1].getObject().task_resource.meta.lastUpdated.date,
            result[0].getObject().task_resource.meta.lastUpdated.date)
        self.assertGreater(
            result[2].getObject().task_resource.meta.lastUpdated.date,
            result[1].getObject().task_resource.meta.lastUpdated.date)

        # Test descending order
        result = portal_catalog.unrestrictedSearchResults(
            task_resource={'status:missing': 'false'},
            _sort='-_lastUpdated',
        )

        self.assertGreater(
            result[0].getObject().task_resource.meta.lastUpdated.date,
            result[1].getObject().task_resource.meta.lastUpdated.date)
        self.assertGreater(
            result[1].getObject().task_resource.meta.lastUpdated.date,
            result[2].getObject().task_resource.meta.lastUpdated.date)

    def test_mapping_adapter_patch(self):
        """collective.elasticsearch.mapping.MappingAdapter.
        The patch provides default index settings"""
        self.convert_to_elasticsearch()
        time.sleep(1)
        es = ElasticSearchCatalog(api.portal.get_tool('portal_catalog'))

        settings = es.connection.indices.get_settings(es.index_name)
        settings = settings[es.real_index_name]['settings']

        self.assertEqual(
            settings['index']['mapping']['nested_fields']['limit'],
            '100')

    def test_issue_6(self):
        """[FhirFieldIndex stores whole FHIR resources json as indexed value]
        https://github.com/nazrulworld/plone.app.fhirfield/issues/6"""
        self.admin_browser.open(self.portal_url + '/++add++FFTestOrganization')

        self.admin_browser.getControl(name='form.widgets.IBasic.title').value \
            = 'Test Hospital'

        with open(os.path.join(FHIR_FIXTURE_PATH, 'Organization.json'), 'r') as f:
            fhir_json = json.load(f)

        self.admin_browser.getControl(name='form.widgets.organization_resource').value \
            = json.dumps(fhir_json)
        self.admin_browser.getControl(name='form.buttons.save').click()
        self.assertIn('Item created', self.admin_browser.contents)
        self.assertIn('fftestorganization/view', self.admin_browser.url)

        rid = api.content.find(portal_type='FFTestOrganization')[0].getRID()
        portal_catalog = api.portal.get_tool('portal_catalog')

        indexed_data = portal_catalog.getIndexDataForRID(rid)['organization_resource']

        index_datum = make_fhir_index_datum(FhirFieldIndex.mapping, fhir_json)

        self.assertEqual(indexed_data, index_datum)

    def tearDown(self):
        """ """
        es = ElasticSearchCatalog(api.portal.get_tool('portal_catalog'))
        es.connection.indices.delete(index='_all')
