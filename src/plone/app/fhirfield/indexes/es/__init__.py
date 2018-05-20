# -*- coding: utf-8 -*-
# @Date    : 2018-05-19 17:18:14
# @Author  : Md Nazrul Islam (email2nazrul@gmail.com)
# @Link    : http://nazrul.me/
# @Version : $Id$
# All imports here
from .fhir import EsFhirFieldIndex
from .fhir import EsFhirOrganizationIndex
from .fhir import EsFhirPatientIndex
from .fhir import EsFhirPractitionerIndex
from .fhir import EsFhirValueSetIndex
from collective.elasticsearch.indexes import INDEX_MAPPING as CIM
from plone.app.fhirfield.indexes.PluginIndexes import FhirFieldIndex
from plone.app.fhirfield.indexes.PluginIndexes import FhirOrganizationIndex
from plone.app.fhirfield.indexes.PluginIndexes import FhirPatientIndex
from plone.app.fhirfield.indexes.PluginIndexes import FhirPractitionerIndex
from plone.app.fhirfield.indexes.PluginIndexes import FhirValueSetIndex


__author__ = 'Md Nazrul Islam (email2nazrul@gmail.com)'

INDEX_MAPPING = {
    FhirFieldIndex: EsFhirFieldIndex,
    FhirOrganizationIndex: EsFhirOrganizationIndex,
    FhirPatientIndex: EsFhirPatientIndex,
    FhirPractitionerIndex: EsFhirPractitionerIndex,
    FhirValueSetIndex: EsFhirValueSetIndex,
}

# Tiny patch
CIM.update(INDEX_MAPPING)
