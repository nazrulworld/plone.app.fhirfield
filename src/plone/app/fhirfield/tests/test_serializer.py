# _*_ coding: utf-8 _*_
from . import FHIR_FIXTURE_PATH
from .schema import ITestOrganization
from plone import api
from plone.app.fhirfield.testing import PLONE_APP_FHIRFIELD_FUNCTIONAL_TESTING
from plone.app.fhirfield.testing import PLONE_APP_FHIRFIELD_INTEGRATION_TESTING
from plone.app.testing import SITE_OWNER_NAME
from plone.app.testing import SITE_OWNER_PASSWORD
from plone.restapi.interfaces import IDeserializeFromJson
from plone.restapi.interfaces import IFieldSerializer
from plone.restapi.interfaces import ISerializeToJson
from plone.restapi.services.content.utils import create
from plone.restapi.services.content.utils import rename
from plone.restapi.testing import RelativeSession
from zope.component import queryMultiAdapter
from zope.publisher.browser import TestRequest
from zope.schema import getFields

import json
import os
import unittest


___author__ = 'Md Nazrul Islam<email2nazrul@gmail.com>'


class SerializerIntegrationTest(unittest.TestCase):
    """ """
    layer = PLONE_APP_FHIRFIELD_INTEGRATION_TESTING

    def setUp(self):
        """ """
        self.portal = self.layer['portal']
        self.request = self.layer['request']

    def add_item(self):
        """ """
        body = {
            '@type': 'TestOrganization',
            'title': 'Test Organization xxx',
        }
        with open(os.path.join(FHIR_FIXTURE_PATH, 'Organization.json'), 'r') as f:
            body['resource'] = json.load(f)

        request = TestRequest(BODY=json.dumps(body))
        obj = create(self.portal, body['@type'], id_=None, title=body['title'])

        deserializer = queryMultiAdapter((obj, request), IDeserializeFromJson)
        assert deserializer is not None
        deserializer(validate_all=True)
        rename(obj)

        return obj

    def test_available_adapter(self):
        """ """
        with open(os.path.join(FHIR_FIXTURE_PATH, 'Organization.json'), 'r') as f:
            json_dict = json.load(f)

        context = api.content.create(
                container=self.portal,
                type='TestOrganization',
                id=None,
                title='Test Organization xxx',
            )
        fhir_field = getFields(ITestOrganization)['resource']
        fhir_value = fhir_field.from_dict(json_dict)
        fhir_field.set(context, fhir_value)

        serializer = queryMultiAdapter(
           (fhir_field, context, self.request),
           IFieldSerializer)

        # Test id adapter is avaialble
        self.assertIsNotNone(serializer)

        value = serializer()
        self.assertEqual(json_dict['resourceType'], value['resourceType'])

        # Test with None value
        serializer.context.resource = None
        self.assertIsNone(serializer())

    def test_serialize(self):
        """ """
        context = self.add_item()
        serializer = queryMultiAdapter((context, self.request), ISerializeToJson)
        result = serializer()

        self.assertEqual(result['resource']['resourceType'], context.resource.resource_type)


class SerializerFunctionalTest(unittest.TestCase):
    """ """
    layer = PLONE_APP_FHIRFIELD_FUNCTIONAL_TESTING

    def setUp(self):
        """ """
        self.portal = self.layer['portal']
        self.portal_url = self.portal.absolute_url()
        self.api_session = RelativeSession(self.portal_url)
        self.api_session.headers.update({'Accept': 'application/json'})
        self.api_session.auth = (SITE_OWNER_NAME, SITE_OWNER_PASSWORD)

    def test_serializer(self):
        """" """
        id_ = 'test-hospital'
        json_body = {
            '@type': 'TestOrganization',
            'title': 'Test Organization xxx',
            'id': id_,
        }
        with open(os.path.join(FHIR_FIXTURE_PATH, 'Organization.json'), 'r') as f:
            json_body['resource'] = json.load(f)

        response = self.api_session.post(
             self.portal_url,
             json=json_body,
        )
        self.assertEqual(201, response.status_code)
        response = self.api_session.get(self.portal_url + '/' + id_)

        self.assertEqual(200, response.status_code)
        self.assertEqual(response.json()['resource']['resourceType'], json_body['resource']['resourceType'])
