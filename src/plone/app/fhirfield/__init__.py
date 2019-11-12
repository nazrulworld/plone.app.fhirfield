# -*- coding: utf-8 -*-
""" """
from plone.app.fhirfield import patch  # noqa: I001

from .exc import SearchQueryError  # noqa: I001,F401
from .field import FhirResource  # noqa: I001,F401
from .widget import FhirResourceWidget  # noqa: I001,F401


patch.monkey_patch_fhir_base_model()  # noqa: I003


__author__ = "Md Nazrul Islam<email2nazrul@gmail.com>"


def initialize(context):
    """ """
    import pkg_resources

    import logging

    log = logging.getLogger("plone.app.fhirfield")

    try:
        pkg_resources.get_distribution("collective.fhirpath")
        log.info("No need to install, as collective.fhirpath is doing that.")
        return
    except pkg_resources.DistributionNotFound:
        pass
    # Registering Pluggable indexes for FHIR
    from plone.app.fhirfield.indexes.PluginIndexes import REGISTRABLE_CLASSES

    for index, form, action in REGISTRABLE_CLASSES:

        context.registerClass(
            index,
            permission="Add Pluggable Index",
            constructors=(form, action),
            icon="indexes/PluginIndexes/index.gif",
            visibility=None,
        )
        log.info("`{0}`  pluggable index has been registered".format(index.__name__))
