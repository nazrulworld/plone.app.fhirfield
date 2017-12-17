# _*_ coding: utf-8 _*_
from . import FHIR_FIXTURE_PATH
from .schema import ITestOrganization
from email.message import Message
from plone.app.fhirfield import marshaler
from plone.app.fhirfield.testing import PLONE_APP_FHIRFIELD_INTEGRATION_TESTING
from plone.restapi.interfaces import IDeserializeFromJson
from plone.restapi.services.content.utils import create
from plone.restapi.services.content.utils import rename
from plone.rfc822 import constructMessageFromSchema
from plone.rfc822.interfaces import IFieldMarshaler
from zope.component import queryMultiAdapter
from zope.publisher.browser import TestRequest
from zope.schema import getFields

import json
import os
import unittest


___author__ = 'Md Nazrul Islam<email2nazrul@gmail.com>'


class MarshalerIntegrationTest(unittest.TestCase):
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

    def test_marshaler(self):
        """ """
        context = self.add_item()
        fhir_field = getFields(ITestOrganization)['resource']

        field_marshaler = queryMultiAdapter((context, fhir_field), IFieldMarshaler)
        self.assertIsNotNone(field_marshaler)
        self.assertIsInstance(field_marshaler, marshaler.FhirResourceFieldMarshaler)

        # Test encode
        value = field_marshaler.encode(fhir_field.from_none())
        self.assertIsNone(value)

        encode_str = field_marshaler.encode(context.resource)

        rfc822_msg = constructMessageFromSchema(context, ITestOrganization)
        self.assertIsInstance(rfc822_msg, Message)
        try:
            rfc822_msg.as_string()
        except Exception as exc:
            raise AssertionError('Code should not come here!\n{0!s}'.format(exc))

        # Test with None value
        value = field_marshaler.encode(None)
        self.assertIsNone(value)

        decoded_value = field_marshaler.decode(encode_str)
        self.assertEqual(decoded_value.as_json(), context.resource.as_json())

        with open(os.path.join(FHIR_FIXTURE_PATH, 'Organization.json'), 'r') as f:
            already_decoded = f.read().decode('utf-8')

        encoding = field_marshaler.getCharset()
        self.assertEqual(encoding, 'utf-8')

        content_type = field_marshaler.getContentType()
        self.assertEqual(content_type, 'application/json')
        try:
            already_decoded.decode(encoding)
            raise AssertionError('Code should not come here! should raise Unicode decoding error.')
        except UnicodeEncodeError:
            decoded_value2 = field_marshaler.decode(already_decoded, charset=encoding, contentType=content_type)
            self.assertEqual(decoded_value.as_json(), decoded_value2.as_json())

        decoded_value = field_marshaler.decode('', charset=encoding, contentType=content_type)
        self.assertIsInstance(decoded_value, decoded_value2.__class__)

        context.resource = None
        fhir_field = getFields(ITestOrganization)['resource']

        field_marshaler = queryMultiAdapter((context, fhir_field), IFieldMarshaler)

        encoding = field_marshaler.getCharset()
        self.assertIsNone(encoding)

        content_type = field_marshaler.getContentType()
        self.assertIsNone(content_type)
