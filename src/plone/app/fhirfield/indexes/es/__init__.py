# -*- coding: utf-8 -*-
# @Date    : 2018-05-19 17:18:14
# @Author  : Md Nazrul Islam (email2nazrul@gmail.com)
# @Link    : http://nazrul.me/
# @Version : $Id$
# All imports here
from .fhir import EsFhirActivityDefinitionIndex
from .fhir import EsFhirAppointmentIndex
from .fhir import EsFhirCarePlanIndex
from .fhir import EsFhirDeviceIndex
from .fhir import EsFhirDeviceRequestIndex
from .fhir import EsFhirFieldIndex
from .fhir import EsFhirHealthcareServiceIndex
from .fhir import EsFhirMedicationAdministrationIndex
from .fhir import EsFhirMedicationDispenseIndex
from .fhir import EsFhirMedicationRequestIndex
from .fhir import EsFhirMedicationStatementIndex
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
from collective.elasticsearch.indexes import INDEX_MAPPING as CIM
from plone.app.fhirfield.indexes.PluginIndexes import FhirActivityDefinitionIndex  # noqa: E501
from plone.app.fhirfield.indexes.PluginIndexes import FhirAppointmentIndex  # noqa: E501
from plone.app.fhirfield.indexes.PluginIndexes import FhirCarePlanIndex  # noqa: E501
from plone.app.fhirfield.indexes.PluginIndexes import FhirDeviceIndex  # noqa: E501
from plone.app.fhirfield.indexes.PluginIndexes import FhirDeviceRequestIndex  # noqa: E501
from plone.app.fhirfield.indexes.PluginIndexes import FhirFieldIndex
from plone.app.fhirfield.indexes.PluginIndexes import FhirHealthcareServiceIndex  # noqa: E501
from plone.app.fhirfield.indexes.PluginIndexes import FhirMedicationAdministrationIndex  # noqa: E501
from plone.app.fhirfield.indexes.PluginIndexes import FhirMedicationDispenseIndex  # noqa: E501
from plone.app.fhirfield.indexes.PluginIndexes import FhirMedicationRequestIndex  # noqa: E501
from plone.app.fhirfield.indexes.PluginIndexes import FhirMedicationStatementIndex  # noqa: E501
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
    FhirAppointmentIndex: EsFhirAppointmentIndex,
    FhirMedicationAdministrationIndex: EsFhirMedicationAdministrationIndex,
    FhirMedicationRequestIndex: EsFhirMedicationRequestIndex,
    FhirMedicationStatementIndex: EsFhirMedicationStatementIndex,
    FhirMedicationDispenseIndex: EsFhirMedicationDispenseIndex,
}

# Tiny patch
CIM.update(INDEX_MAPPING)
