# _*_ coding: utf-8 _*_
from plone.app.fhirfield.interfaces import IFhirResource
from plone.dexterity.interfaces import IDexterityContent
from plone.restapi.interfaces import IFieldSerializer
from plone.restapi.serializer.dxfields import DefaultFieldSerializer
from zope.component import adapter
from zope.interface import implementer
from zope.interface import Interface


__author__ = 'Md Nazrul Islam<email2nazrul@gmail.com>'


@adapter(IFhirResource, IDexterityContent, Interface)
@implementer(IFieldSerializer)
class FhirResourceSerializer(DefaultFieldSerializer):

    def __init__(self, field, context, request):
        self.context = context
        self.request = request
        self.field = field

    def __call__(self):
        """value type: FhirResourceValue"""
        fhir_value = self.get_value()
        if fhir_value:
            value = fhir_value.as_json()
        else:
            value = None
        return value
