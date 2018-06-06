# _*_ coding: utf-8 _*_
from .compat import EMPTY_STRING
from .compat import NO_VALUE
from collections import defaultdict
from DateTime import DateTime
from importlib import import_module
from plone.api.validation import required_parameters
from plone.app.fhirfield.compat import _
from plone.app.fhirfield.compat import json
from zope.interface import Invalid

import logging
import os
import pkgutil
import six
import sys


__author__ = 'Md Nazrul Islam<email2nazrul@gmail.com>'

logger = logging.getLogger('plone.app.fhirfield')
FHIR_FIELD_DEBUG = os.environ.get('FHIR_FIELD_DEBUG', '').lower() in \
    ('y', 'yes', 't', 'true', '1')
FHIR_RESOURCE_MODEL_CACHE = defaultdict()

FHIR_STATIC_DIR = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    'browser',
    'static',
    'FHIR')

with open(os.path.join(FHIR_STATIC_DIR, 'HL7',
                       'search',
                       'FHIR-Search-Parameter-Registry.json')) as f:

    FHIR_SEARCH_PARAMETER_REGISTRY = json.load(f)['object']

with open(os.path.join(FHIR_STATIC_DIR, 'HL7',
                       'search',
                       'FHIR-Search-Parameter-Registry-searchable.json')) as f:

    FHIR_SEARCH_PARAMETER_SEARCHABLE = json.load(f)['searchable']
    FHIR_SEARCH_PARAMETER_SEARCHABLE_KEYS = FHIR_SEARCH_PARAMETER_SEARCHABLE.keys()

FSPR_KEYS_BY_GROUP = dict()

for group, rows in FHIR_SEARCH_PARAMETER_REGISTRY.items():
    FSPR_KEYS_BY_GROUP[group] = list()
    for row in rows[1:]:
        FSPR_KEYS_BY_GROUP[group].append(row[0])


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
        six.reraise(Invalid,
                    Invalid('Invalid JSON String is provided!\n{0!s}'.format(exc)), sys.exc_info()[2])

    return json_dict


class ElasticsearchQueryBuilder(object):
    """Unknown and unsupported parameters
    Servers may receive parameters from the client that they do not recognise,
    or may receive parameters they recognise but do not support
    (either in general, or for a specific search). In general, servers
    SHOULD ignore unknown or unsupported parameters for the following reasons:

    Various HTTP stacks and proxies may add parameters that aren't under the control of the client
    The client can determine what parameters the server used by examining the self link in the return (see below)
    Clients can specify how the server should behave, by using the prefer header

    Prefer: handling=strict: Client requests that the server return an error for any unknown or unsupported parameter
    Prefer: handling=lenient: Client requests that the server ignore any unknown or unsupported parameter
"""
    def __init__(self,
                 params,
                 field_name,
                 resource_type,
                 handling='strict'):

        unwanted = self.clean_params(params)
        if handling == 'strict' and len(unwanted) > 0:
            raise Invalid(
                _('Unwanted params ${params} are found, those are not '
                  'supported as FHIR search parameter'),
                mapping={'params': str(unwanted)})

        self.field_name = field_name
        self.resource_type = resource_type
        self.handling = handling
        self.query_tree = dict(should=list(),
                               must=list(),
                               must_not=dict(),
                               filter=dict(),)

        self.validate(params)
        self.params = params

    def build(self):
        """
        https://www.elastic.co/guide/en/elasticsearch/reference/2.3/query-dsl-bool-query.html
        https://www.elastic.co/guide/en/elasticsearch/guide/current/_finding_multiple_exact_values.html
        https://stackoverflow.com/questions/16243496/nested-boolean-queries-in-elastic-search
        """
        for field, value in self.params.items():
            """ """
            if field in FSPR_KEYS_BY_GROUP.\
                    get('Resource'):
                self.build_resource_parameters(field)
            elif field in FSPR_KEYS_BY_GROUP.\
                    get('Common Search Parameters'):
                self.build_common_search_parameters(field)
            elif field in FSPR_KEYS_BY_GROUP.\
                    get(self.resource_type):
                # TODO: build_${resource_type}
                pass

        return self.query_tree.copy()

    def build_resource_parameters(self, field):
        """ """
        param = self.get_parameter(
            field,
            FHIR_SEARCH_PARAMETER_REGISTRY.get('Resource'))

        if param[1] in ('token', 'uri',):

            q = {
                'match':
                {
                    param[3][0].replace('Resource', self.field_name): self.params.get(field)
                }
            }
            self.query_tree['must'].append(q)
        elif param[1] == 'date':
            value = self.params.get(field)
            value = DateTime(value).ISO8601()
            q = {
                'match':
                {
                    param[3][0].replace('Resource', self.field_name): value
                }
            }
            self.query_tree['must'].append(q)

    def build_common_search_parameters(self, field):
        """ """

    def clean_params(self, params):
        """ """
        unwanted = list()

        for param in params.keys():
            parts = param.split(':')

            if parts[0] not in FHIR_SEARCH_PARAMETER_SEARCHABLE_KEYS:
                unwanted.append(param)
                del params[param]

        FHIR_FIELD_DEBUG and \
            unwanted and \
            logger.info(
                'ElasticsearchQueryBuilder: unwanted {0!s} parameter(s) '
                'have been cleaned'.format(unwanted))
        return unwanted

    def validate(self, params):
        """ """
        return

    def get_parameter(self, field, parameters):

        for param in parameters:
            if param[0] == field:
                return param


def build_elasticsearch_query(params,
                              field_name,
                              resource_type=None,
                              handling='strict'):
    """This is the helper method for making elasticsearch compatiable query from
    HL7 FHIR search standard request params"""
    builder = ElasticsearchQueryBuilder(params,
                                        field_name,
                                        resource_type,
                                        handling)

    return builder.build()
