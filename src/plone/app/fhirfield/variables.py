# -*- coding: utf-8 -*-
# @Date    : 2018-08-09 10:07:41
# @Author  : Md Nazrul Islam <email2nazrul@gmail.com>
# @Link    : http://nazrul.me/
# @Version : $Id$
# All imports here
from collections import defaultdict

import json
import logging
import os


__author__ = 'Md Nazrul Islam <email2nazrul@gmail.com>'

LOGGER = logging.getLogger('plone.app.fhirfield')
FHIR_VERSION = 'STU3'
FHIR_FIELD_DEBUG = os.environ.get('FHIR_FIELD_DEBUG', '').lower() in \
    ('y', 'yes', 't', 'true', '1')
ERROR_PARAM_UNKNOWN = 'EP001'
ERROR_PARAM_UNSUPPORTED = 'EP002'
ERROR_PARAM_WRONG_DATATYPE = 'EP003'

ERROR_MESSAGES = {
    ERROR_PARAM_UNKNOWN: 'Parameter is unrecognized by FHIR search.',
    ERROR_PARAM_UNSUPPORTED: 'Parameter is not supported for this resource type',
    ERROR_PARAM_WRONG_DATATYPE: 'The value\'s data type is not excepted',
}

FHIR_RESOURCE_MODEL_CACHE = defaultdict()

FHIR_STATIC_DIR = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    'browser',
    'static',
    'FHIR')

FHIR_RESOURCE_LIST_DIR = os.path.join(FHIR_STATIC_DIR, 'HL7', 'ResourceList')

with open(os.path.join(FHIR_STATIC_DIR, 'HL7',
                       'search',
                       'FHIR-Search-Parameter-Registry.json')) as f:

    FHIR_SEARCH_PARAMETER_REGISTRY = json.load(f)['object']

with open(os.path.join(FHIR_STATIC_DIR, 'HL7',
                       'search',
                       'FHIR-Search-Parameter-Registry-searchable.json')) as f:

    FHIR_SEARCH_PARAMETER_SEARCHABLE = json.load(f)['searchable']
    FHIR_SEARCH_PARAMETER_SEARCHABLE_KEYS = \
        FHIR_SEARCH_PARAMETER_SEARCHABLE.keys()

FSPR_KEYS_BY_GROUP = dict()

for group, rows in FHIR_SEARCH_PARAMETER_REGISTRY.items():
    FSPR_KEYS_BY_GROUP[group] = list()
    for row in rows[1:]:
        FSPR_KEYS_BY_GROUP[group].append(row[0])

FSPR_VALUE_PRIFIXES_MAP = {
    'eq': None,
    'ne': None,
    'gt': 'gt',
    'lt': 'lt',
    'ge': 'gte',
    'le': 'lte',
    'sa': None,
    'eb': None,
    'ap': None}

SEARCH_PARAM_MODIFIERS = (
    'missing',
    'exists',
    'exact',
    'not',
    'text',
    'in',
    'below',
    'above',
    'not-in')

with open(
    os.path.join(FHIR_RESOURCE_LIST_DIR, FHIR_VERSION + '.json'),
        'r') as f:
    """ """
    FHIR_RESOURCE_LIST = json.load(f)['resources']


FHIR_ES_MAPPINGS_CACHE = dict()
