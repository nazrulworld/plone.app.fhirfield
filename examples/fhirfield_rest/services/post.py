# -*- coding: utf-8 -*-
from Acquisition import aq_base
from Acquisition.interfaces import IAcquirer
from plone.restapi.deserializer import json_body
from plone.restapi.exceptions import DeserializationError
from plone.restapi.interfaces import IDeserializeFromJson
from plone.restapi.services import Service
from plone.restapi.services.content.utils import add as add_obj
from plone.restapi.services.content.utils import create as create_obj
from Products.Archetypes.interfaces import IBaseObject
from Products.CMFPlone.utils import safe_hasattr
from zope.component import queryMultiAdapter
from zope.event import notify
from zope.interface import alsoProvides
from zope.interface import implementer
from zope.lifecycleevent import ObjectCreatedEvent
from zope.publisher.interfaces import IPublishTraverse

import json
import plone.protect.interfaces


__author__ = 'Md Nazrul Islam <nazrul@zitelab.dk>'


@implementer(IPublishTraverse)
class FHIRResourceAdd(Service):
    """Creates a new FHIR Resource object.
    """
    def __init__(self, context, request):
        """ """
        super(FHIRResourceAdd, self).__init__(context, request)
        self.params = []

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

    def reply(self):
        """ """
        data = json_body(self.request)

        # Disable CSRF protection
        if 'IDisableCSRFProtection' in dir(plone.protect.interfaces):
            alsoProvides(self.request,
                         plone.protect.interfaces.IDisableCSRFProtection)

        response = self._create_object(data)
        return response

    def _create_object(self, fhir):
        """ """
        form_data = {
            '@type': 'FF' + fhir['resourceType'],
            'id': fhir['id'],
            'title': '{0}-{1}'.format(
                self.resource_type,
                fhir['id'])
        }
        fhir_field_name = '{0}_resource'.format(
            fhir['resourceType'].lower())
        form_data[fhir_field_name] = fhir

        self.request['BODY'] = json.dumps(form_data)

        context = self.get_container(fhir)

        obj = create_obj(
            context,
            form_data['@type'],
            id_=form_data['id'],
            title=form_data['title'])

        if isinstance(obj, dict) and 'error' in obj:
            self.request.response.setStatus(400)
            return obj

        # Acquisition wrap temporarily to satisfy things like vocabularies
        # depending on tools
        temporarily_wrapped = False
        if IAcquirer.providedBy(obj) and not safe_hasattr(obj, 'aq_base'):
            obj = obj.__of__(context)
            temporarily_wrapped = True

        # Update fields
        deserializer = queryMultiAdapter(
            (obj, self.request),
            IDeserializeFromJson
        )
        if deserializer is None:
            self.request.response.setStatus(501)
            return dict(error=dict(
                message='Cannot deserialize type {0}'.format(obj.portal_type)))

        try:
            deserializer(validate_all=True)
        except DeserializationError as e:
            self.request.response.setStatus(400)
            return dict(error=dict(type='DeserializationError', message=str(e)))

        if temporarily_wrapped:
            obj = aq_base(obj)

        if not IBaseObject.providedBy(obj):
            notify(ObjectCreatedEvent(obj))

        # Adding to Container
        add_obj(context, obj, rename=False)

        self.request.response.setStatus(201)
        response = getattr(obj, fhir_field_name).as_json()

        self.request.response.setHeader(
            'Location',
            '/'.join([self.context.portal_url(),
                     '@fhir',
                      response['resourceType'],
                      response['id']]))

        return response
