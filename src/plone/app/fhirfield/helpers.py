# _*_ coding: utf-8 _*_
from .compat import EMPTY_STRING
from .compat import NO_VALUE
from importlib import import_module
from plone.app.fhirfield.compat import _
from plone.app.fhirfield.compat import json
from zope.interface import Invalid

import six
import sys


__author__ = 'Md Nazrul Islam<email2nazrul@gmail.com>'

fhir_resource_models_map = {
    'Bundle': 'fhirclient.models.bundle',
    'Device': 'fhirclient.models.device',
    'Patient': 'fhirclient.models.patient',
    'Task': 'fhirclient.models.task',
    'ProcedureRequest': 'fhirclient.models.procedurerequest',
    'Questionnaire': 'fhirclient.models.questionnaire',
    'Practitioner': 'fhirclient.models.practitioner',
    'Person': 'fhirclient.models.person',
    'QuestionnaireResponse': 'fhirclient.models.questionnaireresponse',
    'Observation': 'fhirclient.models.observation',
    'Organization': 'fhirclient.models.organization',
    'ActivityDefinition': 'fhirclient.models.activitydefinition',
    'DeviceRequest': 'fhirclient.models.devicerequest',
    'ValueSet': 'fhirclient.models.valueset',
    'HealthcareService': 'fhirclient.models.healthcareservice'
}


def resource_type_to_dotted_model_name(resource_type, silent=False):
    """Simple helper function to feed dotted resource model name from models map"""
    try:
        return fhir_resource_models_map[resource_type]
    except KeyError as e:
        if not silent:
            raise e
    return None


def resource_type_str_to_fhir_model(resource_type):
    """ """
    dotted_path = resource_type_to_dotted_model_name(resource_type, True)
    if dotted_path is None:
        raise Invalid(_('Invalid: `{0}` is not valid resource type!'.format(resource_type)))

    return import_string('{0}.{1}'.format(dotted_path, resource_type))


def import_string(dotted_path):
    """Shameless hack from django utils, please don't mind!"""
    try:
        module_path, class_name = dotted_path.rsplit('.', 1)
    except (ValueError, AttributeError):
        msg = "{0} doesn't look like a module path".format(dotted_path)
        six.reraise(ImportError, ImportError(msg), sys.exc_info()[2])

    module = import_module(module_path)

    try:
        return getattr(module, class_name)
    except AttributeError:
        msg = 'Module "{0}" does not define a "{1}" attribute/class'.format(
            module_path, class_name)
        six.reraise(ImportError, ImportError(msg), sys.exc_info()[2])


def parse_json_str(str_val, encoding='utf-8'):
    """ """
    if str_val in (NO_VALUE, EMPTY_STRING, None):
        # No parsing for empty value
        return None

    try:
        json_dict = json.loads(str_val, encoding=encoding)
    except ValueError as exc:
        six.reraise(Invalid, Invalid('Invalid JSON String is provided!\n{0!s}'.format(exc)), sys.exc_info()[2])

    return json_dict
