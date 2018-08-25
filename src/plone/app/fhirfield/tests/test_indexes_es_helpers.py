# _*_ coding: utf-8 _*_
from plone.app.fhirfield.indexes.es import helpers
from plone.app.fhirfield.testing import PLONE_APP_FHIRFIELD_INTEGRATION_TESTING
from zope.interface import Invalid

import unittest


__author__ = 'Md Nazrul Islam<email2nazrul@gmail.com>'


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
