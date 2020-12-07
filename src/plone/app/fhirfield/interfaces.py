# -*- coding: utf-8 -*-
"""Module where all interfaces, events and exceptions live."""
from fhirspec import FHIR_RELEASES
from plone.app.fhirfield.compat import _
from plone.schema import JSONField
from zope import schema as zs
from zope.interface import Attribute
from zope.interface import Interface
from zope.schema.interfaces import IObject


class IFhirResource(IObject):
    """ """

    resource_type = zs.TextLine(title=_("FHIR Resource Type"), required=False)
    model = zs.DottedName(
        title=_("FHIR Resource Model from fhirclient"), required=False
    )
    fhir_release = zs.Choice(
        title="FHIR Version(Release)",
        values=[r.value for r in FHIR_RELEASES],
        required=True,
    )
    index_mapping = JSONField(title=_("Index Mapping"), required=False)

    def from_dict(dict_value):
        """FhirResourceValue from dict data"""

    def from_resource_model(model_obj):
        """FhirResourceValue from  fhir.resources"""

    def from_none():
        """Make FhirResourceValue isntance without FHIR data """


class IFhirResourceValue(Interface):
    """ """

    _encoding = Attribute(
        "_encoding", _("Encoding name that will be used during json generation")
    )
    _storage = Attribute("_storage", _("_storage to hold Fhir resource model object."))

    def stringify(prettify=False):
        """Transformation to JSON string representation"""

    def patch(patch_data):
        """FHIR Patch implementation: https://www.hl7.org/fhir/fhirpatch.html"""

    def foreground_origin():
        """Return the original object of FHIR model that is proxied!"""
