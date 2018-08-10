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

        self.assertEqual(len(query['and']), 1)
        self.assertEqual(query['and'], compare)

        # test:2 not equal
        params = {'_lastUpdated': 'ne2011-09-17'}

        builder = helpers.ElasticsearchQueryBuilder(params,
                                                    'resource',
                                                    'Organization')
        compare = {'range': {
            'resource.meta.lastUpdated': {'lte': '2011-09-17T00:00:00',
                                          'gte': '2011-09-17T00:00:00'}}}
        query = builder.build()

        self.assertEqual(len(query['and']), 1)
        self.assertEqual(query['and'][0]['query']['not'], compare)

        # test:3 less than
        params = {'_lastUpdated': 'lt2011-09-17'}

        builder = helpers.ElasticsearchQueryBuilder(params,
                                                    'resource',
                                                    'Organization')
        compare = [{'range': {
            'resource.meta.lastUpdated': {'lt': '2011-09-17T00:00:00'}}}]

        query = builder.build()

        self.assertEqual(len(query['and']), 1)
        self.assertEqual(query['and'], compare)

        # test:4 greater than
        params = {'_lastUpdated': 'gt2011-09-17'}

        builder = helpers.ElasticsearchQueryBuilder(params,
                                                    'resource',
                                                    'Organization')
        compare = [{'range': {
            'resource.meta.lastUpdated': {'gt': '2011-09-17T00:00:00'}}}]

        query = builder.build()

        self.assertEqual(len(query['and']), 1)
        self.assertEqual(query['and'], compare)

        # test:4 less than or equal
        params = {'_lastUpdated': 'le2011-09-17'}

        builder = helpers.ElasticsearchQueryBuilder(params,
                                                    'resource',
                                                    'Organization')
        compare = [{'range': {
            'resource.meta.lastUpdated': {'lte': '2011-09-17T00:00:00'}}}]

        query = builder.build()

        self.assertEqual(len(query['and']), 1)
        self.assertEqual(query['and'], compare)

        # test:5 greater than or equal
        params = {'_lastUpdated': 'ge2011-09-17'}

        builder = helpers.ElasticsearchQueryBuilder(params,
                                                    'resource',
                                                    'Organization')
        compare = [{'range': {
            'resource.meta.lastUpdated': {'gte': '2011-09-17T00:00:00'}}}]

        query = builder.build()

        self.assertEqual(len(query['and']), 1)
        self.assertEqual(query['and'], compare)

    def test_build_resource_profile(self):
        """ """
        params = {'_profile': 'https://www.hl7.org/fhir/search.html'}

        builder = helpers.ElasticsearchQueryBuilder(
            params,
            'resource',
            'Organization')
        query = builder.build()
        compare = {'and': [{'terms': {'resource.meta.profile': ['https://www.hl7.org/fhir/search.html']}}]}

        self.assertEqual(query, compare)

    def test_validate(self):
        """ """
        # test with params those are unknown to fhir search
        try:
            params = {'created_on': '2011-09-17', 'fake_param': None}
            helpers.ElasticsearchQueryBuilder(
                params,
                'task_resource',
                'Task')
            raise AssertionError(
                'code should not come here as unknown '
                'parameters are provided')
        except Invalid as e:
            self.assertIn('unrecognized by FHIR search', str(e))
            self.assertIn('created_on', str(e))
            self.assertIn('fake_param', str(e))

        # Test with unsupported modifier
        try:
            params = {'patient:unknown': 'Patient/1'}
            helpers.ElasticsearchQueryBuilder(
                params,
                'task_resource',
                'Task')
            raise AssertionError(
                'code should not come here as unknown '
                'parameters are provided')
        except Invalid as e:
            self.assertIn(
                'Unsupported modifier has been attached with parameter',
                str(e))

    def test_validate_exists_modifier(self):
        """When any parameter has got modifier `missing or exists`,
        value always be boolean"""
        params = {'patient:missing': None}
        try:
            helpers.ElasticsearchQueryBuilder(
                params,
                'task_resource',
                'Task')
            raise AssertionError('Code should not come here, as ')
        except Invalid:
            pass

    def test_validate_date_value(self):
        """ """
        # test with other modifier
        try:
            params = {'_lastUpdated:exact': 'Some Date'}
            helpers.ElasticsearchQueryBuilder(
                params,
                'task_resource',
                'Task')
            raise AssertionError(
                'code should not come here as invalide '
                'modifier has been provided')
        except Invalid as e:
            self.assertIn('don\'t accept any modifier', str(e))

        # test with validate date
        try:
            params = {'_lastUpdated': '7679-89-90'}
            helpers.ElasticsearchQueryBuilder(
                params,
                'task_resource',
                'Task')
            raise AssertionError(
                'code should not come here as invalide '
                'modifier has been provided')
        except Invalid as e:
            self.assertIn('is not valid date string!', str(e))

        # test with invalid prefix
        try:
            params = {'_lastUpdated': 'it2011-09-17'}
            helpers.ElasticsearchQueryBuilder(
                params,
                'task_resource',
                'Task')
            raise AssertionError(
                'code should not come here as invalide '
                'modifier has been provided')
        except Invalid as e:
            self.assertIn('is not valid date string!', str(e))
