# _*_ coding: utf-8 _*_
from plone.app.fhirfield.interfaces import IFhirResource
from plone.dexterity.interfaces import IDexterityContent
from plone.restapi.deserializer.dxfields import DefaultFieldDeserializer
from plone.restapi.interfaces import IFieldDeserializer
from zope.component import adapter
from zope.interface import implementer
from zope.publisher.interfaces.browser import IBrowserRequest

import six


__author__ = 'Md Nazrul Islam <email2nazrul@gmail.com>'


@implementer(IFieldDeserializer)
@adapter(IFhirResource, IDexterityContent, IBrowserRequest)
class FhirResourceDeserializer(DefaultFieldDeserializer):

    def __call__(self, value):
        """ """
        if isinstance(value, six.string_types):
            return IFhirResource(self.field).fromUnicode(value)
        elif isinstance(value, dict):
            return IFhirResource(self.field).from_dict(value)
        else:
            raise ValueError(
                'Invalid data type({0}) provided! only dict or string data type is accepted.'.format(type(value)),
            )
