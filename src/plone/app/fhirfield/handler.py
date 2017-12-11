# -*- coding: utf-8 -*-
from plone.app.fhirfield.field import FhirResource
from plone.app.fhirfield.interfaces import IFhirResource
from plone.supermodel.exportimport import BaseHandler
from plone.supermodel.interfaces import IToUnicode
from zope.component import adapter
from zope.interface import implementer

import six


__author__ = 'Md Nazrul Islam <email2nazrul@gmail.com>'


class FhirResourceHandler_(BaseHandler):
    """Special handling for the FhirResourceField field, to deal with 'default'
    that may be unicode.
    """

    # Don't read or write 'schema'
    filteredAttributes = BaseHandler.filteredAttributes.copy()
    filteredAttributes.update({'schema': 'rw'})

    def __init__(self, klass):
        super(FhirResourceHandler_, self).__init__(klass)


@implementer(IToUnicode)
@adapter(IFhirResource)
class FhirResourceToUnicode(object):

    def __init__(self, context):
        self.context = context

    def toUnicode(self, value):
        return six.text_type(value.stringify())


FhirResourceHandler = FhirResourceHandler_(FhirResource)
