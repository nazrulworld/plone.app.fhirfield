# -*- coding: utf-8 -*-
# @Date    : 2018-04-30 20:10:43
# @Author  : Md Nazrul Islam (email2nazrul@gmail.com)
# @Link    : http://nazrul.me/
# @Version : $Id$
# All imports here
from App.special_dtml import DTMLFile
from plone.app.fhirfield.helpers import validate_index_name
from plone.app.fhirfield.interfaces import IFhirResourceValue
from Products.PluginIndexes.FieldIndex.FieldIndex import FieldIndex


__author__ = 'Md Nazrul Islam <email2nazrul@gmail.com>'


class FhirFieldIndex(FieldIndex):
    """ """
    meta_type = 'FhirFieldIndex'
    query_options = ('query', 'not')
    manage = manage_main = DTMLFile('dtml/manageFhirFieldIndex', globals())
    manage_main._setName('manage_main')

    def __init__(self, id, ignore_ex=None,
                 call_methods=None, extra=None,
                 caller=None):
        """ """
        self._validate_id(id)

        super(FhirFieldIndex, self).__init__(
                 id, ignore_ex=None,
                 call_methods=None, extra=None,
                 caller=None)

    def _validate_id(self, id_):
        """Validation about the convention which is provided by plone.app.fhirfield
        id_ should contains fhir resource name as prefix"""
        validate_index_name(id_)

    def _get_object_datum(self, obj, attr):
        """ """
        datum = super(FhirFieldIndex, self)._get_object_datum(obj, attr)

        if IFhirResourceValue.providedBy(datum):
            datum = datum.as_json()
        return datum

    def unindex_object(self, documentId):
        """ """
        return super(FhirFieldIndex, self).unindex_object(documentId)

    def index_object(self, documentId, obj, threshold=None):
        """ """
        return super(FhirFieldIndex, self).index_object(documentId, obj, threshold=None)


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


REGISTRABLE_CLASSES = [
    # index, form, action
    (FhirFieldIndex,
        manage_addFhirFieldIndexForm,
        manage_addFhirFieldIndex),
]
