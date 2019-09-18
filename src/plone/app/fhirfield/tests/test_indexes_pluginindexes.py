# -*- coding: utf-8 -*-
"""Setup tests for this package."""
import json
import os
import unittest

from plone.app.fhirfield.indexes.PluginIndexes.FHIRIndex import \
    FhirFieldIndex  # noqa: E501
from plone.app.fhirfield.indexes.PluginIndexes.FHIRIndex import make_fhir_index_datum
from plone.app.fhirfield.testing import \
    PLONE_APP_FHIRFIELD_INTEGRATION_TESTING  # noqa: E501

from . import FHIR_FIXTURE_PATH


__author__ = "Md Nazrul Islam<email2nazrul@gamil.com>"


class FHIRIndexIntergrationTest(unittest.TestCase):
    """Test that plone.app.fhirfield is properly installed."""

    layer = PLONE_APP_FHIRFIELD_INTEGRATION_TESTING

    def test_fhir_index_datum(self):
        """Test datum for zope PluginIndex"""
        with open(os.path.join(FHIR_FIXTURE_PATH, "Organization.json"), "r") as f:
            fhir_json = json.load(f)
        # xxx: need improvment to work with all mappings, not just default
        index_datum = make_fhir_index_datum(
            FhirFieldIndex("organization_resource").default_mapping.get("properties"),
            fhir_json,
        )

        expected = {
            "id": fhir_json["id"],
            "resourceType": fhir_json["resourceType"],
            "meta": {
                "lastUpdated": fhir_json["meta"]["lastUpdated"],
                "versionId": fhir_json["meta"]["versionId"],
            },
        }
        self.assertEqual(index_datum, expected)
