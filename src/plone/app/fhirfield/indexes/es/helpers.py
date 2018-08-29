# _*_ coding: utf-8 _*_
from DateTime import DateTime
from plone.api.validation import at_least_one_of
from plone.api.validation import mutually_exclusive_parameters
from plone.app.fhirfield.compat import _
from plone.app.fhirfield.compat import json
from plone.app.fhirfield.exc import SearchQueryValidationError
from plone.app.fhirfield.helpers import fhir_search_path_meta_info
from plone.app.fhirfield.variables import ERROR_MESSAGES
from plone.app.fhirfield.variables import ERROR_PARAM_UNKNOWN
from plone.app.fhirfield.variables import ERROR_PARAM_UNSUPPORTED
from plone.app.fhirfield.variables import ERROR_PARAM_WRONG_DATATYPE
from plone.app.fhirfield.variables import FHIR_ES_MAPPINGS_CACHE
from plone.app.fhirfield.variables import FHIR_FIELD_DEBUG
from plone.app.fhirfield.variables import FHIR_RESOURCE_LIST  # noqa: F401
from plone.app.fhirfield.variables import FHIR_RESOURCE_MODEL_CACHE  # noqa: F401
from plone.app.fhirfield.variables import FHIR_SEARCH_PARAMETER_SEARCHABLE
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
        # Although we are not supporting Multiple Resources Query yet!
        self.resource_types = params.pop('_type', None)

        self.validate()

        self.query_tree = {'and': list()}

    def build(self):
        """
        https://www.elastic.co/guide/en/elasticsearch/reference/2.4/query-dsl-exists-query.html
        https://www.elastic.co/guide/en/elasticsearch/reference/2.3/query-dsl-bool-query.html
        https://www.elastic.co/guide/en/elasticsearch/guide/current/_finding_multiple_exact_values.html
        https://stackoverflow.com/questions/16243496/nested-boolean-queries-in-elastic-search
        """
        for r_field in self.params.keys():
            """ """
            parts = r_field.split(':')
            try:
                field = parts[0]
                modifier = parts[1]
            except IndexError:
                modifier = None

            if modifier in ('missing', 'exists'):
                self.add_exists_query(*parts)
                continue

            # pass
            param_type = FHIR_SEARCH_PARAMETER_SEARCHABLE[field][0]

            if param_type == 'token':
                # xxx: data type have to implement
                # xxx: identify other data type?
                self.add_token_query(field, modifier)

            elif param_type == 'date':
                self.add_date_query(field, modifier)

            elif param_type == 'reference':
                self.add_reference_query(field, modifier)

            elif param_type == 'uri':
                self.add_uri_query(field, modifier)

            elif param_type == 'string':
                self.add_string_query(field, modifier)

            elif param_type == 'quantity':
                self.add_quantity_query(field, modifier)

            elif param_type == 'number':
                self.add_number_query(field, modifier)

        # unofficial but tricky
        query = {'term': {self.field_name + '.resourceType': self.resource_type}}
        # XXX multiple resources?
        self.query_tree['and'].append(query)

        return self.query_tree.copy()

    def add_token_query(self,
                        field,
                        modifier):
        """ """
        if field == 'identifier':
            return self.add_identifier_query(field, modifier)

        raw_path = self.find_path(field)
        # condition like: as(CodeableConcept), is(Range), .where(system='email')
        raw_path, condition = self.normalize_path(raw_path)
        path = self.find_query_path(raw_path=raw_path)

        path_info = fhir_search_path_meta_info(raw_path)

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
            org_field = modifier and ':'.join([field, modifier]) or field
            value = self.params.get(org_field)

            if value in ('true', 'false'):
                if value == 'true':
                    value = True
                else:
                    value = False

            query = dict()
            if path_info[1] is True:
                # check Array type
                query['terms'] = {path: [value]}
            else:
                query['term'] = {path: value}

            if modifier == 'not':
                query = {
                    'query': {'not': query},
                }

            self.query_tree['and'].append(query)

    def add_string_query(self,
                         field,
                         modifier):
        """ """
        # XXX: coming soon
        self.add_token_query(field, modifier)

    def add_number_query(self,
                         field,
                         modifier):
        """ """
        prefix = 'eq'
        org_field = modifier and ':'.join([field, modifier]) or field
        path = self.find_query_path(field=field)
        value = self.params.get(org_field)

        if value[0:2] in FSPR_VALUE_PRIFIXES_MAP:
            prefix = value[0:2]
            value = value[2:]
        if '.' in value:
            value = float(value)
        else:
            value = int(value)

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

        if (prefix != 'ne' and modifier == 'not') or \
                (prefix == 'ne' and modifier != 'not'):
            self.query_tree['and'].append({'query': {'not': q}})
        else:
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
        raw_path = self.find_path(field)
        # condition like: as(CodeableConcept), is(Range), .where(system='email')
        raw_path, condition = self.normalize_path(raw_path)
        path = self.find_query_path(raw_path=raw_path)

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

        if (prefix != 'ne' and modifier == 'not') or \
                (prefix == 'ne' and modifier != 'not'):
            self.query_tree['and'].append({'query': {'not': q}})
        else:
            self.query_tree['and'].append(q)

    def add_quantity_query(self, field, modifier):
        """ """
        raw_path = self.find_path(field)
        # condition like: as(CodeableConcept), is(Range), .where(system='email')
        raw_path, condition = self.normalize_path(raw_path)
        path = self.find_query_path(raw_path=raw_path)

        org_field = modifier and ':'.join([field, modifier]) or field
        value = self.params.get(org_field)
        prefix = 'eq'

        if value[0:2] in FSPR_VALUE_PRIFIXES_MAP:
            prefix = value[0:2]
            value = value[2:]

        matches = list()
        value_parts = value.split('|')
        value = float(value_parts[0])

        value_query = dict()

        if prefix in ('eq', 'ne'):
            value_query['range'] = {
                path: {
                    FSPR_VALUE_PRIFIXES_MAP.get('ge'): value,
                    FSPR_VALUE_PRIFIXES_MAP.get('le'): value,
                },
            }

        elif prefix in ('le', 'lt', 'ge', 'gt'):
            value_query['range'] = {
                path: {
                    FSPR_VALUE_PRIFIXES_MAP.get(prefix): value,
                },
            }

        try:
            if value_parts[1]:
                # some times could be empty
                matches.append({
                    'match': {path + '.system': value_parts[1]},
                })
                matches.append({
                    'match': {path + '.code': value_parts[2]},
                })
            else:
                matches.append({
                    'match': {path + '.unit': value_parts[2]},
                })

        except IndexError:
            pass

        if (prefix != 'ne' and modifier == 'not') or \
                (prefix == 'ne' and modifier != 'not'):
            query = {
                'query': {'bool': {'must_not': [value_query]}},
            }
        else:
            query = {
                'query': {'bool': {'must': [value_query]}},
            }

        if matches:
            if 'must' not in query['query']['bool']:
                query['query']['bool'].update({'must': list()})

            query['query']['bool']['must'].extends(matches)

        self.query_tree['and'].append(query)

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
        raw_path = self.find_path(field)
        path = self.find_query_path(raw_path=raw_path)

        mapping = get_elasticsearch_mapping(self.resource_type)
        mapped_field = path.replace(self.field_name + '.', '').split('.')[0]

        if mapping.get('properties') and \
                mapping['properties'][mapped_field].get('type', None) == 'nested':
            nested = True
        else:
            nested = False

        org_field = ':'.join([field, modifier])
        value = self.params.get(org_field)

        query = dict()
        exists_q = {
            'exists': {'field': path},
        }

        if (modifier == 'missing' and value == 'true') or \
                (modifier == 'exists' and value == 'false'):
            query['bool'] = \
                {
                    'must_not': exists_q,
                }
        elif (modifier == 'missing' and value == 'false') or \
                (modifier == 'exists' and value == 'true'):

            query['exists'] = {'field': path}

        if nested:
            nested_query = {
                    'nested': {
                        'path': path,
                        'query': exists_q,
                    },
                }

            if 'bool' in query:
                query['bool']['must_not'] = nested_query
            else:
                query = {
                    'bool': {
                        'must': nested_query,
                    },
                }

        self.query_tree['and'].append({'query': query})

    def add_uri_query(self, field, modifier):
        """ """
        # XXX: we not sure all could be List of URI???
        raw_path = self.find_path(field)
        path = self.find_query_path(raw_path=raw_path)
        # js_name, is_list, of_many = fhir_search_path_meta_info(path)
        info = fhir_search_path_meta_info(raw_path)

        org_field = modifier and ':'.join([field, modifier]) or field
        value = self.params.get(org_field)
        if info[1] is True:
            # Array
            query = {'terms': {path: [value]}}
        else:
            query = {'term': {path: value}}

        if modifier == 'not':
            query = {
                'query': {'not': query},
            }

        self.query_tree['and'].append(query)

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

        for param, value in self.params.items():

            # Clean escape char in value.
            # https://www.hl7.org/fhir/search.html#escaping
            if value and '\\' in value:
                value = value.replace('\\', '')

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

    @mutually_exclusive_parameters('field', 'raw_path')
    @at_least_one_of('field', 'raw_path')
    def find_query_path(self, field=None, raw_path=None):
        """:param: r_field: resource field"""
        if field:
            raw_path = self.find_path(field)
        if not raw_path:
            return

        if raw_path.startswith('Resource.'):
            return raw_path.replace('Resource', self.field_name)
        else:
            return raw_path.replace(self.resource_type, self.field_name)

    def find_path(self, field):
        """:param: r_field: resource field"""
        if field in FHIR_SEARCH_PARAMETER_SEARCHABLE:
            paths = FHIR_SEARCH_PARAMETER_SEARCHABLE[field][1]

            for path in paths:

                if path.startswith('Resource.'):
                    return path

                if path.startswith(self.resource_type):
                    return path

    def normalize_path(self, path):
        """Seprates if any condition is provided"""
        condition = None

        if '.where(' in path or '.as(' in path or '.is(' in path:
            parts = path.split('.')
            condition = parts[-1]
            path = '.'.join(parts[:-1])

        return path, condition


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
                 field_definitions,
                 sort_fields):
        """ """
        self.field_definitions = field_definitions
        self.sort_fields = sort_fields
        self.validate()

    def build(self, container=None):
        """ """
        container = container or list()
        for resource_type, field in six.iteritems(self.field_definitions):
            for s_field in self.sort_fields:

                cleaned_s_field = s_field.strip()
                sort_order = 'asc'

                if cleaned_s_field.startswith('-'):
                    cleaned_s_field = cleaned_s_field[1:]
                    sort_order = 'desc'

                path_ = self.find_path(cleaned_s_field, field, resource_type)
                container.append(path_ + ':' + sort_order)
        return container

    def validate(self):
        """ """
        errors = list()
        for resource_type, field in six.iteritems(self.field_definitions):
            for s_field in self.sort_fields:

                cleaned_s_field = s_field.strip()
                if cleaned_s_field.startswith('-'):
                    cleaned_s_field = cleaned_s_field[1:]

                if cleaned_s_field not in FHIR_SEARCH_PARAMETER_SEARCHABLE:
                    errors.append(
                        '{0} is unknown as FHIR search sortable field'.
                        format(cleaned_s_field))
                    continue

                if cleaned_s_field in ('_content', '_id', '_lastUpdated',
                                       '_profile', '_query', '_security',
                                       '_tag', '_text'):
                    continue

                supported_paths = \
                    FHIR_SEARCH_PARAMETER_SEARCHABLE[cleaned_s_field][1]

                for path in supported_paths:
                    if path.startswith(resource_type):
                        break
                else:
                    errors.append(
                        '{0} is not available for {1} FHIR Resource'.
                        format(cleaned_s_field, resource_type),
                        )

        if errors:
            raise SearchQueryValidationError(
                'Sort validation: {0}'.
                format(', '.join(errors)))

    def find_path(self, s_field, field, resource_type):
        """:param: s_field: sort field
        :param: field: fhir field
        :param: resource_type
        """
        paths = FHIR_SEARCH_PARAMETER_SEARCHABLE[s_field][1]

        for path in paths:

            if path.startswith('Resource.'):
                return path.replace('Resource', field)

            if path.startswith(resource_type):
                return path.replace(resource_type, field)


def build_elasticsearch_sortable(field_definitions, sort_fields, container=None):
    """ """
    builder = ElasticsearchSortQueryBuilder(field_definitions, sort_fields)

    return builder.build(container)


def get_elasticsearch_mapping(resource, mapping_dir=None, cache=True):
    """Elastic search mapping for FHIR resources"""

    key = resource.lower()
    if mapping_dir is None:
        mapping_dir = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
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
