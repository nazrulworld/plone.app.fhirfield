# _*_ coding: utf-8 _*_
from . import FHIR_FIXTURE_PATH
from plone.app.fhirfield import compat
from plone.app.fhirfield import helpers
from plone.app.fhirfield.testing import PLONE_APP_FHIRFIELD_INTEGRATION_TESTING
from six.moves.urllib.parse import urlencode
from zope.interface import Invalid

import inspect
import os
import unittest


__author__ = "Md Nazrul Islam<email2nazrul@gmail.com>"


class HelperIntegrationTest(unittest.TestCase):
    """ """

    layer = PLONE_APP_FHIRFIELD_INTEGRATION_TESTING

    def test_search_fhir_model(self):
        """ """
        dotted_path = helpers.search_fhir_model("DeviceRequest")
        self.assertEqual("fhir.resources.devicerequest.DeviceRequest", dotted_path)

        dotted_path = helpers.search_fhir_model("FakeResource")
        self.assertIsNone(dotted_path)

    def test_caching_of_search_fhir_model(self):
        """ """
        helpers.FHIR_RESOURCE_MODEL_CACHE.clear()
        dotted_path = helpers.search_fhir_model("DeviceRequest")
        self.assertEqual("fhir.resources.devicerequest.DeviceRequest", dotted_path)

        self.assertEqual(len(helpers.FHIR_RESOURCE_MODEL_CACHE), 1)

    def test_resource_type_str_to_fhir_model(self):
        """ """
        task = helpers.resource_type_str_to_fhir_model("Task")

        self.assertTrue(inspect.isclass(task))

        self.assertEqual(task.resource_type, "Task")

        try:
            helpers.resource_type_str_to_fhir_model("FakeResource")
            raise AssertionError(
                "Code shouldn't come here! as invalid resource type is provided"
            )
        except Invalid as e:
            self.assertIn("FakeResource", str(e))

    def test_import_string(self):
        """ """
        current_user_func = helpers.import_string("plone.api.user.get_current")
        self.assertTrue(inspect.isfunction(current_user_func))

        try:
            # Invalid dotted path!
            helpers.import_string("plone_api_user_get_current")
            raise AssertionError(
                "Code shouldn't come here! as invalid dotted path is provided"
            )
        except ImportError:
            pass

        try:
            # Invalid class or function!
            helpers.import_string("plone.api.user.fake")
            raise AssertionError(
                "Code shouldn't come here! as invalid function name is provided"
            )
        except ImportError:
            pass

        try:
            # Invalid pyton module!
            helpers.import_string("fake.fake.FakeClass")
            raise AssertionError(
                "Code shouldn't come here! as invalid python module is provided"
            )
        except ImportError:
            pass

    def test_parse_json_str(self):
        """ """
        with open(os.path.join(FHIR_FIXTURE_PATH, "Organization.json"), "r") as f:
            json_str = f.read()

        dict_data = helpers.parse_json_str(json_str)

        self.assertEqual(dict_data["resourceType"], "Organization")

        json_str = """
        {"resourceType": "Task", Wrong: null}
        """
        try:
            helpers.parse_json_str(json_str)
            raise AssertionError(
                "Code shouldn't come here! as invalid json string is provided"
            )
        except Invalid:
            pass

    def test_parse_json_str_with_empty(self):
        """ """
        value = helpers.parse_json_str(compat.NO_VALUE)
        self.assertIsNone(value)

        value = helpers.parse_json_str(compat.EMPTY_STRING)
        self.assertIsNone(value)

    def test_fhir_search_path_meta_info(self):
        """ """
        js_name, is_list, of_many = helpers.fhir_search_path_meta_info(
            "Resource.meta.profile"
        )

        self.assertEqual(js_name, "profile")
        self.assertTrue(is_list)
        self.assertIsNone(of_many)

        js_name, is_list, of_many = helpers.fhir_search_path_meta_info(
            "ActivityDefinition.url"
        )

        self.assertFalse(is_list)

    def test_translate_param_name_to_real_path(self):
        """Test param translation"""

        path = helpers.translate_param_name_to_real_path(
            "related-target", "Observation"
        )

        self.assertIsNotNone(path, "Observation")
        self.assertEqual(path, "Observation.related.target")

        # test with logic in path (AS)
        path = helpers.translate_param_name_to_real_path("value-date", "Observation")

        self.assertEqual(path, "Observation.valueDateTime")

        # test with logic in path (IS)
        path = helpers.translate_param_name_to_real_path(
            "abatement-boolean", "Condition"
        )

        self.assertEqual(path, "Condition.abatementRange")

        # test with logic in path (WHERE)
        path = helpers.translate_param_name_to_real_path("email", "RelatedPerson")

        self.assertEqual(path, "RelatedPerson.telecom")

        # test with missing
        path = helpers.translate_param_name_to_real_path("fake-param")

        self.assertIsNone(path)

    def test_parse_query_string(self):
        """ """
        request = dict()
        params = [
            ("patient", "P001"),
            ("lastUpdated", "2018-01-01"),
            ("lastUpdated", "lt2018-09-10"),
        ]

        request["QUERY_STRING"] = urlencode(params)

        results = helpers.parse_query_string(request)

        items = [p[0] for p in results if p[0] == "lastUpdated"]
        self.assertEqual(len(items), 2)

        # Test with empty value [allowed]
        request["QUERY_STRING"] = urlencode(params) + "&lastUpdated"

        results = helpers.parse_query_string(request, True)
        items = [p[0] for p in results if p[0] == "lastUpdated"]
        self.assertEqual(len(items), 3)

        # Test with empty value [not allowed]
        request["QUERY_STRING"] = urlencode(params) + "&lastUpdated"

        results = helpers.parse_query_string(request)
        items = [p[0] for p in results if p[0] == "lastUpdated"]

        self.assertEqual(len(items), 2)
