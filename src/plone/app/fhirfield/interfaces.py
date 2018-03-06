# -*- coding: utf-8 -*-
"""Module where all interfaces, events and exceptions live."""
from plone.app.fhirfield.compat import _
from zope import schema as zs
from zope.interface import Attribute
from zope.interface import Interface
from zope.schema.interfaces import IObject


class IFhirResourceModel(Interface):
    """ """
    resource_type = Attribute(
        'resource_type',
        _('Resource Type'),
    )
    id = Attribute(
        'id',
        _('Logical id of this artifact.'),
    )
    implicitRules = Attribute(
        'implicitRules',
        _('A set of rules under which this content was created.'),
    )
    language = Attribute(
        'language',
        _('Language of the resource content.'),
    )
    meta = Attribute(
        'meta',
        _('Metadata about the resource'),
    )

    def as_json():
        """ """


class IFhirResource(IObject):
    """ """
    resource_type = zs.TextLine(
        title=_('FHIR Resource Type'),
        required=False,
    )
    model = zs.DottedName(
        title=_('FHIR Resource Model from fhirclient'),
        required=False,
    )
    model_interface = zs.DottedName(
        title=_('FHIR Model Interface'),
        required=False,
    )

    def from_dict(dict_value):
        """ """
    def from_none():
        """Make FhirResourceValue isntance without FHIR data """


class IFhirResourceValue(Interface):
    """ """
    _encoding = Attribute(
        '_encoding',
        _('Encoding name that will be used during json generation'),
    )
    _storage = Attribute(
        '_storage',
        _('_storage to hold Fhir resource model object.'),
    )

    def stringify(prettify=False):
        """Transformation to JSON string representation"""

    def patch(patch_data):
        """FHIR Patch implementation: https://www.hl7.org/fhir/fhirpatch.html"""

    def foreground_origin():
        """Return the original object of FHIR model that is proxied!"""
