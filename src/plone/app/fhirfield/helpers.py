# _*_ coding: utf-8 _*_
from .compat import EMPTY_STRING
from .compat import NO_VALUE
from collections import defaultdict
from importlib import import_module
from plone.api.validation import required_parameters
from plone.app.fhirfield.compat import _
from plone.app.fhirfield.compat import json
from zope.interface import Invalid

import pkgutil
import six
import sys


__author__ = 'Md Nazrul Islam<email2nazrul@gmail.com>'

FHIR_RESOURCE_MODEL_CACHE = defaultdict()


@required_parameters('model_name')
def search_fhir_model(model_name, cache=True):
    """ """
    global FHIR_RESOURCE_MODEL_CACHE
    if model_name in FHIR_RESOURCE_MODEL_CACHE.keys() and cache:
        return '{0}.{1}'.format(FHIR_RESOURCE_MODEL_CACHE[model_name], model_name)

    # Trying to get from entire modules
    from fhirclient import models
    for importer, modname, ispkg in \
            pkgutil.walk_packages(models.__path__, models.__name__ + '.', onerror=lambda x: None):
        if ispkg or modname.endswith('_tests'):
            continue

        mod = import_module(modname)
        if getattr(mod, model_name, None):
            FHIR_RESOURCE_MODEL_CACHE[model_name] = modname
            return '{0}.{1}'.format(modname, model_name)

    return None


@required_parameters('resource_type')
def resource_type_str_to_fhir_model(resource_type):
    """ """
    dotted_path = search_fhir_model(resource_type)
    if dotted_path is None:
        raise Invalid(_('Invalid: `{0}` is not valid resource type!'.format(resource_type)))

    return import_string(dotted_path)


@required_parameters('dotted_path')
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


@required_parameters('str_val')
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
