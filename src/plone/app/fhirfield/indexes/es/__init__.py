# -*- coding: utf-8 -*-
# @Date    : 2018-05-19 17:18:14
# @Author  : Md Nazrul Islam (email2nazrul@gmail.com)
# @Link    : http://nazrul.me/
# @Version : $Id$
# All imports here
from .fhir import EsFhirActivityDefinitionIndex
from .fhir import EsFhirCarePlanIndex
from .fhir import EsFhirDeviceIndex
from .fhir import EsFhirDeviceRequestIndex
from .fhir import EsFhirFieldIndex
from .fhir import EsFhirHealthcareServiceIndex
from .fhir import EsFhirObservationIndex
from .fhir import EsFhirOrganizationIndex
from .fhir import EsFhirPatientIndex
from .fhir import EsFhirPlanDefinitionIndex
from .fhir import EsFhirPractitionerIndex
from .fhir import EsFhirProcedureRequestIndex
from .fhir import EsFhirQuestionnaireIndex
from .fhir import EsFhirQuestionnaireResponseIndex
from .fhir import EsFhirRelatedPersonIndex
from .fhir import EsFhirTaskIndex
from .fhir import EsFhirValueSetIndex
from .helpers import build_elasticsearch_sortable
from collective.elasticsearch.indexes import INDEX_MAPPING as CIM
from collective.elasticsearch.query import QueryAssembler
from plone.app.fhirfield.indexes.PluginIndexes import FhirActivityDefinitionIndex  # noqa: E501
from plone.app.fhirfield.indexes.PluginIndexes import FhirCarePlanIndex  # noqa: E501
from plone.app.fhirfield.indexes.PluginIndexes import FhirDeviceIndex  # noqa: E501
from plone.app.fhirfield.indexes.PluginIndexes import FhirDeviceRequestIndex  # noqa: E501
from plone.app.fhirfield.indexes.PluginIndexes import FhirFieldIndex
from plone.app.fhirfield.indexes.PluginIndexes import FhirHealthcareServiceIndex  # noqa: E501
from plone.app.fhirfield.indexes.PluginIndexes import FhirObservationIndex
from plone.app.fhirfield.indexes.PluginIndexes import FhirOrganizationIndex
from plone.app.fhirfield.indexes.PluginIndexes import FhirPatientIndex
from plone.app.fhirfield.indexes.PluginIndexes import FhirPlanDefinitionIndex  # noqa: E501
from plone.app.fhirfield.indexes.PluginIndexes import FhirPractitionerIndex
from plone.app.fhirfield.indexes.PluginIndexes import FhirProcedureRequestIndex
from plone.app.fhirfield.indexes.PluginIndexes import FhirQuestionnaireIndex
from plone.app.fhirfield.indexes.PluginIndexes import FhirQuestionnaireResponseIndex  # noqa: E501
from plone.app.fhirfield.indexes.PluginIndexes import FhirRelatedPersonIndex
from plone.app.fhirfield.indexes.PluginIndexes import FhirTaskIndex
from plone.app.fhirfield.indexes.PluginIndexes import FhirValueSetIndex
from plone.app.fhirfield.variables import FHIR_RESOURCE_LIST  # noqa: F401


__author__ = 'Md Nazrul Islam (email2nazrul@gmail.com)'

INDEX_MAPPING = {
    FhirFieldIndex: EsFhirFieldIndex,
    FhirOrganizationIndex: EsFhirOrganizationIndex,
    FhirPatientIndex: EsFhirPatientIndex,
    FhirPractitionerIndex: EsFhirPractitionerIndex,
    FhirRelatedPersonIndex: EsFhirRelatedPersonIndex,
    FhirValueSetIndex: EsFhirValueSetIndex,
    FhirTaskIndex: EsFhirTaskIndex,
    FhirQuestionnaireIndex: EsFhirQuestionnaireIndex,
    FhirQuestionnaireResponseIndex: EsFhirQuestionnaireResponseIndex,
    FhirActivityDefinitionIndex: EsFhirActivityDefinitionIndex,
    FhirObservationIndex: EsFhirObservationIndex,
    FhirHealthcareServiceIndex: EsFhirHealthcareServiceIndex,
    FhirProcedureRequestIndex: EsFhirProcedureRequestIndex,
    FhirDeviceIndex: EsFhirDeviceIndex,
    FhirDeviceRequestIndex: EsFhirDeviceRequestIndex,
    FhirCarePlanIndex: EsFhirCarePlanIndex,
    FhirPlanDefinitionIndex: EsFhirPlanDefinitionIndex,
}

# Tiny patch
CIM.update(INDEX_MAPPING)


def QueryAssembler_normalize(self, query):
    """ """
    if 'b_size' in query:
        del query['b_size']
    if 'b_start' in query:
        del query['b_start']
    if 'sort_limit' in query:
        del query['sort_limit']

    sort_on = ['_score']
    resources = dict()

    for param in query.keys():
        if param in ('_sort', '_count', 'sort_on', 'sort_order'):
            continue

        try:
            definition = FHIR_RESOURCE_LIST[param.split('_')[0].lower()]
            resources[definition.get('name')] = param
        except KeyError:
            continue

    if resources:
        # we don't care about Plone sorting, if FHIR query is used
        if 'sort_on' in query:
            del query['sort_on']
        if 'sort_order' in query:
            del query['sort_order']

        sort = query.pop('_sort', '').strip()
        if sort:
            build_elasticsearch_sortable(resources, sort.split(','), sort_on)
            sortstr = ','.join(sort_on)
        else:
            sortstr = ''
    else:
        # _sort is useless if FHIR query (using fhir field) is not used
        if '_sort' in query:
            del query['_sort']

        sort = query.pop('sort_on', None)
        if sort:
            sort_on.extend(sort.split(','))
        sort_order = query.pop('sort_order', 'descending')
        if sort_on:
            sortstr = ','.join(sort_on)
            if sort_order in ('descending', 'reverse', 'desc'):
                sortstr += ':desc'
            else:
                sortstr += ':asc'
        else:
            sortstr = ''

    return query, sortstr

# *** Monkey Patch ***


setattr(QueryAssembler, '_old_normalize', QueryAssembler.normalize)
setattr(QueryAssembler, 'normalize', QueryAssembler_normalize)
