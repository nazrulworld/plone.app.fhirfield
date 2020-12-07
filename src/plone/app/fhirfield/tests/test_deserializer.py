# _*_ coding: utf-8 _*_
import json
import os
import unittest

from fhirpath.enums import FHIR_VERSION
from fhirpath.utils import lookup_fhir_class
from plone import api
from plone.app.fhirfield import field
from plone.app.fhirfield.interfaces import IFhirResource
from plone.app.fhirfield.interfaces import IFhirResourceValue
from plone.app.fhirfield.testing import PLONE_APP_FHIRFIELD_INTEGRATION_TESTING
from plone.app.fhirfield.testing import PLONE_APP_FHIRFIELD_REST_FUNCTIONAL_TESTING
from plone.app.testing import SITE_OWNER_NAME
from plone.app.testing import SITE_OWNER_PASSWORD
from plone.restapi.interfaces import IDeserializeFromJson
from plone.restapi.interfaces import IFieldDeserializer
from plone.restapi.services.content.utils import add
from plone.restapi.services.content.utils import create
from plone.restapi.testing import RelativeSession
from zExceptions import BadRequest
from zope.component import queryMultiAdapter
from zope.event import notify
from zope.lifecycleevent import ObjectCreatedEvent
from zope.publisher.browser import TestRequest
from zope.schema import getFields

from . import FHIR_FIXTURE_PATH
from .schema import IFFOrganization


___author__ = "Md Nazrul Islam<email2nazrul@gmail.com>"


class DeserializerIntegrationTest(unittest.TestCase):
    """ """

    layer = PLONE_APP_FHIRFIELD_INTEGRATION_TESTING

    def setUp(self):
        """ """
        self.portal = self.layer["portal"]
        self.request = self.layer["request"]

    def assert_field(self, context, field, json_dict):
        """ """
        # Deserialize to field value
        deserializer = queryMultiAdapter(
            (field, context, self.request), IFieldDeserializer
        )
        self.assertIsNotNone(deserializer)

        field_value = deserializer(json_dict)
        # Value type is derived from right interface
        self.assertTrue(IFhirResourceValue.providedBy(field_value))
        # Test from string data
        field_value2 = deserializer(json.dumps(json_dict))
        self.assertTrue(json.loads(field_value.json()), json.loads(field_value2.json()))

        try:
            deserializer(["I am invalid"])
            raise AssertionError(
                "Code should not come here! because invalid data type is provided."
            )
        except ValueError:
            pass

    def test_available_adapter(self):
        """ """
        with open(os.path.join(FHIR_FIXTURE_PATH, "Organization.json"), "r") as f:
            json_dict = json.load(f)

        context = api.content.create(
            container=self.portal,
            type="FFOrganization",
            id=None,
            title="Test Organization xxx",
        )

        for _name, field_ in getFields(IFFOrganization).items():

            if not IFhirResource.providedBy(field_):
                continue
            self.assert_field(context, field_, json_dict)

    def test_deserializer(self):
        """ """
        body = {"@type": "FFOrganization", "title": "Test Organization xxx"}
        with open(os.path.join(FHIR_FIXTURE_PATH, "Organization.json"), "r") as f:
            body["organization_resource"] = json.load(f)

        request = TestRequest(BODY=json.dumps(body))
        obj = create(self.portal, body["@type"], id_=None, title=body["title"])

        deserializer = queryMultiAdapter((obj, request), IDeserializeFromJson)
        assert deserializer is not None

        deserializer(validate_all=True)

        notify(ObjectCreatedEvent(obj))

        add(self.portal, obj)

        self.assertTrue(IFhirResourceValue.providedBy(obj.organization_resource))

        # Test error handling
        body["organization_resource"] = {"data": "FakeID"}
        request = TestRequest(BODY=json.dumps(body))
        obj = create(self.portal, body["@type"], id_=None, title=body["title"])

        deserializer = queryMultiAdapter((obj, request), IDeserializeFromJson)
        try:
            deserializer(validate_all=True)
            raise AssertionError(
                "Code should not come here! Because invalid fhir json data is provided!"
            )
        except BadRequest as exc:
            field_error = exc.args[0][0]
            self.assertEqual(field_error["field"], "organization_resource")
            self.assertEqual(
                field_error["message"],
                "Validation has been failed on provided FHIR data.",
            )

    def test_deserializer_with_prepared_value(self):
        """ """
        body = {"@type": "FFOrganization", "title": "Test Organization xxx"}
        organization = lookup_fhir_class(
            "Organization", FHIR_VERSION["STU3"]
        ).parse_file(os.path.join(FHIR_FIXTURE_PATH, "Organization.json"))

        obj = create(self.portal, body["@type"], id_=None, title=body["title"])
        request = TestRequest()
        deserializer = queryMultiAdapter((obj, request), IDeserializeFromJson)
        assert deserializer is not None

        deserializer(validate_all=True, data={"organization_resource": organization})

        notify(ObjectCreatedEvent(obj))

        add(self.portal, obj)
        self.assertTrue(IFhirResourceValue.providedBy(obj.organization_resource))

        fhir_field = field.FhirResource(
            title="Organization resource",
            resource_type="Organization",
            fhir_release="STU3",
        )
        organization_val = fhir_field.from_dict(organization.dict())
        obj = create(self.portal, body["@type"], id_=None, title=body["title"])
        request = TestRequest()
        deserializer = queryMultiAdapter((obj, request), IDeserializeFromJson)
        assert deserializer is not None

        deserializer(
            validate_all=True, data={"organization_resource": organization_val}
        )

        notify(ObjectCreatedEvent(obj))

        add(self.portal, obj)
        self.assertTrue(IFhirResourceValue.providedBy(obj.organization_resource))


class DeserializerFunctionalTest(unittest.TestCase):
    """ """

    layer = PLONE_APP_FHIRFIELD_REST_FUNCTIONAL_TESTING

    def setUp(self):
        """ """
        self.portal = self.layer["portal"]
        self.portal_url = self.portal.absolute_url()
        self.api_session = RelativeSession(self.portal_url)
        self.api_session.headers.update({"Accept": "application/json"})
        self.api_session.auth = (SITE_OWNER_NAME, SITE_OWNER_PASSWORD)

    def test_deserializer(self):
        """ """
        json_body = {
            "@type": "FFOrganization",
            "title": "Test Organization xxx",
            "id": "test-hospital",
        }
        with open(os.path.join(FHIR_FIXTURE_PATH, "Organization.json"), "r") as f:
            json_body["organization_resource"] = json.load(f)

        response = self.api_session.post(self.portal_url, json=json_body)
        self.assertEqual(201, response.status_code)
        self.assertEqual(
            response.json()["organization_resource"]["resourceType"],
            json_body["organization_resource"]["resourceType"],
        )

        # Test with mismatched fhir json, I mean mismatcged resource
        json_body[
            "organization_resource"
        ] = """{
          "resourceType": "ValueSet",
          "id": "yesnodontknow",
          "url": "http://hl7.org/fhir/ValueSet/yesnodontknow",
          "name": "Yes/No/Don't Know",
          "status": "draft",
          "description": "For Capturing simple yes-no-don't know answers",
          "compose": {
            "include": [
              {
                "valueSet": [
                  "http://hl7.org/fhir/ValueSet/v2-0136"
                ]
              },
              {
                "system": "http://hl7.org/fhir/data-absent-reason",
                "concept": [
                  {
                    "code": "asked",
                    "display": "Don't know"
                  }
                ]
              }
            ]
          },
          "expansion": {
            "identifier": "urn:uuid:bf99fe50-2c2b-41ad-bd63-bee6919810b4",
            "timestamp": "2015-07-14T10:00:00Z",
            "contains": [
              {
                "system": "http://hl7.org/fhir/v2/0136",
                "code": "Y",
                "display": "Yes"
              },
              {
                "system": "http://hl7.org/fhir/v2/0136",
                "code": "N",
                "display": "No"
              },
              {
                "system": "http://hl7.org/fhir/data-absent-reason",
                "code": "asked",
                "display": "Don't know"
              }
            ]
          }
        }
        """
        json_body["organization_resource"] = json.loads(
            json_body["organization_resource"]
        )
        json_body["id"] = "another-hospital"

        response = self.api_session.post(self.portal_url, json=json_body)
        self.assertEqual(400, response.status_code)
