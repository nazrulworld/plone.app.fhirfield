# _*_ coding: utf-8 _*_
from . import FHIR_FIXTURE_PATH
from plone.app.fhirfield import helpers
from plone.app.fhirfield.testing import PLONE_APP_FHIRFIELD_INTEGRATION_TESTING
from zope.interface import Invalid

import inspect
import os
import unittest


__author__ = 'Md Nazrul Islam<email2nazrul@gmail.com>'


class HelperIntegrationTest(unittest.TestCase):
    """ """
    layer = PLONE_APP_FHIRFIELD_INTEGRATION_TESTING

    def test_resource_type_to_dotted_model_name(self):
        """ """
        dotted_path = helpers.resource_type_to_dotted_model_name('DeviceRequest')
        self.assertEqual('fhirclient.models.devicerequest', dotted_path)

        dotted_path = helpers.resource_type_to_dotted_model_name('FakeResource', silent=True)
        self.assertIsNone(dotted_path)

        try:
            helpers.resource_type_to_dotted_model_name('FakeResource', silent=False)
            raise AssertionError('Code should not come here! because invalid resource is provided with explicit error')
        except KeyError:
            pass

    def test_resource_type_str_to_fhir_model(self):
        """ """
        task = helpers.resource_type_str_to_fhir_model('Task')

        self.assertTrue(inspect.isclass(task))

        self.assertEqual(task.resource_type, 'Task')

        try:
            helpers.resource_type_str_to_fhir_model('FakeResource')
            raise AssertionError('Code shouldn\'t come here! as invalid resource type is provided')
        except Invalid as e:
            self.assertIn('FakeResource', str(e))

    def test_import_string(self):
        """ """
        current_user_func = helpers.import_string('plone.api.user.get_current')
        self.assertTrue(inspect.isfunction(current_user_func))

        try:
            # Invalid dotted path!
            helpers.import_string('plone_api_user_get_current')
            raise AssertionError('Code shouldn\'t come here! as invalid dotted path is provided')
        except ImportError:
            pass

        try:
            # Invalid class or function!
            helpers.import_string('plone.api.user.fake')
            raise AssertionError('Code shouldn\'t come here! as invalid function name is provided')
        except ImportError:
            pass

        try:
            # Invalid pyton module!
            helpers.import_string('fake.fake.FakeClass')
            raise AssertionError('Code shouldn\'t come here! as invalid python module is provided')
        except ImportError:
            pass

    def test_parse_json_str(self):
        """ """
        with open(os.path.join(FHIR_FIXTURE_PATH, 'Organization.json'), 'r') as f:
            json_str = f.read()

        dict_data = helpers.parse_json_str(json_str)

        self.assertEqual(dict_data['resourceType'], 'Organization')

        json_str = """
        {"resourceType": "Task", Wrong: null}
        """
        try:
            helpers.parse_json_str(json_str)
            raise AssertionError('Code shouldn\'t come here! as invalid json string is provided')
        except Invalid:
            pass
