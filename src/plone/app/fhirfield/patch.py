# _*_ coding: utf-8 _*_

__author__ = 'Md Nazrul Islam <email2nazrul@gmail.com>'


def monkey_patch_fhir_base_model():
    """" """
    from zope.interface import implementer
    import fhirclient.models.resource
    from plone.app.fhirfield.interfaces import IFhirResourceModel
    # We forcely implement IFhirResourceModel
    fhirclient.models.resource.Resource = \
        implementer(IFhirResourceModel)(fhirclient.models.resource.Resource)


def fix_resource_registry_import_error():
    """Should be removed when drop support for plone4 """
    import Products.CMFPlone.interfaces
    try:
        Products.CMFPlone.interfaces.IResourceRegistry
    except AttributeError:
        from zope import schema
        from zope.interface import Interface

        class IResourceRegistry(Interface):
            """ """

            js = schema.ASCIILine(
                title=u'Main js file',
                required=False)

            css = schema.List(
                title=u'CSS/LESS files',
                value_type=schema.ASCIILine(title=u'URL'),
                default=[],
                required=False)

            deps = schema.ASCIILine(
                title=u'Dependencies for shim',
                description=u'Comma separated values of resource for shim',
                required=False)
        # Make fall back for plone 4
        setattr(
            Products.CMFPlone.interfaces,
            'IResourceRegistry',
            IResourceRegistry)
