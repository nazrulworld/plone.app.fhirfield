# -*- coding: utf-8 -*-
# @Date    : 2018-04-29 17:09:46
# @Author  : Md Nazrul Islam <email2nazrul@gmail.com>
# @Link    : http://nazrul.me/
# @Version : $Id$
# All imports here
from collective.elasticsearch.indexes import BaseIndex


__author__ = 'Md Nazrul Islam <email2nazrul@gmail.com>'


class EsFhirFieldIndex(BaseIndex):
    """ """
    def create_mapping(self, name):
        return {
            'properties': {
                'name': {
                    'type': 'string',
                    'index': 'analyzed',
                    'analyzer': 'keyword',
                    'store': False
                },
                'resourceType': {
                    'type': 'string',
                    'store': False
                },
                'id': {
                    'type': 'string',
                    'store': True
                },
                'identifier': {
                    'type': 'nested',
                    'properties': {
                        'use': {
                            'type': 'string'
                        },
                        'system': {
                            'type': 'string'
                        },
                        'value': {
                            'type': 'string'
                        }
                    }
                }
            }
        }


class EsFhirOrganizationIndex(EsFhirFieldIndex):
    """ """


class EsFhirPatientIndex(EsFhirFieldIndex):
    """ """


class EsFhirPractitionerIndex(EsFhirFieldIndex):
    """ """


class EsFhirValueSetIndex(EsFhirFieldIndex):
    """ """
