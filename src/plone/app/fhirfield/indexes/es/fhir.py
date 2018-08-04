# -*- coding: utf-8 -*-
# @Date    : 2018-04-29 17:09:46
# @Author  : Md Nazrul Islam <email2nazrul@gmail.com>
# @Link    : http://nazrul.me/
# @Version : $Id$
# All imports here
from collective.elasticsearch.indexes import BaseIndex
from plone.app.fhirfield.helpers import build_elasticsearch_query
from plone.app.fhirfield.helpers import FHIR_RESOURCE_LIST
from plone.app.fhirfield.helpers import make_fhir_elasticsearch_list
from plone.app.fhirfield.helpers import validate_index_name
from plone.app.fhirfield.interfaces import IFhirResourceValue

import os
import warnings


__author__ = 'Md Nazrul Islam <email2nazrul@gmail.com>'

MAPPING_FILE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                'mapping')
FHIR_ES_MAPPINGS = make_fhir_elasticsearch_list(MAPPING_FILE_DIR)

DEPRICATION_MSG = """Use `{0}` CatalogIndex has been deprecated, use `FhirFieldIndex` instead
as this class will be removed to next release.
"""


class EsFhirFieldIndex(BaseIndex):
    """ """
    _mapping_cache = None
    filter_query = True

    def validate_name(self, name):
        """"About validation of index/field name convention """

        validate_index_name(name)

    def create_mapping(self, name):
        """Minimal mapping for all kind of fhir models"""
        self.validate_name(name)

        key = name.split('_')[0]

        try:
            return FHIR_ES_MAPPINGS[key]['mapping']
        except KeyError:
            warnings.warn(
                'No mapping found for `{0}`, instead minimal '
                'mapping has been used.'.format(name),
                UserWarning)

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


class EsFhirOrganizationIndex(EsFhirFieldIndex):
    """ """

    def create_mapping(self, name):
        """"""
        warnings.warn(
            DEPRICATION_MSG.format(self.__class__.__name__),
            UserWarning)
        return EsFhirFieldIndex.create_mapping(self, name)


class EsFhirPatientIndex(EsFhirFieldIndex):
    """ """

    def create_mapping(self, name):
        """"""
        warnings.warn(
            DEPRICATION_MSG.format(self.__class__.__name__),
            UserWarning)
        return EsFhirFieldIndex.create_mapping(self, name)


class EsFhirPractitionerIndex(EsFhirFieldIndex):
    """ """

    def create_mapping(self, name):
        """"""
        warnings.warn(
            DEPRICATION_MSG.format(self.__class__.__name__),
            UserWarning)
        return EsFhirFieldIndex.create_mapping(self, name)


class EsFhirRelatedPersonIndex(EsFhirFieldIndex):
    """ """

    def create_mapping(self, name):
        """"""
        warnings.warn(
            DEPRICATION_MSG.format(self.__class__.__name__),
            UserWarning)
        return EsFhirFieldIndex.create_mapping(self, name)


class EsFhirValueSetIndex(EsFhirFieldIndex):
    """ """

    def create_mapping(self, name):
        """"""
        warnings.warn(
            DEPRICATION_MSG.format(self.__class__.__name__),
            UserWarning)
        return EsFhirFieldIndex.create_mapping(self, name)


class EsFhirTaskIndex(EsFhirFieldIndex):
    """ """

    def create_mapping(self, name):
        """"""
        warnings.warn(
            DEPRICATION_MSG.format(self.__class__.__name__),
            UserWarning)
        return EsFhirFieldIndex.create_mapping(self, name)


class EsFhirQuestionnaireIndex(EsFhirFieldIndex):
    """ """

    def create_mapping(self, name):
        """"""
        warnings.warn(
            DEPRICATION_MSG.format(self.__class__.__name__),
            UserWarning)
        return EsFhirFieldIndex.create_mapping(self, name)


class EsFhirQuestionnaireResponseIndex(EsFhirFieldIndex):
    """ """

    def create_mapping(self, name):
        """"""
        warnings.warn(
            DEPRICATION_MSG.format(self.__class__.__name__),
            UserWarning)
        return EsFhirFieldIndex.create_mapping(self, name)


class EsFhirActivityDefinitionIndex(EsFhirFieldIndex):
    """ """

    def create_mapping(self, name):
        """"""
        warnings.warn(
            DEPRICATION_MSG.format(self.__class__.__name__),
            UserWarning)
        return EsFhirFieldIndex.create_mapping(self, name)


class EsFhirHealthcareServiceIndex(EsFhirFieldIndex):
    """ """

    def create_mapping(self, name):
        """"""
        warnings.warn(
            DEPRICATION_MSG.format(self.__class__.__name__),
            UserWarning)
        return EsFhirFieldIndex.create_mapping(self, name)


class EsFhirObservationIndex(EsFhirFieldIndex):
    """ """

    def create_mapping(self, name):
        """"""
        warnings.warn(
            DEPRICATION_MSG.format(self.__class__.__name__),
            UserWarning)
        return EsFhirFieldIndex.create_mapping(self, name)


class EsFhirProcedureRequestIndex(EsFhirFieldIndex):
    """ """

    def create_mapping(self, name):
        """"""
        warnings.warn(
            DEPRICATION_MSG.format(self.__class__.__name__),
            UserWarning)
        return EsFhirFieldIndex.create_mapping(self, name)


class EsFhirDeviceIndex(EsFhirFieldIndex):
    """ """

    def create_mapping(self, name):
        """"""
        warnings.warn(
            DEPRICATION_MSG.format(self.__class__.__name__),
            UserWarning)
        return EsFhirFieldIndex.create_mapping(self, name)


class EsFhirDeviceRequestIndex(EsFhirFieldIndex):
    """ """

    def create_mapping(self, name):
        """"""
        warnings.warn(
            DEPRICATION_MSG.format(self.__class__.__name__),
            UserWarning)
        return EsFhirFieldIndex.create_mapping(self, name)


class EsFhirCarePlanIndex(EsFhirFieldIndex):
    """ """

    def create_mapping(self, name):
        """"""
        warnings.warn(
            DEPRICATION_MSG.format(self.__class__.__name__),
            UserWarning)
        return EsFhirFieldIndex.create_mapping(self, name)


class EsFhirPlanDefinitionIndex(EsFhirFieldIndex):
    """ """

    def create_mapping(self, name):
        """"""
        warnings.warn(
            DEPRICATION_MSG.format(self.__class__.__name__),
            UserWarning)
        return EsFhirFieldIndex.create_mapping(self, name)
