# -*- coding: utf-8 -*-
from plone import api
from plone.app.fhirfield.helpers import parse_query_string
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
        results = [getattr(
            r.getObject(),
            '{0}_resource'.format(self.resource_type)).as_json()
            for r in self.build_result()]

        if self.resource_id:
            if not results:
                self.request.response.setStatus(404)
                return None
            return results[0]

        return results

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

    def _get_fhir_fieldname(self, resource_type=None):
        """We assume FHIR Field name is ``{resource type}_resource``"""
        resource_type = resource_type or self.resource_type

        return '{0}_resource'.format(resource_type.lower())

    def get_params(self):
        """We are not using self.request.form (parsed by Zope Publisher)!!
        There is special meaning for colon(:) in key field. For example `field_name:list`
        treats data as List and it doesn't recognize FHIR search modifier like :not, :missing
        as a result, from colon(:) all chars are ommited.
        """
        if self.resource_id:
            return {'_id': self.resource_id}

        return parse_query_string(self.request)

    def build_query(self):
        """ """
        query = dict()

        fhir_query = self.get_params()
        extra_params = dict()
        # not supporting count yet!
        if '_count' in fhir_query:
            extra_params['_count'] = fhir_query.pop('_count')

        if 'search-offset' in fhir_query:
            extra_params['search-offset'] = fhir_query.pop('search-offset')

        if 'search-id' in fhir_query:
            extra_params['search-id'] = fhir_query.pop('search-id')

        if fhir_query:
            query[self._get_fhir_fieldname(self.resource_type)] = \
                fhir_query

        return query, extra_params

    def build_result(self):
        """ """
        query, extra_params = self.build_query()
        results = api.content.find(**query)  # noqa: P001
        if not results:
            return 0, []

        return results
