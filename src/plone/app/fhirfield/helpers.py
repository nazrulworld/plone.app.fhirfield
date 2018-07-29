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

FSPR_VALUE_PRIFIXES_MAP = {'eq': None,
                           'ne': None,
                           'gt': 'gt',
                           'lt': 'lt',
                           'ge': 'gte',
                           'le': 'lte',
                           'sa': None,
                           'eb': None,
                           'ap': None}


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
                  'supported as FHIR search parameter',
                  mapping={'params': str(unwanted)}))

        self.field_name = field_name
        self.resource_type = resource_type
        self.handling = handling
        self.query_tree = dict(should=list(),
                               must=list(),
                               must_not=list(),
                               filter=list())

        self.validate(params)
        self.params = params

    def add_token_query(self,
                        field,
                        modifier,
                        datatype=None):
        """ """
        path = self.find_query_path(field)
        org_field = modifier and ':'.join([field, modifier]) or field
        value = self.params.get(org_field)

        if datatype is None:
            if value in ('true', 'false'):
                datatype = 'boolen'

                if value == 'true':
                    value = True
                else:
                    value = False
            else:
                datatype = 'string'

        q = dict()

        if modifier == 'not':

            q['match'] = {path: value}
            self.query_tree['must_not'].append(q)

        elif modifier == 'in':
            # xxx: not implemnted yet
            pass

        elif modifier == 'not-in':
            # xxx: not implemented yet
            pass
        elif modifier in ('above', 'below'):
            # xxx: not implemnted yet
            pass

        else:
            q['match'] = {path: value}
            self.query_tree['must'].append(q)

    def add_date_query(self,
                       field,
                       modifier):
        """ """
        path = self.find_query_path(field)
        org_field = modifier and ':'.join([field, modifier]) or field
        value = self.params.get(org_field)
        prefix = 'eq'

        if value[0:2] in FSPR_VALUE_PRIFIXES_MAP:
            prefix = value[0:2]
            value = value[2:]
        _iso8601 = DateTime(value).ISO8601()

        if '+' in _iso8601:
            parts = _iso8601.split('+')
            timezone = '+{0!s}'.format(parts[1])
            value = parts[0]
        else:
            timezone = None
            value = _iso8601

        q = dict()

        if prefix in ('eq', 'ne'):
            q['range'] = {
                path: {
                    FSPR_VALUE_PRIFIXES_MAP.get('ge'): value,
                    FSPR_VALUE_PRIFIXES_MAP.get('le'): value,
                },
            }

        elif prefix in ('le', 'lt', 'ge', 'gt'):
            q['range'] = {
                path: {
                    FSPR_VALUE_PRIFIXES_MAP.get(prefix): value,
                },
            }

        if timezone:
            q['range'][path]['time_zone'] = timezone

        if prefix == 'ne':
            self.query_tree['must_not'].append(q)
        else:
            self.query_tree['must'].append(q)

    def add_reference_query(self,
                            field,
                            modifier,
                            datatype=None):
        """ """
        path = self.find_query_path(field)
        org_field = modifier and ':'.join([field, modifier]) or field

        if datatype is None:
            datatype = 'object'

        q = dict()
        if datatype == 'object':
            if '.reference' not in path:
                path += '.reference'
            q['match'] = {path: self.params.get(org_field)}
            self.query_tree['must'].append(q)

        elif datatype == 'array':
            # xxx: see elaticsearch array
            pass

    def build(self):
        """
        https://www.elastic.co/guide/en/elasticsearch/reference/2.3/query-dsl-bool-query.html
        https://www.elastic.co/guide/en/elasticsearch/guide/current/_finding_multiple_exact_values.html
        https://stackoverflow.com/questions/16243496/nested-boolean-queries-in-elastic-search
        """
        for r_field, value in self.params.items():
            """ """
            parts = r_field.split(':')
            try:
                r_field = parts[0]
                modifier = parts[1]
            except IndexError:
                modifier = None

            if r_field in FSPR_KEYS_BY_GROUP.\
                    get('Resource'):
                self.build_resource_parameters(r_field, modifier)

            elif r_field in FSPR_KEYS_BY_GROUP.\
                    get('Common Search Parameters'):
                self.build_common_search_parameters(r_field, modifier)

            elif r_field in FSPR_KEYS_BY_GROUP.\
                    get(self.resource_type):
                try:
                    method = 'build_{0}_search_parameters'.\
                        format(self.resource_type.lower())

                    getattr(self, method)(r_field, modifier)

                except AttributeError:
                    self.build_search_parameters(r_field, modifier)

        return self.query_tree.copy()

    def build_resource_parameters(self, field, modifier=None):
        """ """
        param = self.get_parameter(
            field,
            FHIR_SEARCH_PARAMETER_REGISTRY.get('Resource'))

        if param[1] == 'token':
            # xxx: data type have to implement
            self.add_token_query(field, modifier)

        elif param[1] == 'date':
            self.add_date_query(field, modifier)

        elif param[1] == 'uri':

            path = param[3][0].replace('Resource', self.field_name)
            value = self.params.get(field)
            q = {'terms': {path: [value], 'minimum_should_match': 1}}
            self.query_tree['must'].append(q)

    def build_common_search_parameters(self, field, modifier):
        """ """
        param_type = FHIR_SEARCH_PARAMETER_SEARCHABLE[field][0]

        if param_type == 'token':
            # xxx: data type have to implement
            # xxx: identify other data type?
            self.add_token_query(field, modifier)

        elif param_type == 'date':
            self.add_date_query(field, modifier)

        elif param_type == 'reference':
            # xxx: data type for other reference? like partOf?
            self.add_reference_query(field, modifier, 'object')

    def build_search_parameters(self, field, modifier):
        """ """
        param_type = FHIR_SEARCH_PARAMETER_SEARCHABLE[field][0]

        if param_type == 'token':
            # xxx: data type have to implement
            # xxx: identify other data type?
            self.add_token_query(field, modifier)

        elif param_type == 'date':
            self.add_date_query(field, modifier)

        elif param_type == 'reference':
            # xxx: data type
            self.add_reference_query(field, modifier)

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

    def find_query_path(self, r_field):
        """:param: r_field: resource field"""
        if r_field in FHIR_SEARCH_PARAMETER_SEARCHABLE:
            paths = FHIR_SEARCH_PARAMETER_SEARCHABLE[r_field][1]

            for path in paths:

                if path.startswith('Resource.'):
                    return path.replace('Resource', self.field_name)

                if path.startswith(self.resource_type):
                    return path.replace(self.resource_type, self.field_name)


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


class ElasticsearchSortQueryBuilder(object):
    """https://elasticsearch-py.readthedocs.io/en/master/api.html#elasticsearch.Elasticsearch.search
    """

    def __init__(self,
                 params,
                 field_name,
                 resource_type):
        """ """
        self.sort_on = params.pop('_sort', None)
        self.sort_order = 'asc'
        if self.sort_on:
            self.sort_on = self.sort_on.split(',')

            for index, item in enumerate(self.sort_on):
                if item.startswith('-'):
                    self.sort_order = 'desc'
                    self.sort_on[index] = item[1:]

    def build(self):
        """ """
