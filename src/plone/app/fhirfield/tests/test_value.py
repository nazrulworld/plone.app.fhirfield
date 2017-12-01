# _*_ coding: utf-8 _*_
from . import FHIR_FIXTURE_PATH
from plone.app.fhirfield import value
from plone.app.fhirfield.helpers import parse_json_str
from plone.app.fhirfield.helpers import resource_type_str_to_fhir_model
from plone.app.fhirfield.interfaces import IFhirResourceModel
from zope.schema.interfaces import WrongType

import json
import os
import six
import unittest


__author__ = 'Md Nazrul Islam<email2nazrul@gmail.com>'


class ValueIntegrationTest(unittest.TestCase):
    """ """

    def test_object_storage(self):
        """ """
        storage1 = value.ObjectStorage(raw=dict(hello='Ketty'))
        storage2 = value.ObjectStorage(raw=dict(jello='Perry'))
        storage3 = value.ObjectStorage(raw=dict(hello='Ketty'))
        storage4 = dict(dist='ubuntu')

        self.assertTrue(storage1 != storage2)
        self.assertTrue(storage1 == storage3)
        self.assertEqual(storage2.__eq__(storage4), NotImplemented)

    def test_fhir_resource_value(self):
        """ """
        with open(os.path.join(FHIR_FIXTURE_PATH, 'Organization.json'), 'r') as f:
            fhir_json = json.load(f)

        model = resource_type_str_to_fhir_model(fhir_json['resourceType'])
        fhir_resource = model(fhir_json)
        fhir_resource_value = value.FhirResourceValue(raw=fhir_resource)

        # __bool__ should be True
        self.assertTrue(fhir_resource_value)
        self.assertTrue(IFhirResourceModel.providedBy(fhir_resource_value.foreground_origin()))
        self.assertIsInstance(fhir_resource_value.stringify(), six.string_types)
        # Make sure string is transformable to fhir resource
        json_str = fhir_resource_value.stringify()

        json_dict = parse_json_str(json_str)

        try:
            model(json_dict).as_json()
        except Exception:
            raise AssertionError('Code should not come here!')

        empty_resource = value.FhirResourceValue()
        # __bool__ should be False
        self.assertFalse(empty_resource)

        self.assertIsNone(empty_resource.foreground_origin())

        self.assertFalse(fhir_resource_value == empty_resource)
        self.assertFalse(empty_resource == fhir_resource_value)

        # Let's try to modify
        fhir_resource_value.identifier[0].use = 'no-official'

        # test if it impact
        self.assertEqual(fhir_resource_value.as_json()['identifier'][0]['use'], 'no-official')

        # Let's try to set value on empty value
        try:
            empty_resource.id = 'my value'
            raise AssertionError('Code should not come here! because no fhir resource!')
        except AttributeError:
            pass

        self.assertIn('NoneType', repr(empty_resource))

        # Validation Test:: more explict???
        try:
            value.FhirResourceValue(raw=dict(hello='Ketty'))
            raise AssertionError('Code should not come here, because should raise validation error!')
        except WrongType:
            pass
