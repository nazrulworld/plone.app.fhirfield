# -*- coding: utf-8 -*-
""" """
from plone.app.fhirfield import patch  # noqa: I001
patch.monkey_patch_fhir_base_model()  # noqa: I003

from .field import FhirResource  # noqa: I001,F401
from .widget import FhirResourceWidget  # noqa: I001,F401

__author__ = 'Md Nazrul Islam<email2nazrul@gmail.com>'


def initialize(context):
    """ """
    import logging

    log = logging.getLogger('plone.app.fhirfield')

    # Registering Pluggable indexes for FHIR
    from plone.app.fhirfield.indexes.PluginIndexes import FHIRIndex

    context.registerClass(FHIRIndex.FhirFieldIndex,
                          permission='Add Pluggable Index',
                          constructors=(FHIRIndex.manage_addFhirFieldIndexForm,
                                        FHIRIndex.manage_addFhirFieldIndex),
                          icon='indexes/PluginIndexes/index.gif',
                          visibility=None)
    log.info('`FhirFieldIndex`  pluggable index has been registered')

    context.registerClass(FHIRIndex.FhirOrganizationIndex,
                          permission='Add Pluggable Index',
                          constructors=(FHIRIndex.manage_addFhirOrganizationIndexForm,
                                        FHIRIndex.manage_addFhirOrganizationIndex),
                          icon='indexes/PluginIndexes/index.gif',
                          visibility=None)

    log.info('`FhirOrganizationIndex` pluggable index has been registered')

    context.registerClass(FHIRIndex.FhirPatientIndex,
                          permission='Add Pluggable Index',
                          constructors=(FHIRIndex.manage_addFhirPatientIndexForm,
                                        FHIRIndex.manage_addFhirPatientIndex),
                          icon='indexes/PluginIndexes/index.gif',
                          visibility=None)

    log.info('`FhirPatientIndex` pluggable index has been registered')

    context.registerClass(FHIRIndex.FhirPractitionerIndex,
                          permission='Add Pluggable Index',
                          constructors=(FHIRIndex.manage_addFhirPractitionerIndexForm,
                                        FHIRIndex.manage_addFhirPractitionerIndex),
                          icon='indexes/PluginIndexes/index.gif',
                          visibility=None)
    log.info('`FhirPractitionerIndex` pluggable index has been registered')

    context.registerClass(FHIRIndex.FhirValueSetIndex,
                          permission='Add Pluggable Index',
                          constructors=(FHIRIndex.manage_addFhirValueSetIndexForm,
                                        FHIRIndex.manage_addFhirValueSetIndex),
                          icon='indexes/PluginIndexes/index.gif',
                          visibility=None)
    log.info('`FhirValueSetIndex` pluggable index has been registered')
