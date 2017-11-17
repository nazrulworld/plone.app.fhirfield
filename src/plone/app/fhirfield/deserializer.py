# _*_ coding: utf-8 _*_
from plone.app.fhirfield.interfaces import IFhirResourceField
from plone.dexterity.interfaces import IDexterityContent
from plone.restapi.deserializer.dxfields import DefaultFieldDeserializer
from plone.restapi.interfaces import IFieldDeserializer
from zope.component import adapter
from zope.interface import implementer
from zope.publisher.interfaces.browser import IBrowserRequest

import six


__author__ = 'Md Nazrul Islam <email2nazrul@gmail.com>'


@implementer(IFieldDeserializer)
@adapter(IFhirResourceField, IDexterityContent, IBrowserRequest)
class FhirResourceFieldDeserializer(DefaultFieldDeserializer):

    def __call__(self, value):
        """ """
        if isinstance(value, six):
            return IFhirResourceField(self.field).fromUnicode(value)
        elif isinstance(value, dict):
            return IFhirResourceField(self.field).from_dict(value)
        else:
            raise ValueError(
                'Invalid data type({0}) provided! only dict or string data type is accepted.'.format(type(value))
            )
