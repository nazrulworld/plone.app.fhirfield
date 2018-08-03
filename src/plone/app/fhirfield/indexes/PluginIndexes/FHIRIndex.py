# -*- coding: utf-8 -*-
# @Date    : 2018-04-30 20:10:43
# @Author  : Md Nazrul Islam (email2nazrul@gmail.com)
# @Link    : http://nazrul.me/
# @Version : $Id$
# All imports here
from App.special_dtml import DTMLFile
from plone.app.fhirfield.helpers import validate_index_name
from plone.app.fhirfield.interfaces import IFhirResourceValue
from Products.PluginIndexes.FieldIndex.FieldIndex import FieldIndex


__author__ = 'Md Nazrul Islam <email2nazrul@gmail.com>'


class FhirFieldIndex(FieldIndex):
    """ """
    meta_type = 'FhirFieldIndex'
    query_options = ('query', 'not')
    manage = manage_main = DTMLFile('dtml/manageFhirFieldIndex', globals())
    manage_main._setName('manage_main')

    def __init__(self, id, ignore_ex=None,
                 call_methods=None, extra=None,
                 caller=None):
        """ """
        self._validate_id(id)

        super(FhirFieldIndex, self).__init__(
                 id, ignore_ex=None,
                 call_methods=None, extra=None,
                 caller=None)

    def _validate_id(self, id_):
        """Validation about the convention which is provided by plone.app.fhirfield
        id_ should contains fhir resource name as prefix"""
        validate_index_name(id_)

    def _get_object_datum(self, obj, attr):
        """ """
        datum = super(FhirFieldIndex, self)._get_object_datum(obj, attr)

        if IFhirResourceValue.providedBy(datum):
            datum = datum.as_json()
        return datum

    def unindex_object(self, documentId):
        """ """
        return super(FhirFieldIndex, self).unindex_object(documentId)

    def index_object(self, documentId, obj, threshold=None):
        """ """
        return super(FhirFieldIndex, self).index_object(documentId, obj, threshold=None)


def manage_addFhirFieldIndex(self,
                             id,
                             extra=None,
                             REQUEST=None,
                             RESPONSE=None,
                             URL3=None):
    """Add a fhir field index"""
    return self.manage_addIndex(id,
                                'FhirFieldIndex',
                                extra=extra,
                                REQUEST=REQUEST,
                                RESPONSE=RESPONSE,
                                URL1=URL3)
manage_addFhirFieldIndexForm = DTMLFile('dtml/addFhirFieldIndexForm', globals())  # noqa: E305


class FhirOrganizationIndex(FhirFieldIndex):
    """ """
    meta_type = 'FhirOrganizationIndex'


def manage_addFhirOrganizationIndex(self,
                                    id,
                                    extra=None,
                                    REQUEST=None,
                                    RESPONSE=None,
                                    URL3=None):
    """Add a fhir field index"""
    return self.manage_addIndex(id,
                                'FhirOrganizationIndex',
                                extra=extra,
                                REQUEST=REQUEST,
                                RESPONSE=RESPONSE,
                                URL1=URL3)
manage_addFhirOrganizationIndexForm = DTMLFile('dtml/addFhirOrganizationIndexForm', globals())  # noqa: E305


class FhirHealthcareServiceIndex(FhirFieldIndex):
    """ """
    meta_type = 'FhirHealthcareServiceIndex'


def manage_addFhirHealthcareServiceIndex(self,
                                         id,
                                         extra=None,
                                         REQUEST=None,
                                         RESPONSE=None,
                                         URL3=None):
    """Add a fhir field index"""
    return self.manage_addIndex(id,
                                'FhirHealthcareServiceIndex',
                                extra=extra,
                                REQUEST=REQUEST,
                                RESPONSE=RESPONSE,
                                URL1=URL3)
manage_addFhirHealthcareServiceIndexForm = DTMLFile('dtml/addFhirHealthcareServiceIndexForm', globals())  # noqa: E305


class FhirPatientIndex(FhirFieldIndex):
    """ """
    meta_type = 'FhirPatientIndex'


def manage_addFhirPatientIndex(self,
                               id,
                               extra=None,
                               REQUEST=None,
                               RESPONSE=None,
                               URL3=None):
    """Add a fhir patient index"""
    return self.manage_addIndex(id,
                                'FhirPatientIndex',
                                extra=extra,
                                REQUEST=REQUEST,
                                RESPONSE=RESPONSE,
                                URL1=URL3)
manage_addFhirPatientIndexForm = DTMLFile('dtml/addFhirPatientIndexForm', globals())  # noqa: E305


class FhirPractitionerIndex(FhirFieldIndex):
    """ """
    meta_type = 'FhirPractitionerIndex'


def manage_addFhirPractitionerIndex(self,
                                    id,
                                    extra=None,
                                    REQUEST=None,
                                    RESPONSE=None,
                                    URL3=None):
    """Add a fhir practitionar index"""
    return self.manage_addIndex(id,
                                'FhirPractitionerIndex',
                                extra=extra,
                                REQUEST=REQUEST,
                                RESPONSE=RESPONSE,
                                URL1=URL3)
manage_addFhirPractitionerIndexForm = DTMLFile('dtml/addFhirPractitionerIndexForm', globals())  # noqa: E305


class FhirRelatedPersonIndex(FhirFieldIndex):
    """ """
    meta_type = 'FhirRelatedPersonIndex'


def manage_addFhirRelatedPersonIndex(self,
                                     id,
                                     extra=None,
                                     REQUEST=None,
                                     RESPONSE=None,
                                     URL3=None):
    """Add a fhir Related Person index"""
    return self.manage_addIndex(id,
                                'FhirRelatedPersonIndex',
                                extra=extra,
                                REQUEST=REQUEST,
                                RESPONSE=RESPONSE,
                                URL1=URL3)
manage_addFhirRelatedPersonIndexForm = DTMLFile('dtml/addFhirRelatedPersonIndexForm', globals())  # noqa: E305


class FhirValueSetIndex(FhirFieldIndex):
    """ """
    meta_type = 'FhirValueSetIndex'


def manage_addFhirValueSetIndex(self,
                                id,
                                extra=None,
                                REQUEST=None,
                                RESPONSE=None,
                                URL3=None):
    """Add a fhir field index"""
    return self.manage_addIndex(id,
                                'FhirValueSetIndex',
                                extra=extra,
                                REQUEST=REQUEST,
                                RESPONSE=RESPONSE,
                                URL1=URL3)
manage_addFhirValueSetIndexForm = DTMLFile('dtml/addFhirValueSetIndexForm', globals())  # noqa: E305


class FhirTaskIndex(FhirFieldIndex):
    """ """
    meta_type = 'FhirTaskIndex'


def manage_addFhirTaskIndex(self,
                            id,
                            extra=None,
                            REQUEST=None,
                            RESPONSE=None,
                            URL3=None):
    """Add a fhir Task index"""
    return self.manage_addIndex(id,
                                'FhirTaskIndex',
                                extra=extra,
                                REQUEST=REQUEST,
                                RESPONSE=RESPONSE,
                                URL1=URL3)
manage_addFhirTaskIndexForm = DTMLFile('dtml/addFhirTaskIndexForm', globals())  # noqa: E305


class FhirQuestionnaireIndex(FhirFieldIndex):
    """ """
    meta_type = 'FhirQuestionnaireIndex'


def manage_addFhirQuestionnaireIndex(self,
                                     id,
                                     extra=None,
                                     REQUEST=None,
                                     RESPONSE=None,
                                     URL3=None):
    """Add a fhir Questionnaire index"""
    return self.manage_addIndex(id,
                                'FhirQuestionnaireIndex',
                                extra=extra,
                                REQUEST=REQUEST,
                                RESPONSE=RESPONSE,
                                URL1=URL3)
manage_addFhirQuestionnaireIndexForm = DTMLFile('dtml/addFhirQuestionnaireIndexForm', globals())  # noqa: E305


class FhirQuestionnaireResponseIndex(FhirFieldIndex):
    """ """
    meta_type = 'FhirQuestionnaireResponseIndex'


def manage_addFhirQuestionnaireResponseIndex(self,
                                             id,
                                             extra=None,
                                             REQUEST=None,
                                             RESPONSE=None,
                                             URL3=None):
    """Add a fhir field index"""
    return self.manage_addIndex(id,
                                'FhirQuestionnaireResponseIndex',
                                extra=extra,
                                REQUEST=REQUEST,
                                RESPONSE=RESPONSE,
                                URL1=URL3)


manage_addFhirQuestionnaireResponseIndexForm = \
    DTMLFile('dtml/addFhirQuestionnaireResponseIndexForm', globals())  # noqa: E305


class FhirActivityDefinitionIndex(FhirFieldIndex):
    """ """
    meta_type = 'FhirActivityDefinitionIndex'


def manage_addFhirActivityDefinitionIndex(self,
                                          id,
                                          extra=None,
                                          REQUEST=None,
                                          RESPONSE=None,
                                          URL3=None):
    """Add a fhir ActivityDefinition index"""
    return self.manage_addIndex(id,
                                'FhirActivityDefinitionIndex',
                                extra=extra,
                                REQUEST=REQUEST,
                                RESPONSE=RESPONSE,
                                URL1=URL3)


manage_addFhirActivityDefinitionIndexForm = \
    DTMLFile('dtml/addFhirActivityDefinitionIndexForm', globals())  # noqa: E305


class FhirObservationIndex(FhirFieldIndex):
    """ """
    meta_type = 'FhirObservationIndex'


def manage_addFhirObservationIndex(self,
                                   id,
                                   extra=None,
                                   REQUEST=None,
                                   RESPONSE=None,
                                   URL3=None):
    """Add a fhir Observation index"""
    return self.manage_addIndex(id,
                                'FhirObservationIndex',
                                extra=extra,
                                REQUEST=REQUEST,
                                RESPONSE=RESPONSE,
                                URL1=URL3)


manage_addFhirObservationIndexForm = \
    DTMLFile('dtml/addFhirObservationIndexForm', globals())  # noqa: E305


class FhirProcedureRequestIndex(FhirFieldIndex):
    """ """
    meta_type = 'FhirProcedureRequestIndex'


def manage_addFhirProcedureRequestIndex(self,
                                        id,
                                        extra=None,
                                        REQUEST=None,
                                        RESPONSE=None,
                                        URL3=None):
    """Add a fhir ProcedureRequest index"""
    return self.manage_addIndex(id,
                                'FhirProcedureRequestIndex',
                                extra=extra,
                                REQUEST=REQUEST,
                                RESPONSE=RESPONSE,
                                URL1=URL3)


manage_addFhirProcedureRequestIndexForm = \
    DTMLFile('dtml/addFhirProcedureRequestIndexForm', globals())  # noqa: E305


class FhirDeviceRequestIndex(FhirFieldIndex):
    """ """
    meta_type = 'FhirDeviceRequestIndex'


def manage_addFhirDeviceRequestIndex(self,
                                     id,
                                     extra=None,
                                     REQUEST=None,
                                     RESPONSE=None,
                                     URL3=None):
    """Add a fhir DeviceRequest index"""
    return self.manage_addIndex(id,
                                'FhirDeviceRequestIndex',
                                extra=extra,
                                REQUEST=REQUEST,
                                RESPONSE=RESPONSE,
                                URL1=URL3)


manage_addFhirDeviceRequestIndexForm = \
    DTMLFile('dtml/addFhirDeviceRequestIndexForm', globals())  # noqa: E305


class FhirDeviceIndex(FhirFieldIndex):
    """ """
    meta_type = 'FhirDeviceIndex'


def manage_addFhirDeviceIndex(self,
                              id,
                              extra=None,
                              REQUEST=None,
                              RESPONSE=None,
                              URL3=None):
    """Add a fhir Device index"""
    return self.manage_addIndex(id,
                                'FhirDeviceIndex',
                                extra=extra,
                                REQUEST=REQUEST,
                                RESPONSE=RESPONSE,
                                URL1=URL3)


manage_addFhirDeviceIndexForm = \
    DTMLFile('dtml/addFhirDeviceIndexForm', globals())  # noqa: E305


class FhirCarePlanIndex(FhirFieldIndex):
    """ """
    meta_type = 'FhirCarePlanIndex'


def manage_addFhirCarePlanIndex(self,
                                id,
                                extra=None,
                                REQUEST=None,
                                RESPONSE=None,
                                URL3=None):
    """Add a fhir CarePlan index"""
    return self.manage_addIndex(id,
                                'FhirCarePlanIndex',
                                extra=extra,
                                REQUEST=REQUEST,
                                RESPONSE=RESPONSE,
                                URL1=URL3)


manage_addFhirCarePlanIndexForm = \
    DTMLFile('dtml/addFhirCarePlanIndexForm', globals())  # noqa: E305


class FhirPlanDefinitionIndex(FhirFieldIndex):
    """ """
    meta_type = 'FhirPlanDefinitionIndex'


def manage_addFhirPlanDefinitionIndex(self,
                                      id,
                                      extra=None,
                                      REQUEST=None,
                                      RESPONSE=None,
                                      URL3=None):
    """Add a fhir PlanDefinition index"""
    return self.manage_addIndex(id,
                                'FhirPlanDefinitionIndex',
                                extra=extra,
                                REQUEST=REQUEST,
                                RESPONSE=RESPONSE,
                                URL1=URL3)


manage_addFhirPlanDefinitionIndexForm = \
    DTMLFile('dtml/addFhirPlanDefinitionIndexForm', globals())  # noqa: E305


REGISTRABLE_CLASSES = [
    # index, form, action
    (FhirFieldIndex,
        manage_addFhirFieldIndexForm,
        manage_addFhirFieldIndex),
    (FhirOrganizationIndex,
        manage_addFhirOrganizationIndexForm,
        manage_addFhirOrganizationIndex),
    (FhirHealthcareServiceIndex,
        manage_addFhirHealthcareServiceIndexForm,
        manage_addFhirHealthcareServiceIndex),
    (FhirPatientIndex,
        manage_addFhirPatientIndexForm,
        manage_addFhirPatientIndex),
    (FhirPractitionerIndex,
        manage_addFhirPractitionerIndexForm,
        manage_addFhirPractitionerIndex),
    (FhirQuestionnaireIndex,
        manage_addFhirQuestionnaireIndexForm,
        manage_addFhirQuestionnaireIndex),
    (FhirQuestionnaireResponseIndex,
        manage_addFhirQuestionnaireResponseIndexForm,
        manage_addFhirQuestionnaireResponseIndex),
    (FhirTaskIndex,
        manage_addFhirTaskIndexForm,
        manage_addFhirTaskIndex),
    (FhirValueSetIndex,
        manage_addFhirValueSetIndexForm,
        manage_addFhirValueSetIndex),
    (FhirRelatedPersonIndex,
        manage_addFhirRelatedPersonIndexForm,
        manage_addFhirRelatedPersonIndex),
    (FhirActivityDefinitionIndex,
        manage_addFhirActivityDefinitionIndexForm,
        manage_addFhirActivityDefinitionIndex),
    (FhirObservationIndex,
        manage_addFhirObservationIndexForm,
        manage_addFhirObservationIndex),
    (FhirProcedureRequestIndex,
        manage_addFhirProcedureRequestIndexForm,
        manage_addFhirProcedureRequestIndex),
    (FhirDeviceRequestIndex,
        manage_addFhirDeviceRequestIndexForm,
        manage_addFhirDeviceRequestIndex),
    (FhirDeviceIndex,
        manage_addFhirDeviceIndexForm,
        manage_addFhirDeviceIndex),
    (FhirCarePlanIndex,
        manage_addFhirCarePlanIndexForm,
        manage_addFhirCarePlanIndex),
    (FhirPlanDefinitionIndex,
        manage_addFhirPlanDefinitionIndexForm,
        manage_addFhirPlanDefinitionIndex),
]
