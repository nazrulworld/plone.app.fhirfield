# _*_ coding: utf-8 _*_
from plone.app.fhirfield import FhirResource
from plone.dexterity.content import Container
from plone.dexterity.content import Item
from plone.supermodel import model
from zope.interface import implementer


__author__ = 'Md Nazrul Islam<email2nazrul@gmail.com>'


class ITestOrganization(model.Schema):
    """ """
    resource = FhirResource(
        title=u'Fhir Resource Field',
        model='fhirclient.models.organization.Organization',
    )


@implementer(ITestOrganization)
class TestOrganization(Container):
    """ """


class IFFTestOrganization(model.Schema):
    """ """
    organization_resource = FhirResource(
        title=u'Fhir Organization Field',
        model='fhirclient.models.organization.Organization',
    )


@implementer(IFFTestOrganization)
class FFTestOrganization(Container):
    """ """


class IFFTestPatient(model.Schema):
    """ """
    patient_resource = FhirResource(
        title=u'Fhir Patient Field',
        model='fhirclient.models.patient.Patient',
    )


@implementer(IFFTestPatient)
class FFTestPatient(Container):
    """ """


class IFFTestQuestionnaire(model.Schema):
    """ """
    questionnaire_resource = FhirResource(
        title=u'Fhir Questionnaire Field',
        model='fhirclient.models.questionnaire.Questionnaire',
    )


@implementer(IFFTestQuestionnaire)
class FFTestQuestionnaire(Container):
    """ """


class IFFTestQuestionnaireResponse(model.Schema):
    """ """
    questionnaireresponse_resource = FhirResource(
        title=u'Fhir QuestionnaireResponse Field',
        model='fhirclient.models.questionnaireresponse.QuestionnaireResponse',
    )


@implementer(IFFTestQuestionnaireResponse)
class FFTestQuestionnaireResponse(Container):
    """ """


class IFFTestTask(model.Schema):
    """ """
    task_resource = FhirResource(
        title=u'Fhir Task Field',
        model='fhirclient.models.task.Task',
    )


@implementer(IFFTestTask)
class FFTestTask(Container):
    """ """


class IFFTestProcedureRequest(model.Schema):
    """ """
    procedurerequest_resource = FhirResource(
        title=u'Fhir ProcedureRequest Field',
        model='fhirclient.models.procedurerequest.ProcedureRequest',
    )


@implementer(IFFTestProcedureRequest)
class FFTestProcedureRequest(Item):
    """ """


class IFFTestDevice(model.Schema):
    """ """
    device_resource = FhirResource(
        title=u'Fhir Device Field',
        model='fhirclient.models.device.Device',
    )


@implementer(IFFTestDevice)
class FFTestDevice(Item):
    """ """


class IFFTestDeviceRequest(model.Schema):
    """ """
    task_resource = FhirResource(
        title=u'Fhir DeviceRequest Field',
        model='fhirclient.models.devicerequest.DeviceRequest',
    )


@implementer(IFFTestDeviceRequest)
class FFTestDeviceRequest(Item):
    """ """


class IFFTestValueSet(model.Schema):
    """ """
    valueset_resource = FhirResource(
        title=u'Fhir ValueSet Field',
        model='fhirclient.models.valueset.ValueSet',
    )


@implementer(IFFTestValueSet)
class FFTestValueSet(Item):
    """ """
