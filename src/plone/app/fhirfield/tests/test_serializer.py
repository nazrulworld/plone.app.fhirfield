# _*_ coding: utf-8 _*_
from . import FHIR_FIXTURE_PATH
from plone import api
from plone.app.fhirfield.testing import PLONE_APP_FHIRFIELD_FUNCTIONAL_TESTING
from plone.app.fhirfield.testing import PLONE_APP_FHIRFIELD_INTEGRATION_TESTING
from plone.restapi.interfaces import IDeserializeFromJson
from plone.restapi.interfaces import ISerializeToJson
from plone.restapi.services.content.utils import create
from plone.restapi.services.content.utils import rename
from zope.component import queryMultiAdapter
from zope.publisher.browser import TestRequest

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

    def test_serializer_available(self):
        """ """
        obj = self.add_item()
        import pdb;pdb.set_trace()
        # # Insert field values
        # for schema in iterSchemata(self.context):

        #     read_permissions = mergedTaggedValueDict(
        #         schema, READ_PERMISSIONS_KEY)

        #     for name, field in getFields(schema).items():

        #         if not self.check_permission(read_permissions.get(name), obj):
        #             continue

        #         serializer = queryMultiAdapter(
        #             (field, obj, self.request),
        #             IFieldSerializer)
        #         value = serializer()
        #         result[json_compatible(name)] = value

        # return result

    def test_serialize(self):
        """ """