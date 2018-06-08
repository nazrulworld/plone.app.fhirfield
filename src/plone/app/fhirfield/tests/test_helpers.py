# _*_ coding: utf-8 _*_
from . import FHIR_FIXTURE_PATH
from plone.app.fhirfield import compat
from plone.app.fhirfield import helpers
from plone.app.fhirfield.testing import PLONE_APP_FHIRFIELD_INTEGRATION_TESTING
from zope.interface import Invalid

import inspect
import os
import unittest


__author__ = 'Md Nazrul Islam<email2nazrul@gmail.com>'


class HelperIntegrationTest(unittest.TestCase):
    """ """
    layer = PLONE_APP_FHIRFIELD_INTEGRATION_TESTING

    def test_search_fhir_model(self):
        """ """
        dotted_path = helpers.search_fhir_model('DeviceRequest')
        self.assertEqual('fhirclient.models.devicerequest.DeviceRequest', dotted_path)

        dotted_path = helpers.search_fhir_model('FakeResource')
        self.assertIsNone(dotted_path)

    def test_caching_of_search_fhir_model(self):
        """ """
        helpers.FHIR_RESOURCE_MODEL_CACHE.clear()
        dotted_path = helpers.search_fhir_model('DeviceRequest')
        self.assertEqual('fhirclient.models.devicerequest.DeviceRequest', dotted_path)

        self.assertEqual(len(helpers.FHIR_RESOURCE_MODEL_CACHE), 1)

    def test_resource_type_str_to_fhir_model(self):
        """ """
        task = helpers.resource_type_str_to_fhir_model('Task')

        self.assertTrue(inspect.isclass(task))

        self.assertEqual(task.resource_type, 'Task')

        try:
            helpers.resource_type_str_to_fhir_model('FakeResource')
            raise AssertionError('Code shouldn\'t come here! as invalid resource type is provided')
        except Invalid as e:
            self.assertIn('FakeResource', str(e))

    def test_import_string(self):
        """ """
        current_user_func = helpers.import_string('plone.api.user.get_current')
        self.assertTrue(inspect.isfunction(current_user_func))

        try:
            # Invalid dotted path!
            helpers.import_string('plone_api_user_get_current')
            raise AssertionError('Code shouldn\'t come here! as invalid dotted path is provided')
        except ImportError:
            pass

        try:
            # Invalid class or function!
            helpers.import_string('plone.api.user.fake')
            raise AssertionError('Code shouldn\'t come here! as invalid function name is provided')
        except ImportError:
            pass

        try:
            # Invalid pyton module!
            helpers.import_string('fake.fake.FakeClass')
            raise AssertionError('Code shouldn\'t come here! as invalid python module is provided')
        except ImportError:
            pass

    def test_parse_json_str(self):
        """ """
        with open(os.path.join(FHIR_FIXTURE_PATH, 'Organization.json'), 'r') as f:
            json_str = f.read()

        dict_data = helpers.parse_json_str(json_str)

        self.assertEqual(dict_data['resourceType'], 'Organization')

        json_str = """
        {"resourceType": "Task", Wrong: null}
        """
        try:
            helpers.parse_json_str(json_str)
            raise AssertionError('Code shouldn\'t come here! as invalid json string is provided')
        except Invalid:
            pass

    def test_parse_json_str_with_empty(self):
        """ """
        value = helpers.parse_json_str(compat.NO_VALUE)
        self.assertIsNone(value)

        value = helpers.parse_json_str(compat.EMPTY_STRING)
        self.assertIsNone(value)


class ElasticsearchQueryBuilderIntegrationTest(unittest.TestCase):
    """ """
    layer = PLONE_APP_FHIRFIELD_INTEGRATION_TESTING

    def test_build_resource_date_type(self):
        """ """
        # test:1 exact
        params = {'_lastUpdated': '2011-09-17'}

        builder = helpers.ElasticsearchQueryBuilder(params,
                                                    'resource',
                                                    'Organization')
        compare = [{'range': {
            'resource.meta.lastUpdated': {'lte': '2011-09-17T00:00:00',
                                          'gte': '2011-09-17T00:00:00'}}}]
        query = builder.build()

        self.assertEqual(len(query['must']), 1)
        self.assertEqual(query['must'], compare)

        # test:2 not equal
        params = {'_lastUpdated': 'ne2011-09-17'}

        builder = helpers.ElasticsearchQueryBuilder(params,
                                                    'resource',
                                                    'Organization')
        compare = [{'range': {
            'resource.meta.lastUpdated': {'lte': '2011-09-17T00:00:00',
                                          'gte': '2011-09-17T00:00:00'}}}]
        query = builder.build()

        self.assertEqual(len(query['must']), 0)
        self.assertEqual(len(query['must_not']), 1)
        self.assertEqual(query['must_not'], compare)

        # test:3 less than
        params = {'_lastUpdated': 'lt2011-09-17'}

        builder = helpers.ElasticsearchQueryBuilder(params,
                                                    'resource',
                                                    'Organization')
        compare = [{'range': {
            'resource.meta.lastUpdated': {'lt': '2011-09-17T00:00:00'}}}]

        query = builder.build()

        self.assertEqual(len(query['must']), 1)
        self.assertEqual(query['must'], compare)

        # test:4 greater than
        params = {'_lastUpdated': 'gt2011-09-17'}

        builder = helpers.ElasticsearchQueryBuilder(params,
                                                    'resource',
                                                    'Organization')
        compare = [{'range': {
            'resource.meta.lastUpdated': {'gt': '2011-09-17T00:00:00'}}}]

        query = builder.build()

        self.assertEqual(len(query['must']), 1)
        self.assertEqual(query['must'], compare)

        # test:4 less than or equal
        params = {'_lastUpdated': 'le2011-09-17'}

        builder = helpers.ElasticsearchQueryBuilder(params,
                                                    'resource',
                                                    'Organization')
        compare = [{'range': {
            'resource.meta.lastUpdated': {'lte': '2011-09-17T00:00:00'}}}]

        query = builder.build()

        self.assertEqual(len(query['must']), 1)
        self.assertEqual(query['must'], compare)

        # test:5 greater than or equal
        params = {'_lastUpdated': 'ge2011-09-17'}

        builder = helpers.ElasticsearchQueryBuilder(params,
                                                    'resource',
                                                    'Organization')
        compare = [{'range': {
            'resource.meta.lastUpdated': {'gte': '2011-09-17T00:00:00'}}}]

        query = builder.build()

        self.assertEqual(len(query['must']), 1)
        self.assertEqual(query['must'], compare)

    def test_build_resource_profile(self):
        """ """
