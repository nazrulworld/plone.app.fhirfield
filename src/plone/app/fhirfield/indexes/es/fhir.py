# -*- coding: utf-8 -*-
# @Date    : 2018-04-29 17:09:46
# @Author  : Md Nazrul Islam <email2nazrul@gmail.com>
# @Link    : http://nazrul.me/
# @Version : $Id$
# All imports here
from .helpers import build_elasticsearch_query
from .helpers import get_elasticsearch_mapping
from collective.elasticsearch import logger
from collective.elasticsearch.indexes import BaseIndex
from Missing import MV
from plone.app.fhirfield.helpers import validate_index_name
from plone.app.fhirfield.interfaces import IFhirResourceValue
from plone.app.fhirfield.variables import FHIR_RESOURCE_LIST

import warnings


__author__ = 'Md Nazrul Islam <email2nazrul@gmail.com>'


class EsFhirFieldIndex(BaseIndex):
    """ """
    filter_query = True

    def validate_name(self, name):
        """"About validation of index/field name convention """

        validate_index_name(name)

    def create_mapping(self, name):
        """Minimal mapping for all kind of fhir models"""
        self.validate_name(name)

        key = name.split('_')[0]

        try:
            return get_elasticsearch_mapping(key)
        except LookupError:
            warnings.warn(
                'No mapping found for `{0}`, instead minimal '
                'mapping has been used.'.format(name),
                UserWarning)
        # Return the base/basic mapping
        return get_elasticsearch_mapping('Resource')

    def get_value(self, object):
        """ """
        value = None
        attrs = self.index.getIndexSourceNames()
        if len(attrs) > 0:
            attr = attrs[0]
        else:
            attr = ''

        if getattr(self.index, 'index_object', None):
            value = self.index._get_object_datum(object, attr, es_datum=True)
        else:
            logger.info(
                'catalogObject was passed bad index '
                'object {0!s}.'.format(self.index),
            )
        if value == MV:
            return None

        if IFhirResourceValue.providedBy(value):
            value = value.as_json()

        return value

    def get_query(self, name, value):
        """Only prepared fhir query is acceptable
        other query is building here"""
        self.validate_name(name)

        value = self._normalize_query(value)
        if value in (None, ''):
            return

        if value.get('query'):
            query = {'and': value.get('query')}
            # need query validation???
            return query

        params = None

        if value.get('params'):
            params = value.get('params')

        resource_type = value.pop(
            'resource_type',
            FHIR_RESOURCE_LIST[name.split('_')[0].lower()]['name'])
        if params is None:
            params = value

        query = build_elasticsearch_query(
            params,
            field_name=name,
            resource_type=resource_type)

        return query
