# _*_ coding: utf-8 _*_
from DateTime import DateTime
from plone.app.fhirfield.compat import _
from plone.app.fhirfield.compat import json
from plone.app.fhirfield.exc import SearchQueryValidationError
from plone.app.fhirfield.variables import ERROR_MESSAGES
from plone.app.fhirfield.variables import ERROR_PARAM_UNKNOWN
from plone.app.fhirfield.variables import ERROR_PARAM_UNSUPPORTED
from plone.app.fhirfield.variables import ERROR_PARAM_WRONG_DATATYPE
from plone.app.fhirfield.variables import FHIR_ES_MAPPINGS_CACHE
from plone.app.fhirfield.variables import FHIR_FIELD_DEBUG
from plone.app.fhirfield.variables import FHIR_RESOURCE_LIST  # noqa: F401
from plone.app.fhirfield.variables import FHIR_RESOURCE_MODEL_CACHE  # noqa: F401
from plone.app.fhirfield.variables import FHIR_SEARCH_PARAMETER_REGISTRY
from plone.app.fhirfield.variables import FHIR_SEARCH_PARAMETER_SEARCHABLE
from plone.app.fhirfield.variables import FSPR_KEYS_BY_GROUP
from plone.app.fhirfield.variables import FSPR_VALUE_PRIFIXES_MAP
from plone.app.fhirfield.variables import LOGGER
from plone.app.fhirfield.variables import SEARCH_PARAM_MODIFIERS

import mapping_types
import os
import six


__author__ = 'Md Nazrul Islam<email2nazrul@gmail.com>'


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
                        modifier):
        """ """
        if field == 'identifier':
            return self.add_identifier_query(field, modifier)

        path = self.find_query_path(field)

        mapping = get_elasticsearch_mapping(self.resource_type)
        mapped_field = path.replace(self.field_name + '.', '').split('.')[0]
        mapped_definition = mapping['properties'][mapped_field]

        if mapped_definition.get('properties'):
            nested = mapped_definition.get('type', None) == 'nested'

            if mapping_types.CodeableConcept.get('properties') == \
               mapped_definition.get('properties'):

                self.add_codeableconcept_query(
                        field, modifier,
                        path, nested)

            elif mapped_definition.get('properties') == \
                    mapping_types.Coding.get('properties'):

                self.add_coding_query(
                        field, modifier,
                        path, nested)

            elif mapped_definition.get('properties') == \
                    mapping_types.Address.get('properties'):
                # address query
                pass
            elif mapped_definition.get('properties') == \
                    mapping_types.ContactPoint.get('properties'):
                # address query
                pass

        else:
            self.add_str_token_query(field, modifier, path)

    def add_str_token_query(self,
                            field,
                            modifier,
                            path):
        """ """
        org_field = modifier and ':'.join([field, modifier]) or field
        value = self.params.get(org_field)

        if value in ('true', 'false'):
            if value == 'true':
                value = True
            else:
                value = False

        q = dict()

        if modifier == 'not':

            q['query'] = {'not': {'term': {path: value}}}
            self.query_tree['and'].append(q)

        else:
            q['term'] = {path: value}
            self.query_tree['and'].append(q)

    def add_codeableconcept_query(self,
                                  field,
                                  modifier,
                                  path,
                                  nested):
        """ """
        org_field = modifier and ':'.join([field, modifier]) or field
        value = self.params.get(org_field)

        if modifier == 'not':
            match_key = 'must_not'

        elif modifier == 'text':
            match_key = 'must'

        elif modifier in ('above', 'below'):
            # xxx: not implemnted yet
            match_key = 'must'

        else:
            match_key = 'must'

        matches = list()
        org_field = modifier and ':'.join([field, modifier]) or field
        value = self.params.get(org_field)
        has_pipe = '|' in value

        if modifier == 'text':
            # make CodeableConcept.text query
            matches.append({
                'match': {path + '.text': value},
                })

        elif has_pipe:

            pipe_matches = list()

            if value.startswith('|'):
                pipe_matches.append({
                    'match': {path + '.coding.code': value[1:]},
                })
            elif value.endswith('|'):
                pipe_matches.append({
                    'match': {path + '.coding.system': value[:-1]},
                })
            else:
                parts = value.split('|')
                try:
                    pipe_matches.append({
                        'match': {path + '.coding.system': parts[0]},
                    })

                    pipe_matches.append({
                        'match': {path + '.coding.code': parts[1]},
                    })

                except IndexError:
                    pass

            pipe_query = {
                'nested': {
                    'path': path + '.coding',
                    'query': {'bool': {'must': pipe_matches}},
                },
            }
            matches.append(pipe_query)

        else:
            matches.append({
                'match': {path + '.text': value},
                })

        if nested:
            query = {
                'nested': {
                    'path': path,
                    'query': {'bool': {match_key: matches}},
                },
            }
        else:
            query = {
                'query': {'bool': {match_key: matches}},
            }
        self.query_tree['and'].append(query)

    def add_coding_query(self,
                         field,
                         modifier,
                         path,
                         nested):
        """ """
        org_field = modifier and ':'.join([field, modifier]) or field
        value = self.params.get(org_field)

        if modifier == 'not':
            match_key = 'must_not'

        elif modifier == 'text':
            match_key = 'must'

        elif modifier in ('above', 'below'):
            # xxx: not implemnted yet
            match_key = 'must'

        else:
            match_key = 'must'

        matches = list()
        org_field = modifier and ':'.join([field, modifier]) or field
        value = self.params.get(org_field)
        has_pipe = '|' in value

        if modifier == 'text':
            # make CodeableConcept.text query
            matches.append({
                'match': {path + '.display': value},
                })

        elif has_pipe:

            if value.startswith('|'):
                matches.append({
                    'match': {path + '.code': value[1:]},
                })
            elif value.endswith('|'):
                matches.append({
                    'match': {path + '.system': value[:-1]},
                })
            else:
                parts = value.split('|')
                try:
                    matches.append({
                        'match': {path + '.system': parts[0]},
                    })

                    matches.append({
                        'match': {path + '.code': parts[1]},
                    })

                except IndexError:
                    pass

        else:
            matches.append({
                'match': {path + '.code': value},
                })

        if nested:
            query = {
                'nested': {
                    'path': path,
                    'query': {'bool': {match_key: matches}},
                },
            }
        else:
            query = {
                'query': {'bool': {match_key: matches}},
            }
        self.query_tree['and'].append(query)

    def add_cotactpoint_query(self,
                              field,
                              modifier,
                              path,
                              nested):
        """ """
        org_field = modifier and ':'.join([field, modifier]) or field
        value = self.params.get(org_field)

        if modifier == 'not':
            match_key = 'must_not'

        elif modifier == 'text':
            match_key = 'must'

        elif modifier in ('above', 'below'):
            # xxx: not implemnted yet
            match_key = 'must'

        else:
            match_key = 'must'

        matches = list()
        org_field = modifier and ':'.join([field, modifier]) or field
        value = self.params.get(org_field)
        has_pipe = '|' in value

        if modifier == 'text':
            # make CodeableConcept.text query
            matches.append({
                'match': {path + '.value': value},
                })

        elif has_pipe:

            if value.startswith('|'):
                matches.append({
                    'match': {path + '.value': value[1:]},
                })
            elif value.endswith('|'):
                matches.append({
                    'match': {path + '.use': value[:-1]},
                })
            else:
                parts = value.split('|')
                try:
                    matches.append({
                        'match': {path + '.use': parts[0]},
                    })

                    matches.append({
                        'match': {path + '.value': parts[1]},
                    })

                except IndexError:
                    pass

        else:
            matches.append({
                'match': {path + '.value': value},
                })

        if nested:
            query = {
                'nested': {
                    'path': path,
                    'query': {'bool': {match_key: matches}},
                },
            }
        else:
            query = {
                'query': {'bool': {match_key: matches}},
            }
        self.query_tree['and'].append(query)

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

        if prefix == 'ne' or modifier == 'not':
            self.query_tree['and'].append({'query': {'not': q}})
        else:
            self.query_tree['and'].append(q)

    def add_reference_query(self,
                            field,
                            modifier):
        """ """
        path = self.find_query_path(field)
        org_field = modifier and ':'.join([field, modifier]) or field

        mapping = get_elasticsearch_mapping(self.resource_type)
        mapped_field = path.replace(self.field_name + '.', '').split('.')[0]

        if mapping['properties'][mapped_field].get('type', None) == 'nested':
            nested = True
        else:
            nested = False

        q = dict()
        if '.reference' not in path:
            fullpath = path + '.reference'
        else:
            fullpath = path

        term = {fullpath: self.params.get(org_field)}

        if nested:
            if modifier == 'not':
                match_key = 'must_not'
            else:
                match_key = 'must'
            q = {
                'nested': {
                    'path': path,
                    'query': {'bool': {match_key: [
                        {'match': term},
                    ]}},
                },
            }
        else:
            if modifier == 'not':
                q['query'] = {
                    'not': {
                        'term': term,
                    },
                }
            else:
                q['term'] = {fullpath: self.params.get(org_field)}

        self.query_tree['and'].append(q)

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
            self.add_reference_query(field, modifier)

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
            self.add_reference_query(field, modifier)

    def add_identifier_query(self, field, modifier):
        """https://www.elastic.co/guide/en/elasticsearch/guide/current/nested-query.html
        """
        mapping = get_elasticsearch_mapping(self.resource_type)
        if mapping['properties']['identifier'].get('type', None) == 'nested':
            nested = True
        else:
            nested = False

        path = self.find_query_path(field)
        matches = list()

        org_field = modifier and ':'.join([field, modifier]) or field
        value = self.params.get(org_field)
        has_pipe = '|' in value

        if modifier == 'not':
            match_key = 'must_not'
        else:
            match_key = 'must'

        if modifier == 'text':
            # make dentifier.type.text query
            matches.append({
                'match': {path + '.type.text': value},
                })

        elif has_pipe:
            if value.startswith('|'):
                matches.append({
                    'match': {path + '.value': value[1:]},
                })
            elif value.endswith('|'):
                matches.append({
                    'match': {path + '.system': value[:-1]},
                })
            else:
                parts = value.split('|')
                try:
                    matches.append({
                        'match': {path + '.system': parts[0]},
                    })

                    matches.append({
                        'match': {path + '.value': parts[1]},
                    })

                except IndexError:
                    pass
        else:
            matches.append({
                'match': {path + '.value': value},
                })

        if nested:
            query = {
                'nested': {
                    'path': path,
                    'query': {'bool': {match_key: matches}},
                },
            }
        else:
            query = {
                'query': {'bool': {match_key: matches}},
            }
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


def get_elasticsearch_mapping(resource, mapping_dir=None, cache=True):
    """Elastic search mapping for FHIR resources"""

    key = resource.lower()
    if mapping_dir is None:
        mapping_dir = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            'indexes',
            'es',
            'mapping')

    if key not in FHIR_ES_MAPPINGS_CACHE or cache is False:
        file_location = None
        expected_filename = '{0}.mapping.json'.format(FHIR_RESOURCE_LIST[key]['name'])
        for root, dirs, files in os.walk(mapping_dir, topdown=True):
            for filename in files:
                if filename == expected_filename:
                    file_location = os.path.join(root, filename)
                    break

        if file_location is None:
            raise LookupError(
                'Mapping files {0}/{1} doesn\'t exists.'.
                format(mapping_dir, expected_filename),
                )

        with open(os.path.join(root, file_location), 'r') as f:
            content = json.load(f)
            assert filename.split('.')[0] == content['resourceType']

            FHIR_ES_MAPPINGS_CACHE[key] = content

    return FHIR_ES_MAPPINGS_CACHE[key]['mapping']
