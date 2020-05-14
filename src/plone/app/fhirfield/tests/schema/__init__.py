# _*_ coding: utf-8 _*_
from plone.app.fhirfield import FhirResource
from plone.dexterity.content import Container
from plone.dexterity.content import Item
from plone.supermodel import model
from zope.interface import implementer


__author__ = "Md Nazrul Islam<email2nazrul@gmail.com>"


class IFFOrganization(model.Schema):
    """ """

    organization_resource = FhirResource(
        title=u"Fhir Organization Field",
        model="fhir.resources.STU3.organization.Organization",
        fhir_release="STU3",
    )


@implementer(IFFOrganization)
class FFOrganization(Container):
    """ """


class IFFPatient(model.Schema):
    """ """

    patient_resource = FhirResource(
        title=u"Fhir Patient Field",
        model="fhir.resources.STU3.patient.Patient",
        fhir_release="STU3",
    )


@implementer(IFFPatient)
class FFPatient(Container):
    """ """


class IFFPractitioner(model.Schema):
    """ """

    practitioner_resource = FhirResource(
        title=u"Fhir Practitioner Field",
        model="fhir.resources.STU3.practitioner.Practitioner",
        fhir_release="STU3",
    )


@implementer(IFFPractitioner)
class FFPractitioner(Container):
    """ """


class IFFQuestionnaire(model.Schema):
    """ """

    questionnaire_resource = FhirResource(
        title=u"Fhir Questionnaire Field",
        model="fhir.resources.STU3.questionnaire.Questionnaire",
        fhir_release="STU3",
    )


@implementer(IFFQuestionnaire)
class FFQuestionnaire(Container):
    """ """


class IFFQuestionnaireResponse(model.Schema):
    """ """

    questionnaireresponse_resource = FhirResource(
        title=u"Fhir QuestionnaireResponse Field",
        model="fhir.resources.STU3.questionnaireresponse.QuestionnaireResponse",
        fhir_release="STU3",
    )


@implementer(IFFQuestionnaireResponse)
class FFQuestionnaireResponse(Container):
    """ """


class IFFTask(model.Schema):
    """ """

    task_resource = FhirResource(
        title=u"Fhir Task Field",
        model="fhir.resources.STU3.task.Task",
        fhir_release="STU3",
    )


@implementer(IFFTask)
class FFTask(Container):
    """ """


class IFFProcedureRequest(model.Schema):
    """ """

    procedurerequest_resource = FhirResource(
        title=u"Fhir ProcedureRequest Field",
        model="fhir.resources.STU3.procedurerequest.ProcedureRequest",
        fhir_release="STU3",
    )


@implementer(IFFProcedureRequest)
class FFProcedureRequest(Item):
    """ """


class IFFDevice(model.Schema):
    """ """

    device_resource = FhirResource(
        title=u"Fhir Device Field", resource_type="Device", fhir_release="STU3"
    )


@implementer(IFFDevice)
class FFDevice(Item):
    """ """


class IFFDeviceRequest(model.Schema):
    """ """

    devicerequest_resource = FhirResource(
        title=u"Fhir DeviceRequest Field",
        resource_type="DeviceRequest",
        fhir_release="STU3",
    )


@implementer(IFFDeviceRequest)
class FFDeviceRequest(Item):
    """ """


class IFFValueSet(model.Schema):
    """ """

    valueset_resource = FhirResource(
        title=u"Fhir ValueSet Field", resource_type="ValueSet", fhir_release="STU3"
    )


@implementer(IFFValueSet)
class FFValueSet(Item):
    """ """


class IFFChargeItem(model.Schema):
    """"""

    chargeitem_resource = FhirResource(
        title=u"Fhir ChargeItem Field", resource_type="ChargeItem", fhir_release="STU3"
    )


@implementer(IFFChargeItem)
class FFChargeItem(Item):
    """ """


class IFFEncounter(model.Schema):
    """"""

    encounter_resource = FhirResource(
        title=u"Fhir FFEncounter Field", resource_type="Encounter", fhir_release="STU3"
    )


@implementer(IFFEncounter)
class FFEncounter(Item):
    """ """


class IFFMedicationRequest(model.Schema):
    """"""

    medicationrequest_resource = FhirResource(
        title=u"Fhir MedicationRequest Field",
        resource_type="MedicationRequest",
        fhir_release="STU3",
    )


@implementer(IFFMedicationRequest)
class FFMedicationRequest(Item):
    """ """


class IFFObservation(model.Schema):
    """"""

    observation_resource = FhirResource(
        title=u"Fhir Observation Field",
        resource_type="Observation",
        fhir_release="STU3",
    )


@implementer(IFFObservation)
class FFObservation(Item):
    """ """


class IFFMedia(model.Schema):
    """"""

    media_resource = FhirResource(
        title=u"Fhir Media Field", resource_type="Media", fhir_release="STU3"
    )


@implementer(IFFMedia)
class FFMedia(Item):
    """ """
