# _*_ coding: utf-8 _*_
from . import FHIR_FIXTURE_PATH
from plone.app.fhirfield import field
from plone.app.fhirfield.helpers import parse_json_str
from plone.app.fhirfield.helpers import resource_type_str_to_fhir_model
from plone.app.fhirfield.interfaces import IFhirResourceModel
from zope.interface import Invalid
from zope.schema.interfaces import WrongType

import json
import os
import six
import unittest


__author__ = 'Md Nazrul Islam<email2nazrul@gmail.com>'


class FieldIntegrationTest(unittest.TestCase):
    """ """

    def test_init_validate(self):
        """ """
        # Test with minimal params
        try:
            field.FhirResource(
                title=six.text_type('Organization resource')
            )
        except Invalid as exc:
            raise AssertionError('Code should not come here, as everything should goes fine.\n{0!s}'.format(exc))
        # Test with fhir field specific params
        try:
            field.FhirResource(
                title=six.text_type('Organization resource'),
                model='fhirclient.models.organization.Organization',
                model_interface=IFhirResourceModel
            )
        except Invalid as exc:
            raise AssertionError('Code should not come here, as everything should goes fine.\n{0!s}'.format(exc))

        try:
            field.FhirResource(
                title=six.text_type('Organization resource'),
                resource_type='Organization'
            )
        except Invalid as exc:
            raise AssertionError('Code should not come here, as everything should goes fine.\n{0!s}'.format(exc))

        # resource_type and model are not allowed combinely
        try:
            field.FhirResource(
                title=six.text_type('Organization resource'),
                resource_type='Organization',
                model='fhirclient.models.organization.Organization'
            )
            raise AssertionError('Code should not come here! as should be invalid error')
        except Invalid:
            pass

        # test with invalid pyton style dotted path (fake module)
        try:
            field.FhirResource(
                title=six.text_type('Organization resource'),
                model='fake.fake.models.organization.Organization'
            )
            raise AssertionError('Code should not come here! as should be invalid error')
        except Invalid:
            pass

        # test with invalid fhir model
        try:
            field.FhirResource(
                title=six.text_type('Organization resource'),
                model='plone.app.fhirfield.handler.FhirResourceHandler_'
            )
            raise AssertionError('Code should not come here! as should be invalid error')
        except Invalid as exc:
            self.assertIn('must be valid model class from fhirclient.model', str(exc))

        # test with invalid ResourceType
        try:
            field.FhirResource(
                title=six.text_type('Organization resource'),
                resource_type='FakeResource'
            )
            raise AssertionError('Code should not come here! as should be invalid error')
        except Invalid as exc:
            self.assertIn('FakeResource is not valid resource type', str(exc))
