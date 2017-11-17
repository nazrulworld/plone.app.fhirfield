# -*- coding: utf-8 -*-
"""Module where all interfaces, events and exceptions live."""
from plone.app.fhirfield import _
from zope.interface import Attribute
from zope.interface import Interface
from zope.schema.interfaces import IFromUnicode
from zope.schema.interfaces import IObject


class IFhirResource(Interface):
    """ """
    resource_type = Attribute(
        'resource_type',
        _('Resource Type')
    )


class IFhirResourceField(IObject):
    """ """
    model = Attribute('model', _('FHIR Resource Model from fhirclient'))
    resource_type = Attribute('resource_type', _('FHIR Resource Type'))

    def from_dict(dict_value):
        pass


class IFhirResourceFieldEdit(IFhirResourceField, IFromUnicode):
    """ """


class IFhirResourceValue(Interface):
    """ """
    def stringify():
        pass

    def json_patch(patch):
        pass
