# -*- coding: utf-8 -*-
# @Date    : 2018-05-19 17:18:14
# @Author  : Md Nazrul Islam (email2nazrul@gmail.com)
# @Link    : http://nazrul.me/
# @Version : $Id$
# All imports here
from .fhir import EsFhirFieldIndex
from .helpers import build_elasticsearch_sortable
from collective.elasticsearch.indexes import INDEX_MAPPING as CIM
from collective.elasticsearch.mapping import MappingAdapter
from collective.elasticsearch.query import QueryAssembler
from plone.app.fhirfield.indexes.PluginIndexes import FhirFieldIndex
from plone.app.fhirfield.variables import FHIR_RESOURCE_LIST  # noqa: F401
from plone.registry.interfaces import IRegistry
from zope.component import getUtility

import warnings


__author__ = 'Md Nazrul Islam (email2nazrul@gmail.com)'

INDEX_MAPPING = {
    FhirFieldIndex: EsFhirFieldIndex,
}

# Tiny patch
CIM.update(INDEX_MAPPING)


def QueryAssembler_normalize(self, query):
    """ """
    if 'b_size' in query:
        del query['b_size']
    if 'b_start' in query:
        del query['b_start']
    if 'sort_limit' in query:
        del query['sort_limit']

    sort_on = ['_score']
    resources = dict()

    for param in query.keys():
        if param in ('_sort', '_count', 'sort_on', 'sort_order'):
            continue

        try:
            definition = FHIR_RESOURCE_LIST[param.split('_')[0].lower()]
            resources[definition.get('name')] = param
        except KeyError:
            continue

    if resources:
        # we don't care about Plone sorting, if FHIR query is used
        if 'sort_on' in query:
            del query['sort_on']
        if 'sort_order' in query:
            del query['sort_order']

        sort = query.pop('_sort', '').strip()
        if sort:
            build_elasticsearch_sortable(resources, sort.split(','), sort_on)
            sortstr = ','.join(sort_on)
        else:
            sortstr = ''
    else:
        # _sort is useless if FHIR query (using fhir field) is not used
        if '_sort' in query:
            del query['_sort']

        sort = query.pop('sort_on', None)
        if sort:
            sort_on.extend(sort.split(','))
        sort_order = query.pop('sort_order', 'descending')
        if sort_on:
            sortstr = ','.join(sort_on)
            if sort_order in ('descending', 'reverse', 'desc'):
                sortstr += ':desc'
            else:
                sortstr += ':asc'
        else:
            sortstr = ''

    return query, sortstr


def MappingAdapter_get_index_creation_body(self):
    """Per index based settings
    https://www.elastic.co/guide/en/elasticsearch/reference/current/indices-create-index.html
    https://www.elastic.co/guide/en/elasticsearch/reference/current/mapping.html#mapping-limit-settings
    """
    registry = getUtility(IRegistry)
    settings = dict()
    try:
        settings['index'] = {
            'mapping': {
                'total_fields': {'limit': registry['fhirfield.es.index.mapping.total_fields.limit']},
                'depth': {'limit': registry['fhirfield.es.index.mapping.depth.limit']},
                'nested_fields': {'limit': registry['fhirfield.es.index.mapping.nested_fields.limit']},
            },
        }
    except KeyError:
        msg = 'Plone registry records ("fhirfield.es.index.mapping.total_fields.limit",'\
              '"fhirfield.es.index.mapping.depth.limit", "fhirfield.es.index.mapping.nested_fields.limit"'\
              ') are not created.\n May be plone.app.fhirfield is not installed!\n'\
              'Either install plone.app.fhirfield or create records from other addon.'
        warnings.warn(
            msg,
            UserWarning)

    return dict(settings=settings)

# *** Monkey Patch ***


setattr(QueryAssembler, '_old_normalize', QueryAssembler.normalize)
setattr(QueryAssembler, 'normalize', QueryAssembler_normalize)

setattr(MappingAdapter,
        'get_index_creation_body',
        MappingAdapter_get_index_creation_body)
