# -*- coding: utf-8 -*-
"""Module where all interfaces, events and exceptions live."""
from fhirspec import FHIR_RELEASES
from plone.app.fhirfield.compat import _
from plone.schema import JSONField
from zope import schema as zs
from zope.schema.interfaces import IField


class IFhirResource(IField):
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
    gzip_compression = zs.Bool(title=_("Enable GZip compression"), default=False)

    def from_dict(dict_value):
        """ """

    def from_none():
        """Make FhirResourceValue isntance without FHIR data """
