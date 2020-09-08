# _*_ coding: utf-8 _*_
import json
import os
import pickle as cPickle
import unittest

from fhirpath.enums import FHIR_VERSION
from fhirpath.utils import lookup_fhir_class
from plone.app.fhirfield import value
from zope.interface import Invalid
from zope.schema.interfaces import WrongType

from . import FHIR_FIXTURE_PATH


__author__ = "Md Nazrul Islam<email2nazrul@gmail.com>"


class ValueIntegrationTest(unittest.TestCase):
    """ """

    def test_object_storage(self):
        """ """
        storage1 = value.ObjectStorage(raw=dict(hello="Ketty"))
        storage2 = value.ObjectStorage(raw=dict(jello="Perry"))
        storage3 = value.ObjectStorage(raw=dict(hello="Ketty"))
        storage4 = dict(dist="ubuntu")

        self.assertTrue(storage1 != storage2)
        self.assertTrue(storage1 == storage3)
        self.assertEqual(storage2.__eq__(storage4), NotImplemented)
        self.assertEqual(storage2.__ne__(storage4), NotImplemented)

        # Test representation
        self.assertIn("ObjectStorage", repr(storage1))

    def test_fhir_resource_value(self):
        """ """
        with open(os.path.join(FHIR_FIXTURE_PATH, "Organization.json"), "r") as f:
            fhir_json = json.load(f)

        model = lookup_fhir_class(fhir_json["resourceType"], FHIR_VERSION["STU3"])
        fhir_resource = model(**fhir_json)
        fhir_resource_value = value.FhirResourceValue(raw=fhir_resource)

        # __bool__ should be True
        self.assertTrue(fhir_resource_value)
        self.assertTrue(
            "FHIRAbstractModel"
            in str(fhir_resource_value.foreground_origin().__class__.mro())
        )
        self.assertIsInstance(fhir_resource_value.stringify(), str)

        # Test Patch
        patch_data = {"hello": 123}
        try:
            fhir_resource_value.patch(patch_data)
            raise AssertionError(
                "Code should not come here! because "
                "wrong type data is provided for patch!"
            )
        except WrongType:
            pass
        patch_data = [
            {
                "path": "/text/fake path",
                "value": "patched!",
                "Invalid Option": "replace",
            }
        ]
        # Test getting original error from json patcher
        try:
            fhir_resource_value.patch(patch_data)
            raise AssertionError(
                "Code should not come here! because wrong patch data is"
                " provided for patch and invalid format as well!"
            )
        except Invalid as exc:
            self.assertIn("does not contain 'op' member", str(exc))

        patch_data = [{"path": "/text/status", "value": "patched!", "op": "replace"}]
        fhir_resource_value.patch(patch_data)

        self.assertEqual("patched!", fhir_resource_value.text.status)

        # Make sure string is transformable to fhir resource
        json_str = fhir_resource_value.stringify()

        try:
            model.parse_raw(json_str)
        except Exception:
            raise AssertionError("Code should not come here!")

        # Test self representation
        self.assertIn(
            fhir_resource_value.__class__.__module__, repr(fhir_resource_value)
        )

        empty_resource = value.FhirResourceValue()
        # __bool__ should be False
        self.assertFalse(empty_resource)

        self.assertIsNone(empty_resource.foreground_origin())

        self.assertFalse(fhir_resource_value == empty_resource)
        self.assertFalse(empty_resource == fhir_resource_value)
        self.assertTrue(empty_resource != fhir_resource_value)

        # Test Patch with empty value
        try:
            empty_resource.patch(patch_data)
            raise AssertionError(
                "Code should not come here! because empty resource cannot be patched!"
            )
        except Invalid:
            pass

        # Let's try to modify
        fhir_resource_value.identifier[0].use = "no-official"

        # test if it impact
        self.assertEqual(
            fhir_resource_value.dict()["identifier"][0]["use"], "no-official"
        )

        # Let's try to set value on empty value
        try:
            empty_resource.id = "my value"
            raise AssertionError("Code should not come here! because no fhir resource!")
        except AttributeError:
            pass

        self.assertIn("NoneType", repr(empty_resource))
        self.assertEqual("", str(empty_resource))

        # Validation Test:: more explict???
        try:
            value.FhirResourceValue(raw=dict(hello="Ketty"))
            raise AssertionError(
                "Code should not come here, because should raise validation error!"
            )
        except WrongType:
            pass

    def test_fhir_resource_value_pickling(self):
        """ """
        with open(os.path.join(FHIR_FIXTURE_PATH, "Organization.json"), "r") as f:
            fhir_json = json.load(f)

        model = lookup_fhir_class(fhir_json["resourceType"], FHIR_VERSION["STU3"])
        fhir_resource = model(**fhir_json)
        fhir_resource_value = value.FhirResourceValue(raw=fhir_resource)

        serialized = cPickle.dumps(fhir_resource_value)
        deserialized = cPickle.loads(serialized)
        self.assertEqual(
            len(deserialized.stringify()), len(fhir_resource_value.stringify())
        )
