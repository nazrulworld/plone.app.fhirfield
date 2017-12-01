# -*- coding: utf-8 -*-
"""Module where all interfaces, events and exceptions live."""
from plone.app.fhirfield.compat import _
from zope.interface import Attribute
from zope.interface import Interface
from zope.schema.interfaces import IObject


class IFhirResourceModel(Interface):
    """ """
    resource_type = Attribute(
        'resource_type',
        _('Resource Type')
    )


class IFhirResource(IObject):
    """ """
    model = Attribute('model', _('FHIR Resource Model from fhirclient'))
    resource_type = Attribute('resource_type', _('FHIR Resource Type'))

    def from_dict(dict_value):
        pass


class IFhirResourceValue(Interface):
    """ """
    def stringify():
        pass

    def json_patch(patch):
        pass

    def foreground_origin():
        """Return the original object of FHIR model that is proxied!"""
        pass
