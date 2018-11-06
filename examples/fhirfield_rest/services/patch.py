# -*- coding: utf-8 -*-
from plone import api
from plone.restapi.deserializer import json_body
from plone.restapi.services import Service
from plone.restapi.services.locking.locking import is_locked
from zope.interface import alsoProvides
from zope.interface import implementer
from zope.publisher.interfaces import IPublishTraverse

import plone.protect.interfaces


@implementer(IPublishTraverse)
class FHIRResourcePatch(Service):
    """Patch a FHIR Resource object.
    """
    def __init__(self, context, request):
        """ """
        super(FHIRResourcePatch, self).__init__(context, request)
        self.params = []

    def publishTraverse(self, request, name):  # noqa: N802
        # Consume any path segments after /@fhir as parameters
        self.params.append(name)
        return self

    @property
    def resource_id(self):
        """ """
        if 1 < len(self.params):
            return self.params[1]
        return None

    @property
    def resource_type(self):
        """ """

        if 0 < len(self.params):
            _rt = self.params[0]
            return _rt
        return None

    def reply(self):
        """ """
        query = {
            '{0}_resource'.format(
                self.resource_type.lower()
                ): {'_id': self.resource_id}
            }
        brains = api.content.find(**query)

        if len(brains) == 0:
            self.request.response.setStatus(404)
            return None

        obj = brains[0].getObject()

        if is_locked(obj, self.request):
                self.request.response.setStatus(403)
                return dict(error=dict(
                    type='Forbidden', message='Resource is locked.'))

        data = json_body(self.request)

        # Disable CSRF protection
        if 'IDisableCSRFProtection' in dir(plone.protect.interfaces):
            alsoProvides(self.request,
                         plone.protect.interfaces.IDisableCSRFProtection)

        fhir_value = getattr(
            obj,
            '{0}_resource'.format(self.resource_type.lower()))
        fhir_value.patch(data['patch'])

        self.request.response.setStatus(204)
        # Return None
        return None
