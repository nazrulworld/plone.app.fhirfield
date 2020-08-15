# _*_ coding: utf-8 _*_
import json
import os
import unittest

import six
from fhirpath.enums import FHIR_VERSION
from fhirpath.utils import lookup_fhir_class
from plone.app.fhirfield import field
from plone.app.fhirfield.value import FhirResourceValue
from zope.interface import Invalid
from zope.schema.interfaces import ValidationError
from zope.schema.interfaces import WrongContainedType

from . import FHIR_FIXTURE_PATH


__author__ = "Md Nazrul Islam<email2nazrul@gmail.com>"


class FieldIntegrationTest(unittest.TestCase):
    """ """

    def test_init_validate(self):  # noqa: C901
        """ """
        # Test with minimal params
        try:
            field.FhirResource(
                title=u"Organization resource",
                fhir_release="STU3",
                resource_type="Organization",
            )
        except Invalid as exc:
            raise AssertionError(
                "Code should not come here, "
                "as everything should goes fine.\n{0!s}".format(exc)
            )
        # Test with fhir field specific params
        try:
            field.FhirResource(
                title="Organization resource",
                model="fhir.resources.STU3.organization.Organization",
                fhir_release="STU3",
            )
        except Invalid as exc:
            raise AssertionError(
                "Code should not come here, as "
                "everything should goes fine.\n{0!s}".format(exc)
            )

        try:
            field.FhirResource(
                title="Organization resource",
                resource_type="Organization",
                fhir_release="STU3",
            )
        except Invalid as exc:
            raise AssertionError(
                "Code should not come here, "
                "as everything should goes fine.\n{0!s}".format(exc)
            )

        # resource_type and model are not allowed combinely
        try:
            field.FhirResource(
                title="Organization resource",
                resource_type="Organization",
                model="fhir.resources.organization.Organization",
                fhir_release="STU3",
            )
            raise AssertionError(
                "Code should not come here! as should be invalid error"
            )
        except Invalid:
            pass

        # test with invalid pyton style dotted path (fake module)
        try:
            field.FhirResource(
                title="Organization resource",
                model="fake.fake.models.organization.Organization",
                fhir_release="STU3",
            )
            raise AssertionError(
                "Code should not come here! as should be invalid error"
            )
        except Invalid:
            pass

        # test with invalid fhir model
        try:
            field.FhirResource(
                title="Organization resource",
                model="plone.app.fhirfield.handler.FhirResourceHandler_",
                fhir_release="STU3",
            )
            raise AssertionError(
                "Code should not come here! as should be invalid error"
            )
        except Invalid as exc:
            self.assertIn("must be valid model class from fhirclient.model", str(exc))

        # test with invalid ResourceType
        try:
            field.FhirResource(
                title="Organization resource",
                resource_type="FakeResource",
                fhir_release="STU3",
            )
            raise AssertionError(
                "Code should not come here! as should be invalid error"
            )
        except Invalid as exc:
            self.assertIn(
                "FakeResource is not valid fhir resource type!", str(exc),
            )

        # Wrong base interface class
        try:
            field.FhirResource(
                title="Organization resource",
                model_interface="plone.app.fhirfield.interfaces.IFhirResourceValue",
                fhir_release="STU3",
            )
            raise AssertionError(
                "Code should not come here! as wrong subclass of interface is provided"
            )
        except Invalid:
            pass

    def test_init_validation_with_wrong_dotted_path(self):
        """ """
        # Wrong module path
        try:
            field.FhirResource(
                title="Organization resource",
                model="fake.tests.NoneInterfaceClass",
                fhir_release="STU3",
            )
            raise AssertionError(
                "Code should not come here! as wrong model class is provided"
            )
        except Invalid as exc:
            self.assertIn("Invalid FHIR Resource Model", str(exc))

    def test_validate(self):
        """ """
        with open(os.path.join(FHIR_FIXTURE_PATH, "Organization.json"), "r") as f:
            json_dict = json.load(f)

        organization = lookup_fhir_class("Organization", FHIR_VERSION["STU3"])(
            **json_dict  # noqa: C815
        )
        fhir_resource_value = FhirResourceValue(raw=organization)

        fhir_field = field.FhirResource(
            title=six.text_type("Organization resource"),
            resource_type="Organization",
            fhir_release="STU3",
        )

        try:
            fhir_field._validate(fhir_resource_value)
        except Invalid as exc:
            raise AssertionError("Code should not come here!\n{0!s}".format(exc))

        # Test model constraint
        fhir_field = field.FhirResource(
            title="Organization resource",
            model="fhir.resources.STU3.task.Task",
            fhir_release="STU3",
        )

        try:
            fhir_field._validate(fhir_resource_value)
            raise AssertionError("Code should not come here! model mismatched!")
        except WrongContainedType as exc:
            self.assertIn("Wrong fhir resource value", str(exc))

        # Test resource type constraint!
        fhir_field = field.FhirResource(
            title="Organization resource", resource_type="Task", fhir_release="STU3"
        )

        try:
            fhir_field._validate(fhir_resource_value)
            raise AssertionError("Code should not come here! model mismatched!")
        except WrongContainedType as exc:
            self.assertIn(
                "Wrong fhir resource value is provided! Value should be objec", str(exc)
            )

    def test_from_dict(self):
        """ """
        with open(os.path.join(FHIR_FIXTURE_PATH, "Organization.json"), "r") as f:
            json_dict = json.load(f)

        fhir_field = field.FhirResource(
            title="Organization resource",
            model="fhir.resources.STU3.organization.Organization",
            fhir_release="STU3",
        )

        try:
            fhir_resource_value = fhir_field.from_dict(json_dict)
        except Invalid as exc:
            raise AssertionError(
                "Code should not come here! as should "
                "return valid FhirResourceValue.\n{0!s}".format(exc)
            )

        self.assertEqual(fhir_resource_value.resource_type, json_dict["resourceType"])

        fhir_field = field.FhirResource(
            title="Organization resource",
            resource_type="Organization",
            fhir_release="STU3",
        )

        fhir_resource_value = fhir_field.from_dict(json_dict)
        try:
            fhir_resource_value.json()
        except Exception:
            raise AssertionError(
                "Code should not come here! as should be valid fhir resource"
            )

        # Test with invalid data type
        try:
            invalid_data = ("hello", "tree", "go")
            fhir_field.from_dict(invalid_data)
        except ValidationError as exc:
            self.assertIn(
                "the JSON object must be str, bytes or bytearray, not tuple", str(exc)
            )

        # Test with invalid fhir data
        try:
            invalid_data = dict(hello="fake", foo="bar")
            fhir_field.from_dict(invalid_data)

            raise AssertionError("Code should not come here, because of invalid data")
        except Invalid as exc:
            self.assertIn("extra fields not permitted", str(exc))

        # Test contraint
        fhir_field = field.FhirResource(
            title="Organization resource",
            model="fhir.resources.STU3.task.Task",
            fhir_release="STU3",
        )

        try:
            fhir_field.from_dict(json_dict)
            raise AssertionError(
                "Code should not come here as required fhir "
                "model is mismatched with provided resourcetype"
            )
        except ValidationError as exc:
            self.assertIn(
                "expects resource type ``Task``, but got ``Organization`", str(exc)
            )

    def test_fromUnicode(self):
        """ """
        with open(os.path.join(FHIR_FIXTURE_PATH, "Organization.json"), "r") as f:
            json_str = f.read()

        fhir_field = field.FhirResource(
            title="Organization resource",
            model="fhir.resources.STU3.organization.Organization",
            fhir_release="STU3",
        )

        try:
            fhir_field.fromUnicode(json_str)
        except Invalid as exc:
            raise AssertionError(
                "Code should not come here! as should return "
                "valid FhirResourceValue.\n{0!s}".format(exc)
            )

        # Test with invalid json string
        try:
            invalid_data = "{hekk: invalg, 2:3}"
            fhir_field.fromUnicode(invalid_data)
            raise AssertionError(
                "Code should not come here! invalid json string is provided"
            )
        except Invalid as exc:
            self.assertIn("Expecting property name enclosed in double quotes", str(exc))

    def test_fromUnicode_with_empty_str(self):
        """ """
        fhir_field = field.FhirResource(
            title="Organization resource",
            model="fhir.resources.STU3.organization.Organization",
            required=False,
            fhir_release="STU3",
        )

        value = fhir_field.fromUnicode("")
        self.assertFalse(value)

    def test_from_none(self):
        """ """
        fhir_field = field.FhirResource(
            title="Organization resource",
            model="fhir.resources.STU3.organization.Organization",
            fhir_release="STU3",
        )

        empty_value = fhir_field.from_none()
        self.assertFalse(empty_value)

        try:
            empty_value.resource_type
            raise AssertionError(
                "Code should not come here! should raise attribute error"
            )
        except AttributeError:
            pass

        try:
            empty_value.resource_type = "set value"
            raise AssertionError(
                "Code should not come here! should raise attribute error"
            )
        except AttributeError:
            pass

    def test_default_value(self):
        """ """
        with open(os.path.join(FHIR_FIXTURE_PATH, "Organization.json"), "r") as f:
            json_dict = json.load(f)

        fhir_field = field.FhirResource(
            title="Organization resource",
            model="fhir.resources.STU3.organization.Organization",
            default=json_dict,
            fhir_release="STU3",
        )
        self.assertEqual(json_dict, json.loads(fhir_field.default.json()))

        fhir_field2 = field.FhirResource(
            title="Organization resource",
            model="fhir.resources.STU3.organization.Organization",
            default=json.dumps(json_dict),
            fhir_release="STU3",
        )

        self.assertEqual(fhir_field2.default.json(), fhir_field.default.json())

        fhir_field3 = field.FhirResource(
            title="Organization resource",
            model="fhir.resources.STU3.organization.Organization",
            default=None,
            fhir_release="STU3",
        )
        self.assertEqual(str(fhir_field3.default), "")

    def test_resource_type_constraint(self):
        """Regarding to issue: #3 """
        fhir_field = field.FhirResource(
            title="Organization resource",
            resource_type="Organization",
            fhir_release="STU3",
        )
        with open(os.path.join(FHIR_FIXTURE_PATH, "Patient.json"), "r") as f:
            json_dict = json.load(f)

        try:
            fhir_field.from_dict(json_dict)
        except ValidationError as e:
            self.assertIn(
                "expects resource type ``Organization``, but got ``Patient`", str(e)
            )
