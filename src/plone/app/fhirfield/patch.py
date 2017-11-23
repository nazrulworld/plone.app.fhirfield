# _*_ coding: utf-8 _*_

__author__ = 'Md Nazrul Islam <email2nazrul@gmail.com>'


def monkey_patch_fhir_base_model():
    """" """
    from zope.interfaces import implementer
    import fhirclient.model.resource
    from plone.app.fhirfield.interfaces import IFhirResourceModel
    # We forcely implement IFhirResourceModel
    fhirclient.model.resource.Resource = implementer(IFhirResourceModel)(fhirclient.model.resource.Resource)
