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


__author__ = "Md Nazrul Islam (email2nazrul@gmail.com)"

INDEX_MAPPING = {FhirFieldIndex: EsFhirFieldIndex}

# Tiny patch
CIM.update(INDEX_MAPPING)


def QueryAssembler_normalize(self, query):
    """ """
    sort_on = []
    resources = dict()
    sort_on_orig = query.pop("sort_on", None)
    if sort_on_orig:
        sort_on_orig = map(lambda x: x.strip(), sort_on_orig.split(","))

    for param in query.keys():
        if param in ("_sort", "_count", "sort_order"):
            continue
        try:
            definition = FHIR_RESOURCE_LIST[param.split("_")[0].lower()]
            resources[definition.get("name")] = param
        except KeyError:
            continue

    # fallback from plone style
    if len(resources) == 0 and sort_on_orig is not None:

        for sf in sort_on_orig:
            try:
                definition = FHIR_RESOURCE_LIST[sf.split("_")[0].lower()]
                resources[definition.get("name")] = sf
            except KeyError:
                continue

    if resources:
        # we don't care about Plone sorting, if FHIR query is used
        if "sort_order" in query:
            del query["sort_order"]

        sort = query.pop("_sort", "").strip()
        if sort:
            build_elasticsearch_sortable(resources, sort.split(","), sort_on)

    else:
        # _sort is useless if FHIR query (using fhir field) is not used
        if "_sort" in query:
            del query["_sort"]

        # default plone is ascending
        sort_order = query.pop("sort_order", "asc")
        if sort_order in ("descending", "reverse", "desc"):
            sort_order = "desc"
        else:
            sort_order = "asc"

        if sort_on_orig:
            for sort_str in sort_on_orig:
                sort_on.append({sort_str: {"order": sort_order}})

    sort_on.append("_score")

    if "b_size" in query:
        del query["b_size"]
    if "b_start" in query:
        del query["b_start"]
    if "sort_limit" in query:
        del query["sort_limit"]

    return query, sort_on


def QueryAssembler___call__(self, dquery):
    """This patch should be removed, if bellow issue is fixed,
    or may be not for optimization purpose?
    @see Issue:https://github.com/collective/collective.elasticsearch/issues/55"""

    query = self._old___call__(dquery)
    if "bool" not in query:
        return query

    if "minimum_should_match" in query["bool"]:
        if len(query["bool"].get("should", [])) == 0:
            del query["bool"]["minimum_should_match"]

    for context in ("must", "must_not", "filter", "should"):

        if context in query["bool"] and len(query["bool"][context]) == 0:
            del query["bool"][context]
    return query


def MappingAdapter_get_index_creation_body(self):
    """Per index based settings
    https://www.elastic.co/guide/en/elasticsearch/reference/current/indices-create-index.html
    https://www.elastic.co/guide/en/elasticsearch/reference/current/mapping.html#mapping-limit-settings
    """
    registry = getUtility(IRegistry)
    settings = dict()
    try:
        settings["index"] = {
            "mapping": {
                "total_fields": {
                    "limit": registry["fhirfield.es.index.mapping.total_fields.limit"]
                },
                "depth": {"limit": registry["fhirfield.es.index.mapping.depth.limit"]},
                "nested_fields": {
                    "limit": registry["fhirfield.es.index.mapping.nested_fields.limit"]
                },
            }
        }
        settings["analysis"] = {
            "analyzer": {
                "path_analyzer": {"tokenizer": "path_tokenizer"},
                "fhir_reference_analyzer": {"tokenizer": "fhir_reference_tokenizer"}
            },
            "tokenizer": {
                "path_tokenizer": {"type": "path_hierarchy", "delimiter": "/"},
                "fhir_reference_tokenizer": {"type": "pattern", "pattern": "/"}
            },
            "filter": {},
            "char_filter": {},
        }
        settings["index.mapper.dynamic"] = False

    except KeyError:
        msg = """
            Plone registry records ("
            fhirfield.es.index.mapping.total_fields.limit,
            fhirfield.es.index.mapping.depth.limit,
            fhirfield.es.index.mapping.nested_fields.limit")
            are not created.\n May be plone.app.fhirfield is not installed!\n
            Either install plone.app.fhirfield or create records from other addon.
        """
        warnings.warn(msg, UserWarning)

    return dict(settings=settings)


# *** Monkey Patch ***
setattr(QueryAssembler, "_old_normalize", QueryAssembler.normalize)
setattr(QueryAssembler, "normalize", QueryAssembler_normalize)

setattr(QueryAssembler, "_old___call__", QueryAssembler.__call__)
setattr(QueryAssembler, "__call__", QueryAssembler___call__)

setattr(
    MappingAdapter, "get_index_creation_body", MappingAdapter_get_index_creation_body
)
