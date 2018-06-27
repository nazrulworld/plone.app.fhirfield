# -*- coding: utf-8 -*-
# @Date    : 2018-04-29 17:09:46
# @Author  : Md Nazrul Islam <email2nazrul@gmail.com>
# @Link    : http://nazrul.me/
# @Version : $Id$
# All imports here
from collective.elasticsearch.indexes import BaseIndex
from plone.app.fhirfield.compat import json
from plone.app.fhirfield.helpers import build_elasticsearch_query
from plone.app.fhirfield.interfaces import IFhirResourceValue

import os


__author__ = 'Md Nazrul Islam <email2nazrul@gmail.com>'

MAPPING_FILE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                'mapping')


class EsFhirFieldIndex(BaseIndex):
    """ """
    _mapping_cache = None
    _resource_type = 'Resource'
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
                            'format': 'date_time_no_millis||date_optional_time',
                            'store': False,
                        },
                        'profile': {
                            'type': 'string',
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
        """Only prepared fhir query is acceptable
        other query is building here"""
        value = self._normalize_query(value)
        if value in (None, ''):
            return

        if value.get('query'):
            query = {
                'bool': value.get('query'),
            }
            # need query validation???
            return query

        params = None

        if value.get('params'):
            params = value.get('params')

        resource_type = value.pop('resource_type', self._resource_type)
        if params is None:
            params = value

        query = build_elasticsearch_query(params,
                                          field_name=name,
                                          resource_type=resource_type)

        return {'bool': query}


class EsFhirOrganizationIndex(EsFhirFieldIndex):
    """ """
    _resource_type = 'Organization'

    def create_mapping(self, name):
        """Minimal mapping for all kind of fhir models"""
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
    _resource_type = 'Patient'


class EsFhirPractitionerIndex(EsFhirFieldIndex):
    """ """
    _resource_type = 'Practitioner'


class EsFhirRelatedPersonIndex(EsFhirFieldIndex):
    """ """
    _resource_type = 'RelatedPerson'


class EsFhirValueSetIndex(EsFhirFieldIndex):
    """ """
    _resource_type = 'ValueSet'


class EsFhirTaskIndex(EsFhirFieldIndex):
    """ """
    _resource_type = 'Task'


class EsFhirQuestionnaireIndex(EsFhirFieldIndex):
    """ """
    _resource_type = 'Questionnaire'


class EsFhirQuestionnaireResponseIndex(EsFhirFieldIndex):
    """ """
    _resource_type = 'QuestionnaireResponse'


class EsFhirActivityDefinitionIndex(EsFhirFieldIndex):
    """ """
    _resource_type = 'ActivityDefinition'


class EsFhirHealthcareServiceIndex(EsFhirFieldIndex):
    """ """
    _resource_type = 'HealthcareService'


class EsFhirObservationIndex(EsFhirFieldIndex):
    """ """
    _resource_type = 'Observation'


class EsFhirProcedureRequestIndex(EsFhirFieldIndex):
    """ """
    _resource_type = 'ProcedureRequest'


class EsFhirDeviceIndex(EsFhirFieldIndex):
    """ """
    _resource_type = 'Device'


class EsFhirDeviceRequestIndex(EsFhirFieldIndex):
    """ """
    _resource_type = 'DeviceRequest'
