# _*_ coding: utf-8 _*_
from plone.app.fhirfield import _
from plone.app.fhirfield.field import FhirResourceField
from plone.schemaeditor.fields import FieldFactory


__author__ = 'Md Nazrul Islam<email2nazrul@gmail.com>'


FhirResourceFieldFactory = FieldFactory(FhirResourceField, _(u'FHIR Resource Field'))
