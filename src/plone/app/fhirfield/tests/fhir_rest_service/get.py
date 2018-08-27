# -*- coding: utf-8 -*-
from plone.restapi.services import Service
from zope.interface import implementer
from zope.publisher.interfaces import IPublishTraverse


@implementer(IPublishTraverse)
class FHIRSearchService(Service):
    """ """
    def __init__(self, context, request):
        """ """
        super(FHIRSearchService, self).__init__(context, request)
        self.params = []

    def reply(self):
        """ """
        params = self.request.forms.copy()
        params['resource_type'] = self.resource_type

    def publishTraverse(self, request, name):  # noqa: N802
        # Consume any path segments after /@fhir as parameters
        self.params.append(name)
        return self

    @property
    def resource_type(self):
        """ """

        if 0 < len(self.params):
            _rt = self.params[0]
            return _rt
        return None
