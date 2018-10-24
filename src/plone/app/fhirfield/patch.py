# _*_ coding: utf-8 _*_

__author__ = 'Md Nazrul Islam <email2nazrul@gmail.com>'


def monkey_patch_fhir_base_model():
    """" """
    from zope.interface import implementer
    import fhirclient.models.resource
    from plone.app.fhirfield.interfaces import IFhirResourceModel
    # We forcely implement IFhirResourceModel
    fhirclient.models.resource.Resource = implementer(IFhirResourceModel)(fhirclient.models.resource.Resource)


def fix_resource_registry_import_error():
    """Should be removed when drop support for plone4 """
    import Products.CMFPlone.interfaces
    try:
        Products.CMFPlone.interfaces.IResourceRegistry
    except AttributeError:
        from zope.interface import Interface

        class IResourceRegistry(Interface):
            """ """
        # Make fall back for plone 4
        setattr(
            Products.CMFPlone.interfaces,
            'IResourceRegistry',
            IResourceRegistry)
