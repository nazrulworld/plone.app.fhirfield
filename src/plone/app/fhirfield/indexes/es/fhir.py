# -*- coding: utf-8 -*-
# @Date    : 2018-04-29 17:09:46
# @Author  : Md Nazrul Islam <email2nazrul@gmail.com>
# @Link    : http://nazrul.me/
# @Version : $Id$
# All imports here
from collective.elasticsearch.indexes import BaseIndex
from plone.app.fhirfield.compat import json
from plone.app.fhirfield.interfaces import IFhirResourceValue

import os


__author__ = 'Md Nazrul Islam <email2nazrul@gmail.com>'

MAPPING_FILE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                'mapping')


class EsFhirFieldIndex(BaseIndex):
    """ """
    _mapping_cache = None
    filter_query = False

    def create_mapping(self, name):
        """Minimal mapping for all kind of fhir models"""
        return {
            'properties': {
                'id': {
                    'type': 'string',
                    'store': True,
                },
                'identifier': {
                    'type': 'nested',
                    'properties': {
                        'use': {
                            'type': 'string',
                        },
                        'system': {
                            'type': 'string',
                        },
                        'value': {
                            'type': 'string',
                        },
                    },
                },
                'resourceType': {
                    'type': 'string',
                    'store': False,
                },
                'meta': {
                    'properties': {
                        'versionId': {
                            'type': 'string',
                            'store': False,
                        },
                        'lastUpdated': {
                            'type': 'date',
                            'store': False,
                        },
                    },
                },
            },
        }

    def get_value(self, object):
        """ """
        value = super(EsFhirFieldIndex, self).get_value(object)
        if IFhirResourceValue.providedBy(value):
            # should be sim value based on mapping?
            value = value.as_json()

        return value

    def get_query(self, name, value):
        value = self._normalize_query(value)
        if value in (None, ''):
            return
        query = {
            'bool': {
                'should': []
            }
        }
        should_container = query['bool']['should']
        should_container.append(value)
        return query

    def add_prefix(self, prefix, items):
        """Add field name as prefix """
        container = list()
        pass


class EsFhirOrganizationIndex(EsFhirFieldIndex):
    """ """

    def create_mapping(self, name):
        """Minimal mapping for all kind of fhir models"""
        print name
        return self._get_mapping()

    def _get_mapping(self, cache=True):
        """Fetch mapping from file system associated with resourceType"""
        if not cache or self._mapping_cache is None:
            with open(os.path.join(MAPPING_FILE_DIR, 'Organization.json'), 'r') as f:
                contents = json.load(f)
                # ??? do some validation ???
                self._mapping_cache = contents['mapping']

        return self._mapping_cache


class EsFhirPatientIndex(EsFhirFieldIndex):
    """ """


class EsFhirPractitionerIndex(EsFhirFieldIndex):
    """ """


class EsFhirValueSetIndex(EsFhirFieldIndex):
    """ """
