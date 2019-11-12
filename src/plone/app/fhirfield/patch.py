# _*_ coding: utf-8 _*_
from fhirpath.enums import FHIR_VERSION


__author__ = "Md Nazrul Islam <email2nazrul@gmail.com>"


def monkey_patch_fhir_base_model():
    """" """
    from zope.interface import implementer
    import importlib
    from plone.app.fhirfield.interfaces import IFhirResourceModel

    releases = set(
        [
            member.value
            for member in FHIR_VERSION
            if member.value != FHIR_VERSION.DEFAULT.value
        ]
    )
    # We forcely implement IFhirResourceModel
    _resource = importlib.import_module("fhir.resources.resource")
    _resource.Resource = implementer(IFhirResourceModel)(_resource.Resource)

    for rel in releases:
        _resource = importlib.import_module("fhir.resources.{0}.resource".format(rel))
        _resource.Resource = implementer(IFhirResourceModel)(_resource.Resource)
