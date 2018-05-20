# -*- coding: utf-8 -*-
# @Date    : 2018-04-30 20:10:43
# @Author  : Md Nazrul Islam (email2nazrul@gmail.com)
# @Link    : http://nazrul.me/
# @Version : $Id$
# All imports here
from App.special_dtml import DTMLFile
from Products.PluginIndexes.FieldIndex.FieldIndex import FieldIndex


__author__ = 'Md Nazrul Islam <email2nazrul@gmail.com>'


class FhirFieldIndex(FieldIndex):
    """ """
    meta_type = 'FhirFieldIndex'
    query_options = ('query', 'range', 'not')
    manage = manage_main = DTMLFile('dtml/manageFhirFieldIndex', globals())
    manage_main._setName('manage_main')


def manage_addFhirFieldIndex(self,
                             id,
                             extra=None,
                             REQUEST=None,
                             RESPONSE=None,
                             URL3=None):
    """Add a fhir field index"""
    return self.manage_addIndex(id,
                                'FhirFieldIndex',
                                extra=extra,
                                REQUEST=REQUEST,
                                RESPONSE=RESPONSE,
                                URL1=URL3)
manage_addFhirFieldIndexForm = DTMLFile('dtml/addFhirFieldIndexForm', globals())  # noqa: E305


class FhirOrganizationIndex(FhirFieldIndex):
    """ """
    meta_type = 'FhirOrganizationIndex'


def manage_addFhirOrganizationIndex(self,
                                    id,
                                    extra=None,
                                    REQUEST=None,
                                    RESPONSE=None,
                                    URL3=None):
    """Add a fhir field index"""
    return self.manage_addIndex(id,
                                'FhirOrganizationIndex',
                                extra=extra,
                                REQUEST=REQUEST,
                                RESPONSE=RESPONSE,
                                URL1=URL3)
manage_addFhirOrganizationIndexForm = DTMLFile('dtml/addFhirOrganizationIndexForm', globals())  # noqa: E305


class FhirPatientIndex(FhirFieldIndex):
    """ """
    meta_type = 'FhirPatientIndex'


def manage_addFhirPatientIndex(self,
                               id,
                               extra=None,
                               REQUEST=None,
                               RESPONSE=None,
                               URL3=None):
    """Add a fhir patient index"""
    return self.manage_addIndex(id,
                                'FhirPatientIndex',
                                extra=extra,
                                REQUEST=REQUEST,
                                RESPONSE=RESPONSE,
                                URL1=URL3)
manage_addFhirPatientIndexForm = DTMLFile('dtml/addFhirPatientIndexForm', globals())  # noqa: E305


class FhirPractitionerIndex(FhirFieldIndex):
    """ """
    meta_type = 'FhirPractitionerIndex'


def manage_addFhirPractitionerIndex(self,
                                    id,
                                    extra=None,
                                    REQUEST=None,
                                    RESPONSE=None,
                                    URL3=None):
    """Add a fhir practitionar index"""
    return self.manage_addIndex(id,
                                'FhirPractitionerIndex',
                                extra=extra,
                                REQUEST=REQUEST,
                                RESPONSE=RESPONSE,
                                URL1=URL3)
manage_addFhirPractitionerIndexForm = DTMLFile('dtml/addFhirPractitionerIndexForm', globals())  # noqa: E305


class FhirValueSetIndex(FhirFieldIndex):
    """ """
    meta_type = 'FhirValueSetIndex'


def manage_addFhirValueSetIndex(self,
                                id,
                                extra=None,
                                REQUEST=None,
                                RESPONSE=None,
                                URL3=None):
    """Add a fhir field index"""
    return self.manage_addIndex(id,
                                'FhirValueSetIndex',
                                extra=extra,
                                REQUEST=REQUEST,
                                RESPONSE=RESPONSE,
                                URL1=URL3)
manage_addFhirValueSetIndexForm = DTMLFile('dtml/addFhirValueSetIndexForm', globals())  # noqa: E305