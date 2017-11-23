# _*_ coding: utf-8 _*_
from plone.app.fhirfield import _
from plone.app.fhirfield import field
from plone.app.fhirfield import interfaces
from plone.schemaeditor.fields import FieldFactory


__author__ = 'Md Nazrul Islam<email2nazrul@gmail.com>'


class IFhirResource(interfaces.IFhirResource):
    """ """

FhirResourceFieldFactory = FieldFactory(field.FhirResource, _(u'FHIR Resource Field'))
