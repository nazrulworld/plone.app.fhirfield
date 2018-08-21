# _*_ coding: utf-8 _*_
from .compat import EMPTY_STRING
from .compat import NO_VALUE
from .exc import SearchQueryError
from .exc import SearchQueryValidationError
from .variables import ERROR_MESSAGES
from .variables import ERROR_PARAM_UNKNOWN
from .variables import ERROR_PARAM_UNSUPPORTED
from .variables import ERROR_PARAM_WRONG_DATATYPE
from .variables import FHIR_FIELD_DEBUG
from .variables import FHIR_RESOURCE_LIST  # noqa: F401
from .variables import FHIR_RESOURCE_MODEL_CACHE  # noqa: F401
from .variables import FHIR_SEARCH_PARAMETER_REGISTRY
from .variables import FHIR_SEARCH_PARAMETER_SEARCHABLE
from .variables import FSPR_KEYS_BY_GROUP
from .variables import FSPR_VALUE_PRIFIXES_MAP
from .variables import LOGGER
from .variables import SEARCH_PARAM_MODIFIERS
from DateTime import DateTime
from importlib import import_module
from plone.api.validation import required_parameters
from plone.app.fhirfield.compat import _
from plone.app.fhirfield.compat import json
from zope.interface import Invalid

import os
import pkgutil
import six
import sys


__author__ = 'Md Nazrul Islam<email2nazrul@gmail.com>'


@required_parameters('model_name')
def search_fhir_model(model_name, cache=True):
    """ """
    global FHIR_RESOURCE_MODEL_CACHE
    if model_name in FHIR_RESOURCE_MODEL_CACHE.keys() and cache:
        return '{0}.{1}'.format(
            FHIR_RESOURCE_MODEL_CACHE[model_name],
            model_name)

    # Trying to get from entire modules
    from fhirclient import models
    for importer, modname, ispkg in \
            pkgutil.walk_packages(models.__path__, models.__name__ + '.',
                                  onerror=lambda x: None):
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
        raise SearchQueryValidationError(
            _('Invalid: `{0}` is not valid resource type!'.
              format(resource_type)))

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
                    Invalid('Invalid JSON String is provided!\n{0!s}'.
                            format(exc)), sys.exc_info()[2])

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

        self.field_name = field_name
        self.resource_type = resource_type
        self.handling = handling
        self.params = params

        self.validate()

        self.query_tree = {'and': list()}

    def add_token_query(self,
                        field,
                        modifier,
                        datatype=None):
        """ """
        if field == 'identifier':
            return self.add_identifier_query(field, modifier)

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

            q['query'] = {'not': {'term': {path: value}}}
            self.query_tree['and'].append(q)

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
            q['term'] = {path: value}
            self.query_tree['and'].append(q)

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
            self.query_tree['and'].append({'query': {'not': q}})
        else:
            self.query_tree['and'].append(q)

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
            q['term'] = {path: self.params.get(org_field)}
            self.query_tree['and'].append(q)

        elif datatype == 'array':
            # xxx: see elaticsearch array
            pass

    def add_exists_query(self, field, modifier):
        """https://www.elastic.co/guide/en/elasticsearch/reference/2.4/query-dsl-exists-query.html
        """
        path = self.find_query_path(field)
        org_field = ':'.join([field, modifier])
        value = self.params.get(org_field)
        q = dict(query=dict())
        if (modifier == 'missing' and value == 'true') or \
                (modifier == 'exists' and value == 'false'):
            q['query']['bool'] = \
                {
                    'must_not': {'exists': {'field': path}},
                }
        elif (modifier == 'missing' and value == 'false') or \
                (modifier == 'exists' and value == 'true'):

            q['query']['exists'] = {'field': path}

        self.query_tree['and'].append(q)

    def build(self):
        """
        https://www.elastic.co/guide/en/elasticsearch/reference/2.4/query-dsl-exists-query.html
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

            if modifier in ('missing', 'exists'):
                self.add_exists_query(*parts)
                continue

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
            q = {'terms': {path: [value]}}
            self.query_tree['and'].append(q)

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

    def add_identifier_query(self, field, modifier):
        """https://www.elastic.co/guide/en/elasticsearch/guide/current/nested-query.html
        """
        path = self.find_query_path(field)
        query = {
            'nested': {
                'path': path,
                'query': {'bool': {'must': list()}},
            },
        }
        org_field = modifier and ':'.join([field, modifier]) or field
        value = self.params.get(org_field)

        if modifier == 'text':
            # make dentifier.type.text query
            query['nested']['query']['bool']['must'].append({
                'match': {path + '.type.text': value},
                })
            self.query_tree['and'].append(query)
            return
        has_pipe = '|' in value

        if has_pipe:
            if value.startswith('|'):
                query['nested']['query']['bool']['must'].append({
                    'match': {path + '.value': value[1:]},
                })
            elif value.endswith('|'):
                query['nested']['query']['bool']['must'].append({
                    'match': {path + '.system': value[:-1]},
                })
            else:
                parts = value.split('|')
                try:
                    query['nested']['query']['bool']['must'].append({
                        'match': {path + '.system': parts[0]},
                    })

                    query['nested']['query']['bool']['must'].append({
                        'match': {path + '.value': parts[1]},
                    })

                except IndexError:
                    pass
        else:
            query['nested']['query']['bool']['must'].append({
                'match': {path + '.value': value},
                })

        self.query_tree['and'].append(query)

    def clean_params(self):
        """ """
        unwanted = list()

        for param in self.params.keys():
            parts = param.split(':')

            if parts[0] not in FHIR_SEARCH_PARAMETER_SEARCHABLE:
                unwanted.append((param, ERROR_PARAM_UNKNOWN))
                del self.params[param]
                continue

            if parts[0] in ('_content', '_id', '_lastUpdated',
                            '_profile', '_query', '_security',
                            '_tag', '_text'):
                continue

            supported_paths = \
                FHIR_SEARCH_PARAMETER_SEARCHABLE[parts[0]][1]

            for path in supported_paths:
                if path.startswith(self.resource_type):
                    break
            else:
                del self.params[param]
                unwanted.append((param, ERROR_PARAM_UNSUPPORTED))

        FHIR_FIELD_DEBUG and \
            unwanted and \
            LOGGER.info(
                'ElasticsearchQueryBuilder: unwanted {0!s} parameter(s) '
                'have been cleaned'.format(unwanted))
        return unwanted

    def validate(self):
        """ """
        unwanted = self.clean_params()

        if self.handling == 'strict' and len(unwanted) > 0:

            errors = self.process_error_message(unwanted)

            raise SearchQueryValidationError(
                _('Unwanted search parameters are found, {0!s}').
                format(errors),
                )

        error_fields = list()

        for param, value in six.iteritems(self.params):
            """ """
            parts = param.split(':')
            try:
                name = parts[0]
                modifier = parts[1]
            except IndexError:
                modifier = None

            if modifier and (modifier not in SEARCH_PARAM_MODIFIERS):
                error_fields.append((
                    name,
                    _('Unsupported modifier has been attached with parameter.'
                      'Allows modifiers are {0!s}'.
                      format(SEARCH_PARAM_MODIFIERS)),
                    ))
                continue

            if modifier in ('missing', 'exists') and \
                    value not in ('true', 'false'):
                error_fields.append((param, ERROR_PARAM_WRONG_DATATYPE))
                continue

            param_type = FHIR_SEARCH_PARAMETER_SEARCHABLE[name][0]

            if param_type == 'date':
                self.validate_date(name, modifier, value, error_fields)
            elif param_type == 'token':
                self.validate_token(name, modifier, value, error_fields)

        if error_fields:
            errors = self.process_error_message(error_fields)
            raise SearchQueryValidationError(
                _('Validation failed, {0!s}').format(errors))

    def validate_date(self, field, modifier, value, container):
        """ """
        if modifier:
            container.append((
                field,
                _('date type parameter don\'t accept any modifier except `missing`'),
            ))
        else:
            prefix = value[0:2]
            if prefix in FSPR_VALUE_PRIFIXES_MAP:
                date_val = value[2:]
            else:
                date_val = value

            try:
                DateTime(date_val)
            except Exception:
                container.append((field, '{0} is not valid date string!'.format(value)))

    def validate_token(self, field, modifier, value, container):
        """ """
        if modifier == 'text' and '|' in value:
            container.append((
                field,
                _('Pipe (|) is not allowed in value, when `text` modifier is provided'),
            ))
        elif len(value.split('|')) > 2:

            container.append((
                field,
                _('Only single Pipe (|) can be used as separator!'),
            ))

    def process_error_message(self, errors):
        """ """
        container = list()
        for field, code in errors:
            try:
                container.append({
                    'name': field,
                    'error': ERROR_MESSAGES[code],
                    })
            except KeyError:
                container.append({
                    'name': field,
                    'error': code,
                    })
        return container

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
    if not isinstance(params, dict):
        raise TypeError(
            'parameters must be dict data type, but got {0}'.
            format(type(params)))

    builder = ElasticsearchQueryBuilder(params.copy(),
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


def make_fhir_elasticsearch_list(mapping_dir):
    """ """
    container = dict()

    for root, dirs, files in os.walk(mapping_dir, topdown=True):

        for filename in files:

            if not filename.endswith('.json'):
                continue

            with open(os.path.join(root, filename), 'r') as f:
                content = json.load(f)

            assert filename.split('.')[0] == content['resourceType']

            container[content['resourceType'].lower()] = content

    return container


def validate_index_name(name):
    """ZCatalog index name validation"""
    global FHIR_RESOURCE_LIST

    parts = name.split('_')

    try:
        FHIR_RESOURCE_LIST[parts[0].lower()]
    except KeyError:
        msg = _(
            'Invalid index name for FhirFieldIndex. Index name must start with '
            'any valid fhir resource type name as prefix or just use '
            'resource type name as index name.\n'
            'allowed format: (resource type as prefix)_(your name), '
            '(resource_type as index name)\n'
            'example: hospital_resource, patient')

        six.reraise(SearchQueryError, SearchQueryError(msg), sys.exc_info()[2])
