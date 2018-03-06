# _*_ coding: utf-8 _*_
from plone.app.fhirfield import FhirResource
from plone.dexterity.content import Container
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
