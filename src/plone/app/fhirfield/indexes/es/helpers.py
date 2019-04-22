# _*_ coding: utf-8 _*_
from DateTime import DateTime
from plone.api.validation import at_least_one_of
from plone.api.validation import mutually_exclusive_parameters
from plone.app.fhirfield.compat import _
from plone.app.fhirfield.compat import json
from plone.app.fhirfield.exc import SearchQueryValidationError
from plone.app.fhirfield.helpers import fhir_search_path_meta_info
from plone.app.fhirfield.helpers import PATH_WITH_DOT_AS
from plone.app.fhirfield.helpers import PATH_WITH_DOT_IS
from plone.app.fhirfield.helpers import PATH_WITH_DOT_WHERE
from plone.app.fhirfield.variables import ERROR_MESSAGES
from plone.app.fhirfield.variables import ERROR_PARAM_UNKNOWN
from plone.app.fhirfield.variables import ERROR_PARAM_UNSUPPORTED
from plone.app.fhirfield.variables import ERROR_PARAM_WRONG_DATATYPE
from plone.app.fhirfield.variables import FHIR_ES_MAPPINGS_CACHE
from plone.app.fhirfield.variables import FHIR_FIELD_DEBUG
from plone.app.fhirfield.variables import FHIR_RESOURCE_LIST  # noqa: F401
from plone.app.fhirfield.variables import FHIR_RESOURCE_MODEL_CACHE  # noqa: F401
from plone.app.fhirfield.variables import FHIR_SEARCH_PARAMETER_SEARCHABLE
from plone.app.fhirfield.variables import FSPR_VALUE_PRIFIXES_MAP
from plone.app.fhirfield.variables import LOGGER
from plone.app.fhirfield.variables import SEARCH_PARAM_MODIFIERS

import ast
import copy
import mapping_types
import os
import re
import six


__author__ = "Md Nazrul Islam<email2nazrul@gmail.com>"

escape_comma_replacer = "_ESCAPE_COMMA_"
uri_scheme = re.compile(r"^https?://", re.I)


def has_escape_comma(val):
    return "\\," in val


class ElasticsearchQueryBuilder(object):
    """Unknown and unsupported parameters
    Servers may receive parameters from the client that they do not recognise,
    or may receive parameters they recognise but do not support
    (either in general, or for a specific search). In general, servers
    SHOULD ignore unknown or unsupported parameters for the following reasons:

    Various HTTP stacks and proxies may add parameters that aren't under the control
    of the client The client can determine what parameters the server used by examining
    the self link in the return (see below)
    Clients can specify how the server should behave, by using the prefer header

    Prefer: handling=strict: Client requests that the server return an error for any
    unknown or unsupported parameter
    Prefer: handling=lenient: Client requests that the
    server ignore any unknown or unsupported parameter
"""

    def __init__(self, params, field_name, resource_type, handling="strict"):

        self.field_name = field_name
        self.resource_type = resource_type
        self.handling = handling

        if isinstance(params, dict):
            self.params = six.iteritems(params)

        else:
            # might be list or tuple or None
            self.params = params

        self.validate()

        self.query_tree = {
            "bool": {"must_not": list(), "must": list(), "filter": list()}
        }

    #       => Private methods stared from here <=

    def _make_address_query(
        self, path, value, logic_in_path=None, nested=None, modifier=None
    ):
        """ """
        query_context = "filter"
        multiple_paths = len(path.split(".")) == 2
        nested_path = path

        if multiple_paths:
            query_context = "should"

        else:
            nested_path = ".".join(path.split(".")[:-1])
            query_context = "filter"

        matches = list()
        if multiple_paths:
            matches.append({"term": {path + ".city": value}})
            matches.append({"term": {path + ".country": value}})
            matches.append({"term": {path + ".postalCode": value}})
            matches.append({"term": {path + ".state": value}})
        else:
            matches.append({"term": {path: value}})

        if nested:
            query = {
                "nested": {
                    "path": nested_path,
                    "query": {"bool": {query_context: matches}},
                }
            }
            if query_context == "should":
                query["nested"]["query"]["bool"]["minimum_should_match"] = 1
        else:
            query = {"bool": {query_context: matches}}
            if query_context == "should":
                query["bool"]["minimum_should_match"] = 1
        # we dependent on modifier
        return modifier == "not" and "must_not" or "filter", query

    def make_codeableconcept_query(
        self, path, value, nested=None, modifier=None, logic_in_path=None
    ):
        """ """
        if modifier == "not":
            occurrence_type = "must_not"

        elif modifier == "text":
            occurrence_type = "filter"

        elif modifier in ("above", "below"):
            # xxx: not implemnted yet
            occurrence_type = "filter"

        else:
            occurrence_type = "filter"

        queries = list()
        has_escape_comma_ = has_escape_comma(value)

        if has_escape_comma_:
            value = value.replace("\\,", escape_comma_replacer)

        for val in value.split(","):
            if has_escape_comma_ and has_escape_comma(val):
                val = val.replace(escape_comma_replacer, "\\,")

            query = self._make_codeableconcept_query(
                path,
                val.strip(),
                nested=nested,
                modifier=modifier,
                logic_in_path=logic_in_path,
            )
            queries.append(query)

        if len(queries) == 1:
            return occurrence_type, queries[0]

        if nested:
            combined = {
                "nested": {
                    "path": path,
                    "query": {"bool": {"minimum_should_match": 1, "should": list()}},
                }
            }
            should_path = combined["nested"]["query"]["bool"]["should"]

        else:
            combined = {"bool": {"minimum_should_match": 1, "should": list()}}
            should_path = combined["bool"]["should"]

        for query in queries:
            if "nested" in query:
                query_ = query["nested"]["query"]["bool"]["filter"]
            else:
                query_ = query["bool"]["filter"]
            if len(query_) == 1:
                should_path.append(query_[0])
            elif len(query_) > 1:
                should_path.append({"bool": {"filter": query_}})

        return occurrence_type, combined

    def _make_codeableconcept_query(
        self, path, value, nested=None, modifier=None, logic_in_path=None
    ):
        """ """
        matches = list()

        if modifier == "text":
            # make CodeableConcept.text query
            matches.append({"match": {path + ".text": value}})
        else:
            coding_query = self._make_coding_query(
                path + ".coding", value, nested=True, logic_in_path=logic_in_path
            )

            matches.append(coding_query)

        if nested:
            query = {"nested": {"path": path, "query": {"bool": {"filter": matches}}}}
        else:
            query = {"bool": {"filter": matches}}
        return query

    def make_coding_query(
        self, path, value, nested=None, modifier=None, logic_in_path=None
    ):
        queries = list()
        has_escape_comma_ = has_escape_comma(value)

        if has_escape_comma_:
            value = value.replace("\\,", escape_comma_replacer)

        for val in value.split(","):
            if has_escape_comma_ and has_escape_comma(val):
                val = val.replace(escape_comma_replacer, "\\,")

            query = self._make_coding_query(
                path,
                val.strip(),
                nested=nested,
                modifier=modifier,
                logic_in_path=logic_in_path,
            )
            queries.append(query)

        if len(queries) == 1:
            # occurrence_type always filter
            return "filter", queries[0]

        if nested:
            combined = {
                "nested": {
                    "path": path,
                    "query": {"bool": {"minimum_should_match": 1, "should": list()}},
                }
            }
            should_path = combined["nested"]["query"]["bool"]["should"]

        else:
            combined = {"bool": {"minimum_should_match": 1, "should": list()}}
            should_path = combined["bool"]["should"]

        for query in queries:
            if "nested" in query:
                query_bool = query["nested"]["query"]["bool"]
            else:
                query_bool = query["bool"]

            should_path.append({"bool": query_bool})

        return "filter", combined

    def _make_coding_query(
        self, path, value, nested=None, modifier=None, logic_in_path=None
    ):
        """ """
        if modifier == "not":
            match_key = "must_not"
        elif modifier == "text":
            match_key = "filter"
        elif modifier in ("above", "below"):
            # xxx: not implemnted yet
            match_key = "filter"
        else:
            match_key = "filter"

        matches = list()
        has_pipe = "|" in value

        if modifier == "text":

            matches.append({"term": {path + ".display": value}})

        elif has_pipe:

            if value.startswith("|"):
                matches.append({"term": {path + ".code": value[1:]}})
            elif value.endswith("|"):
                matches.append({"term": {path + ".system": value[:-1]}})
            else:
                parts = value.split("|")
                try:
                    matches.append({"term": {path + ".system": parts[0]}})

                    matches.append({"term": {path + ".code": parts[1]}})

                except IndexError:
                    pass

        else:
            matches.append({"term": {path + ".code": value}})

        if nested:
            query = {"nested": {"path": path, "query": {"bool": {match_key: matches}}}}
        else:
            query = {"bool": {match_key: matches}}

        return query

    def _make_contactpoint_query(
        self, path, value, logic_in_path=None, nested=None, modifier=None
    ):
        """ """
        occurrence_type = "filter"

        if modifier == "not":
            occurrence_type = "must_not"

        elif modifier == "text":
            occurrence_type = "filter"

        elif modifier in ("above", "below"):
            # xxx: not implemnted yet
            occurrence_type = "filter"

        matches = list()
        matches.append({"match": {path + ".value": value}})

        if logic_in_path:
            parts = logic_in_path.split("|")
            matches.append({"term": {path + "." + parts[1]: parts[2]}})

        if nested:
            query = {"nested": {"path": path, "query": {"bool": {"filter": matches}}}}
        else:
            query = {"bool": {"filter": matches}}

        return occurrence_type, query

    def make_date_query(self, path, value, modifier=None):
        """ """
        queries = list()
        has_escape_comma_ = has_escape_comma(value)
        if has_escape_comma_:
            value = value.replace("\\,", escape_comma_replacer)

        for val in value.split(","):
            if has_escape_comma_ and has_escape_comma(val):
                val = val.replace(escape_comma_replacer, "\\,")

            occurance_type, query = self._make_date_query(
                path, val.strip(), modifier=modifier
            )
            queries.append((occurance_type, query))

        if len(queries) == 1:
            return queries[0]
        elif len(queries) > 1:
            same_occurance = len(set(map(lambda x: x[0], queries))) == 1
            combined = {"bool": {"should": list(), "minimum_should_match": 1}}
            for occurance_type, query in queries:
                if same_occurance or occurance_type in ("filter", "must"):
                    combined["bool"]["should"].append(query)
                else:
                    query_ = {"bool": {"must_not": query}}
                    combined["bool"]["should"].append(query_)
            # allways filter
            return "filter", combined

    def _make_date_query(self, path, value, modifier=None):
        """ """
        occurance_type = "filter"
        prefix = "eq"

        if value[0:2] in FSPR_VALUE_PRIFIXES_MAP:
            prefix = value[0:2]
            value = value[2:]
        _iso8601 = DateTime(value).ISO8601()

        if "+" in _iso8601:
            parts = _iso8601.split("+")
            timezone = "+{0!s}".format(parts[1])
            value = parts[0]
        else:
            timezone = None
            value = _iso8601

        query = dict()

        if prefix in ("eq", "ne"):
            query["range"] = {
                path: {
                    FSPR_VALUE_PRIFIXES_MAP.get("ge"): value,
                    FSPR_VALUE_PRIFIXES_MAP.get("le"): value,
                }
            }

        elif prefix in ("le", "lt", "ge", "gt"):
            query["range"] = {path: {FSPR_VALUE_PRIFIXES_MAP.get(prefix): value}}

        if timezone:
            query["range"][path]["time_zone"] = timezone

        if (prefix != "ne" and modifier == "not") or (
            prefix == "ne" and modifier != "not"
        ):
            occurance_type = "must_not"

        return occurance_type, query

    def _make_exists_query(self, path, value, nested, modifier=None):
        """ """
        query = dict()
        occurrence_type = "filter"
        exists_q = {"exists": {"field": path}}

        if (modifier == "missing" and value == "true") or (
            modifier == "exists" and value == "false"
        ):
            occurrence_type = "must_not"

        if nested:
            query = {"nested": {"path": path, "query": exists_q}}
        else:
            query = exists_q

        return occurrence_type, query

    def _make_humanname_query(self, path, value, nested=None, modifier=None):
        """ """
        fullpath = path + ".text"
        if len(path.split(".")) == 2:
            fullpath = path + ".text"
        else:
            fullpath = path
            path = ".".join(path.split(".")[:-1])

        if fullpath.split(".")[-1] == "given":
            array_ = True
        else:
            array_ = False

        if fullpath.split(".")[-1] == "text":
            occurrence_type, query = self._make_match_query(fullpath, value, modifier)

        else:

            occurrence_type, query = self._make_token_query(
                fullpath, value, array_=array_, modifier=modifier
            )

        if nested:
            query = {"nested": {"path": path, "query": query}}
        return occurrence_type, query

    def _make_identifier_query(self, path, value, nested=None, modifier=None):
        """ """
        matches = list()
        has_pipe = "|" in value

        if modifier == "not":
            occurrence_type = "must_not"
        else:
            occurrence_type = "filter"

        if modifier == "text":
            # make dentifier.type.text query
            matches.append({"match": {path + ".type.text": value}})

        elif has_pipe:
            if value.startswith("|"):
                matches.append({"term": {path + ".value": value[1:]}})
            elif value.endswith("|"):
                matches.append({"term": {path + ".system": value[:-1]}})
            else:
                parts = value.split("|")
                try:
                    matches.append({"term": {path + ".system": parts[0]}})

                    matches.append({"term": {path + ".value": parts[1]}})

                except IndexError:
                    pass
        else:
            matches.append({"term": {path + ".value": value}})

        if nested:
            query = {"nested": {"path": path, "query": {"bool": {"filter": matches}}}}
        else:
            if len(matches) == 1:
                query = matches[0]
            else:
                query = {"bool": {"filter": matches}}

        return occurrence_type, query

    def _make_match_query(self, path, value, modifier=None):
        """ """

        if modifier == "not":
            occurrence_type = "must_not"
        else:
            occurrence_type = "filter"

        if modifier == "exact":
            query = {"match_phrase": {path: value}}
        else:
            query = {"match": {path: value}}

        return occurrence_type, query

    def make_number_query(self, path, value, modifier=None):
        """ """
        queries = list()
        mapped_definition = self.get_mapped_definition(path)
        for val in value.split(","):

            occurrence_type, query = self._make_number_query(
                path,
                val.strip(),
                mapped_definition=mapped_definition,
                modifier=modifier,
            )
            queries.append((occurrence_type, query))

        if len(queries) == 1:
            return queries[0]

        elif len(queries) > 1:
            combined = {"bool": {"should": list(), "minimum_should_match": 1}}
            for occurrence_type, query in queries:
                if occurrence_type == "must_not":
                    combined["bool"]["should"].append({"bool": {"must_not": query}})
                else:
                    combined["bool"]["should"].append(query)
            # allways filter
            return "filter", combined

    def _make_number_query(self, path, value, mapped_definition, modifier=None):
        """ """
        occurrence_type = "filter"
        prefix, val = self.parse_prefix(value)
        path_ = path
        if "properties" in mapped_definition:
            if "value" in mapped_definition["properties"]:
                path_ = path + ".value"
                type_ = mapped_definition["properties"]["value"]["type"]
        else:
            type_ = mapped_definition["type"]

        if type_ == "float":
            val = float(val)
        else:
            val = int(val)

        query = dict()
        if prefix in ("eq", "ne"):
            query["range"] = {
                path_: {
                    FSPR_VALUE_PRIFIXES_MAP.get("ge"): val,
                    FSPR_VALUE_PRIFIXES_MAP.get("le"): val,
                }
            }

        elif prefix in ("le", "lt", "ge", "gt"):
            query["range"] = {path_: {FSPR_VALUE_PRIFIXES_MAP.get(prefix): val}}

        if (prefix != "ne" and modifier == "not") or (
            prefix == "ne" and modifier != "not"
        ):
            occurrence_type = "must_not"

        return occurrence_type, query

    def make_quantity_query(self, path, value, modifier=None):
        """ """
        queries = list()
        has_escape_comma_ = has_escape_comma(value)
        if has_escape_comma_:
            value = value.replace("\\,", escape_comma_replacer)

        for val in value.split(","):
            if has_escape_comma_ and has_escape_comma(val):
                val = val.replace(escape_comma_replacer, "\\,")

            query = self._make_quantity_query(path, val.strip(), modifier=modifier)
            queries.append(query)

        if len(queries) == 1:
            # always filter
            return "filter", queries[0]
        elif len(queries) > 1:
            combined = {"bool": {"should": list(), "minimum_should_match": 1}}
            for query in queries:
                combined["bool"]["should"].append(query)
            # allways filter
            return "filter", combined

    def _make_quantity_query(self, path, value, modifier=None):
        """ """
        matches = list()
        value_parts = value.split("|")
        mapped_definition = self.get_mapped_definition(path)
        query = {"bool": {}}
        if value_parts[0]:
            occurrence_type, value_query = self._make_number_query(
                path,
                value_parts[0],
                mapped_definition=mapped_definition,
                modifier=modifier,
            )
            query["bool"] = {occurrence_type: [value_query]}
        # Potential extras
        system = None
        code = None
        unit = None

        if len(value_parts) == 3:
            system = value_parts[1]
            code = value_parts[2]
        elif len(value_parts) == 2:
            unit = value_parts[1]

        if system:
            matches.append({"term": {path + ".system": system}})
        if code:
            matches.append({"term": {path + ".code": code}})
        if unit:
            matches.append({"term": {path + ".unit": unit}})

        if matches:
            if modifier == "not":
                if "must_not" in query["bool"]:
                    query["bool"] = {"must_not": list()}
                query["bool"]["must_not"].extend(matches)

            else:
                if "filter" not in query["bool"]:
                    query["bool"].update({"filter": list()})

                query["bool"]["filter"].extend(matches)

        return query

    def make_reference_query(self, path, value, nested=None, modifier=None):
        """ """
        occurrence_type = "filter"
        queries = list()
        has_escape_comma_ = has_escape_comma(value)

        if has_escape_comma_:
            value = value.replace("\\,", escape_comma_replacer)

        for val in value.split(","):
            if has_escape_comma_ and has_escape_comma(val):
                val = val.replace(escape_comma_replacer, "\\,")

            query = self._make_reference_query(path, val.strip(), nested=nested)
            queries.append(query)

        if modifier == "not":
            occurrence_type = "must_not"

        if len(queries) == 1:
            return occurrence_type, queries[0]
        elif len(queries) > 1:
            if nested:
                combined = {
                    "nested": {
                        "path": path,
                        "query": {
                            "bool": {"minimum_should_match": 1, "should": list()}
                        },
                    }
                }
                should_path = combined["nested"]["query"]["bool"]["should"]

            else:
                combined = {"bool": {"minimum_should_match": 1, "should": list()}}
                should_path = combined["bool"]["should"]

            for query in queries:
                if "nested" in query:
                    query = query["nested"]["query"]["bool"]["filter"]

                should_path.append(query)

            return occurrence_type, combined

    def _make_reference_query(self, path, value, nested=None):
        """ """
        fullpath = path + ".reference"

        if "/" in value or uri_scheme.match(value):
            query = dict(match_phrase={fullpath: value})
        else:
            query = dict(term={fullpath: value})

        if nested:
            query = {"nested": {"path": path, "query": {"bool": {"filter": query}}}}

        return query

    def _make_term_query(self, path, value, array_=None):
        """ """
        # check array type or multiple terms is provided
        use_terms = array_ or type(value) in (list, tuple, set)

        if use_terms:
            if type(value) not in (list, tuple, set):
                terms = [value]
            else:
                terms = value
            query = {"terms": {path: terms}}
        else:
            query = {"term": {path: value}}

        return query

    def _make_token_query(self, path, value, array_=None, modifier=None):
        """ """
        occurrence_type = "filter"
        has_escape_comma_ = has_escape_comma(value)
        if has_escape_comma_:
            value = value.replace("\\,", escape_comma_replacer)

        if value in ("true", "false"):
            if value == "true":
                value = True
            else:
                value = False
        elif isinstance(value, six.string_types) and "," in value:
            container = list()
            for val in value.split(","):
                if has_escape_comma_ and has_escape_comma(val):
                    val = val.replace(escape_comma_replacer, "\\,")
                container.append(val.strip())
            value = container

        if modifier == "not":
            occurrence_type = "must_not"
        else:
            occurrence_type = "filter"

        term_query = self._make_term_query(path, value, array_)

        query = [term_query]
        return occurrence_type, query

    #       =>     Private methods ended        <=

    def build(self):
        """
        https://www.elastic.co/guide/en/elasticsearch/reference/2.4/query-dsl-exists-query.html
        https://www.elastic.co/guide/en/elasticsearch/reference/2.3/query-dsl-bool-query.html
        https://www.elastic.co/guide/en/elasticsearch/guide/current/_finding_multiple_exact_values.html
        https://stackoverflow.com/questions/16243496/nested-boolean-queries-in-elastic-search
        """
        for param_name, value in self.params:
            """ """
            query = None

            parts = param_name.split(":")
            try:
                param_name = parts[0]
                modifier = parts[1]
            except IndexError:
                modifier = None

            query_meta = self.resolve_query_meta(param_name)
            occurrence_type, query = self._build_query(
                param_name, value, modifier, query_meta=query_meta
            )

            # add generated field query in list
            assert query, "Query `{0}` must not be empty!".format(query)
            if isinstance(query, (tuple, list)):
                self.query_tree["bool"][occurrence_type].extend(query)
            else:
                self.query_tree["bool"][occurrence_type].append(query)

        # unofficial but tricky!
        query = self._make_term_query(
            self.field_name + ".resourceType", self.resource_type
        )

        # XXX multiple resources?
        self.query_tree["bool"]["filter"].append(query)

        query_tree = copy.deepcopy(self.query_tree)
        for ot in self.query_tree["bool"]:
            if len(query_tree["bool"][ot]) == 0:
                del query_tree["bool"][ot]

        return query_tree

    def _build_query(self, param_name, value, modifier, query_meta):
        """ """
        path, raw_path, param_type, logic_in_path, map_cls = query_meta

        if modifier in ("missing", "exists"):

            nested = self.is_nested_mapping(path=path)

            occurrence_type, query = self._make_exists_query(
                path=path, value=value, nested=nested, modifier=modifier
            )

        elif param_type == "date":
            occurrence_type, query = self.make_date_query(path, value, modifier)

        elif param_type == "reference":

            nested = self.is_nested_mapping(path)

            occurrence_type, query = self.make_reference_query(
                path, value, nested=nested, modifier=modifier
            )

        elif param_type == "uri":

            meta_info = fhir_search_path_meta_info(raw_path)
            array_ = meta_info[1] is True

            occurrence_type, query = self._make_token_query(
                path, value, array_=array_, modifier=modifier
            )

        elif param_type == "string":
            # For now we are using literal string search
            # in future there could be searchable text like
            # search
            occurrence_type, query = self.build_string_query(
                value,
                path,
                raw_path,
                logic_in_path=logic_in_path,
                map_cls=map_cls,
                modifier=modifier,
            )

        elif param_type == "quantity":

            occurrence_type, query = self.make_quantity_query(
                path, value, modifier=modifier
            )

        elif param_type == "number":
            occurrence_type, query = self.make_number_query(
                path, value, modifier=modifier
            )

        elif param_type == "token":
            # One of most complex param type
            occurrence_type, query = self.build_token_query(
                value,
                path,
                raw_path,
                logic_in_path=logic_in_path,
                map_cls=map_cls,
                modifier=modifier,
            )

        elif param_type == "composite":
            occurrence_type, query = self.build_composite_query(value, param_name, path)

        return occurrence_type, query

    def build_composite_query(self, value, param_name, path):
        """ """
        params = None
        queries = list()
        if param_name.startswith("code-"):
            parts = param_name.split("-")
            params = (
                (parts[0], self.resolve_query_meta(parts[0])),
                ("-".join(parts[1:]), self.resolve_query_meta("-".join(parts[1:]))),
            )

        assert params is not None

        for composite_val in value.split(","):
            value_parts = composite_val.split("&")

            occurrence_type, query1 = self._build_query(
                params[0][0], value_parts[0], modifier=None, query_meta=params[0][1]
            )

            occurrence_type, query2 = self._build_query(
                params[1][0], value_parts[1], modifier=None, query_meta=params[1][1]
            )
            queries.append(self.merge_query(query1, query2))

        if len(queries) == 1:
            return "filter", queries[0]
        else:

            query = dict(bool=dict(should=list(), minimum_should_match=1))

            for qr in queries:
                query["bool"]["should"].append(qr)

            return "filter", query

    def build_token_query(
        self, value, path, raw_path, logic_in_path=None, map_cls=None, modifier=None
    ):
        """ """
        mapped_definition = self.get_mapped_definition(path)
        map_properties = mapped_definition.get("properties", None)
        nested = self.is_nested_mapping(mapped_definition=mapped_definition)

        if (
            map_properties == mapping_types.Identifier.get("properties")
            or map_cls == "Identifier"
        ):
            query = self._make_identifier_query(
                path, value, nested=nested, modifier=modifier
            )
        elif (
            map_properties == mapping_types.CodeableConcept.get("properties")
            or map_cls == "CodeableConcept"
        ):

            query = self.make_codeableconcept_query(
                path,
                value,
                nested=nested,
                modifier=modifier,
                logic_in_path=logic_in_path,
            )

        elif (
            map_properties == mapping_types.Coding.get("properties")
            or map_cls == "Coding"
        ):

            query = self.make_coding_query(
                path,
                value,
                nested=nested,
                modifier=modifier,
                logic_in_path=logic_in_path,
            )

        elif (
            map_properties == mapping_types.Address.get("properties")
            or map_cls == "Address"
        ):
            # address query
            query = self._make_address_query(
                path,
                value,
                logic_in_path=logic_in_path,
                nested=nested,
                modifier=modifier,
            )

        elif (
            map_properties == mapping_types.ContactPoint.get("properties")
            or map_cls == "ContactPoint"
        ):
            # contact point query
            query = self._make_contactpoint_query(
                path,
                value,
                logic_in_path=logic_in_path,
                nested=nested,
                modifier=modifier,
            )

        elif (
            map_properties == mapping_types.HumanName.get("properties")
            or map_cls == "HumanName"
        ):
            # contact HumanName query
            query = self._make_humanname_query(
                path, value, nested=nested, modifier=modifier
            )

        else:
            path_info = fhir_search_path_meta_info(raw_path)
            array_ = path_info[1] is True
            query = self._make_token_query(
                path, value, array_=array_, modifier=modifier
            )

        return query

    def build_string_query(
        self, value, path, raw_path, logic_in_path=None, map_cls=None, modifier=None
    ):
        """ """
        mapped_definition = self.get_mapped_definition(path)
        map_properties = mapped_definition.get("properties", None)
        nested = self.is_nested_mapping(mapped_definition=mapped_definition)

        if map_properties in (mapping_types.SearchableText, mapping_types.Text):

            query = self._make_match_query(path, value, modifier)

        elif (
            map_properties == mapping_types.Address.get("properties")
            or map_cls == "Address"
        ):
            # address query
            query = self._make_address_query(
                path,
                value,
                logic_in_path=logic_in_path,
                nested=nested,
                modifier=modifier,
            )

        elif (
            map_properties == mapping_types.HumanName.get("properties")
            or map_cls == "HumanName"
        ):
            # contact HumanName query
            query = self._make_humanname_query(
                path, value, nested=nested, modifier=modifier
            )

        else:
            path_info = fhir_search_path_meta_info(raw_path)
            array_ = path_info[1] is True
            query = self._make_token_query(
                path, value, array_=array_, modifier=modifier
            )

        return query

    def clean_params(self):
        """ """
        unwanted = list()
        cleaned_params = list()
        for index, item in enumerate(self.params):
            param, value = item
            # Clean escape char in value.
            # https://www.hl7.org/fhir/search.html#escaping
            if value and "\\" in value:
                value = value.replace("\\", "")

            parts = param.split(":")

            if parts[0] not in FHIR_SEARCH_PARAMETER_SEARCHABLE:
                unwanted.append((param, ERROR_PARAM_UNKNOWN))
                continue

            if parts[0] in (
                "_content",
                "_id",
                "_lastUpdated",
                "_profile",
                "_query",
                "_security",
                "_tag",
                "_text",
            ):

                cleaned_params.append(item)

                continue

            supported_paths = FHIR_SEARCH_PARAMETER_SEARCHABLE[parts[0]][1]

            for path in supported_paths:
                if path.startswith(self.resource_type):
                    cleaned_params.append(item)
                    break
            else:
                unwanted.append((param, ERROR_PARAM_UNSUPPORTED))

        FHIR_FIELD_DEBUG and unwanted and LOGGER.info(
            "ElasticsearchQueryBuilder: unwanted {0!s} parameter(s) "
            "have been cleaned".format(unwanted)
        )

        # reset clened version
        self.params = cleaned_params

        return unwanted

    def validate(self):
        """ """
        unwanted = self.clean_params()

        if self.handling == "strict" and len(unwanted) > 0:

            errors = self.process_error_message(unwanted)

            raise SearchQueryValidationError(
                _("Unwanted search parameters are found, {0!s}").format(errors)
            )

        error_fields = list()

        for param, value in self.params:
            """ """
            parts = param.split(":")
            try:
                name = parts[0]
                modifier = parts[1]
            except IndexError:
                modifier = None

            if modifier and (modifier not in SEARCH_PARAM_MODIFIERS):
                error_fields.append(
                    (
                        name,
                        _(
                            "Unsupported modifier has been attached with parameter."
                            "Allows modifiers are {0!s}".format(SEARCH_PARAM_MODIFIERS)
                        ),
                    )
                )
                continue

            if modifier in ("missing", "exists") and value not in ("true", "false"):
                error_fields.append((param, ERROR_PARAM_WRONG_DATATYPE))
                continue

            param_type = FHIR_SEARCH_PARAMETER_SEARCHABLE[name][0]

            if param_type == "date":
                self.validate_date(name, modifier, value, error_fields)
            elif param_type == "token":
                self.validate_token(name, modifier, value, error_fields)

        if error_fields:
            errors = self.process_error_message(error_fields)
            raise SearchQueryValidationError(
                _("Validation failed, {0!s}").format(errors)
            )

    def validate_date(self, field, modifier, value, container):
        """ """
        if modifier and modifier not in ("not", "missing"):
            container.append(
                (
                    field,
                    _(
                        "date type parameter don't accept "
                        "any modifier except `missing` and `not`"
                    ),
                )
            )
            return
        # Issue#21
        for val in value.split(","):
            self._validate_date(field, val.strip(), container)

    def _validate_date(self, field, value, container):
        """ """
        prefix = value[0:2]
        if prefix in FSPR_VALUE_PRIFIXES_MAP:
            date_val = value[2:]
        else:
            date_val = value

        try:
            DateTime(date_val)
        except Exception:
            container.append((field, "{0} is not valid date string!".format(value)))

    def validate_token(self, field, modifier, value, container):
        """ """
        has_escape_comma_ = has_escape_comma(value)

        if has_escape_comma_:
            value = value.replace("\\,", escape_comma_replacer)

        for val in value.split(","):
            if has_escape_comma_ and has_escape_comma(val):
                val = val.replace(escape_comma_replacer, "\\,")
            self._validate_token(field, modifier, val, container)

    def _validate_token(self, field, modifier, value, container):
        """ """
        if modifier == "text" and "|" in value:
            container.append(
                (
                    field,
                    _(
                        "Pipe (|) is not allowed in value, when "
                        "`text` modifier is provided"
                    ),
                )
            )
        elif len(value.split("|")) > 2:

            container.append(
                (field, _("Only single Pipe (|) can be used as separator!"))
            )

    def process_error_message(self, errors):
        """ """
        container = list()
        for field, code in errors:
            try:
                container.append({"name": field, "error": ERROR_MESSAGES[code]})
            except KeyError:
                container.append({"name": field, "error": code})
        return container

    def find_path(self, param_name):
        """:param: param_name: resource field"""
        if param_name in FHIR_SEARCH_PARAMETER_SEARCHABLE:
            paths = FHIR_SEARCH_PARAMETER_SEARCHABLE[param_name][1]

            for path in paths:

                if path.startswith("Resource."):
                    return path

                if path.startswith(self.resource_type):
                    return path

    def resolve_query_meta(self, param_name):
        """Seprates if any logic_in_path is provided
        and also change the field type based on logic_in_path"""
        param_type = FHIR_SEARCH_PARAMETER_SEARCHABLE[param_name][0]
        map_cls = None
        logic_in_path = None
        # replace with unique
        replacer = "XXXXXXX"
        raw_path = self.find_path(param_name)

        if PATH_WITH_DOT_AS.search(raw_path):
            word = PATH_WITH_DOT_AS.search(raw_path).group()
            path = raw_path.replace(word, replacer)

            new_word = word[4].upper() + word[5:-1]
            path = path.replace(replacer, new_word)

            logic_in_path = "AS"

        elif PATH_WITH_DOT_IS.search(raw_path):

            word = PATH_WITH_DOT_IS.search(raw_path).group()
            path = raw_path.replace(word, replacer)

            new_word = word[4].upper() + word[5:-1]
            path = path.replace(replacer, new_word)

            logic_in_path = "IS"

        elif PATH_WITH_DOT_WHERE.search(raw_path):

            word = PATH_WITH_DOT_WHERE.search(raw_path).group()
            path = raw_path.replace(word, "")
            parts = word[7:-1].split("=")

            logic_in_path = "|".join(["WHERE", parts[0], ast.literal_eval(parts[1])])

        else:
            path = raw_path

        if logic_in_path in ("AS", "IS"):
            # with logic_in_path try to find appropriate param type
            map_name = path.split(".")[1]

            if re.search(r"(Age)|(Quantity)|(Range)", map_name):
                param_type = "quantity"
                if "Range" in map_name:
                    map_cls = "Range"

            elif re.search(r"(Date)|(DateTime)|(Period)", map_name):
                param_type = "date"
                if "Period" in map_name:
                    map_cls = "Period"

            elif re.search(r"(String)|(Reference)|(Boolean)", map_name):
                param_type = "token"
                if "Reference" in map_name:
                    map_cls = "Reference"

            elif "Uri" in map_name:
                param_type = "uri"

            elif "CodeableConcept" in map_name:
                param_type = "token"
                map_cls = "CodeableConcept"

        # make query ready path
        if path.startswith("Resource."):
            path = path.replace("Resource", self.field_name)
        else:
            path = path.replace(self.resource_type, self.field_name)

        return path, raw_path, param_type, logic_in_path, map_cls

    def get_mapped_definition(self, path):
        """ """
        mapping = get_elasticsearch_mapping(self.resource_type)
        mapped_field = path.replace(self.field_name + ".", "").split(".")[0]

        mapped_definition = mapping["properties"][mapped_field]

        return mapped_definition

    @at_least_one_of("path", "mapped_definition")
    @mutually_exclusive_parameters("path", "mapped_definition")
    def is_nested_mapping(self, path=None, mapped_definition=None):
        """ """
        if path:
            mapped_definition = self.get_mapped_definition(path)

        if "type" in mapped_definition:
            return mapped_definition["type"] == "nested"

        return False

    def parse_prefix(self, value, default="eq"):
        """ """
        if value[0:2] in FSPR_VALUE_PRIFIXES_MAP:
            prefix = value[0:2]
            value = value[2:]
        else:
            prefix = default

        return prefix, value

    def merge_query(self, *queries):
        """ """
        assert len(queries) > 1, "Number of queries must be more than one!"
        first_query = queries[0]

        for query in queries[1:]:
            if "filter" in query["bool"]:
                if "filter" not in first_query["bool"]:
                    first_query["bool"]["filter"] = list()
                first_query["bool"]["filter"].extend(first_query["bool"]["filter"])

            if "must" in query["bool"]:
                if "must" not in first_query["bool"]:
                    first_query["bool"]["must"] = list()
                first_query["bool"]["must"].extend(first_query["bool"]["must"])

            if "must_not" in query["bool"]:
                if "must_not" not in first_query["bool"]:
                    first_query["bool"]["must_not"] = list()
                first_query["bool"]["must_not"].extend(first_query["bool"]["must_not"])

            if "should" in query["bool"]:
                if "should" not in first_query["bool"]:
                    first_query["bool"]["should"] = list()
                first_query["bool"]["should"].extend(first_query["bool"]["should"])

        return first_query


def build_elasticsearch_query(
    params, field_name, resource_type=None, handling="strict"
):
    """This is the helper method for making elasticsearch compatiable query from
    HL7 FHIR search standard request params"""
    if not isinstance(params, (dict, list, tuple)):
        raise TypeError(
            "parameters must be dict or list data type, but got {0}".format(
                type(params)
            )
        )

    builder = ElasticsearchQueryBuilder(
        copy.copy(params), field_name, resource_type, handling
    )

    return builder.build()


class ElasticsearchSortQueryBuilder(object):
    """https://elasticsearch-py.readthedocs.io/en/master/api.html#elasticsearch.Elasticsearch.search
    """

    def __init__(self, field_definitions, sort_fields):
        """ """
        self.field_definitions = field_definitions
        self.sort_fields = sort_fields
        self.validate()

    def build(self, container=None):
        """ """
        if container is None:
            container = []

        for resource_type, field in six.iteritems(self.field_definitions):
            for s_field in self.sort_fields:

                cleaned_s_field = s_field.strip()
                sort_order = "asc"

                if cleaned_s_field.startswith("-"):
                    cleaned_s_field = cleaned_s_field[1:]
                    sort_order = "desc"

                path_ = self.find_path(cleaned_s_field, field, resource_type)
                container.append({path_: {"order": sort_order}})
        return container

    def validate(self):
        """ """
        errors = list()
        for resource_type, field in six.iteritems(self.field_definitions):
            for s_field in self.sort_fields:

                cleaned_s_field = s_field.strip()
                if cleaned_s_field.startswith("-"):
                    cleaned_s_field = cleaned_s_field[1:]

                if cleaned_s_field not in FHIR_SEARCH_PARAMETER_SEARCHABLE:
                    errors.append(
                        "{0} is unknown as FHIR search sortable field".format(
                            cleaned_s_field
                        )
                    )
                    continue

                if cleaned_s_field in (
                    "_content",
                    "_id",
                    "_lastUpdated",
                    "_profile",
                    "_query",
                    "_security",
                    "_tag",
                    "_text",
                ):
                    continue

                supported_paths = FHIR_SEARCH_PARAMETER_SEARCHABLE[cleaned_s_field][1]

                for path in supported_paths:
                    if path.startswith(resource_type):
                        break
                else:
                    errors.append(
                        "{0} is not available for {1} FHIR Resource".format(
                            cleaned_s_field, resource_type
                        )
                    )

        if errors:
            raise SearchQueryValidationError(
                "Sort validation: {0}".format(", ".join(errors))
            )

    def find_path(self, s_field, field, resource_type):
        """:param: s_field: sort field
        :param: field: fhir field
        :param: resource_type
        """
        paths = FHIR_SEARCH_PARAMETER_SEARCHABLE[s_field][1]

        for path in paths:

            if path.startswith("Resource."):
                return path.replace("Resource", field)

            if path.startswith(resource_type):
                return path.replace(resource_type, field)


def build_elasticsearch_sortable(field_definitions, sort_fields, container=None):
    """ """
    builder = ElasticsearchSortQueryBuilder(field_definitions, sort_fields)

    return builder.build(container)


def get_elasticsearch_mapping(resource, mapping_dir=None, cache=True):
    """Elastic search mapping for FHIR resources"""

    key = resource.lower()
    if mapping_dir is None:
        mapping_dir = os.path.join(
            os.path.dirname(os.path.abspath(__file__)), "mapping"
        )

    if key not in FHIR_ES_MAPPINGS_CACHE or cache is False:
        file_location = None
        expected_filename = "{0}.mapping.json".format(FHIR_RESOURCE_LIST[key]["name"])
        for root, dirs, files in os.walk(mapping_dir, topdown=True):
            for filename in files:
                if filename == expected_filename:
                    file_location = os.path.join(root, filename)
                    break

        if file_location is None:
            raise LookupError(
                "Mapping files {0}/{1} doesn't exists.".format(
                    mapping_dir, expected_filename
                )
            )

        with open(os.path.join(root, file_location), "r") as f:
            content = json.load(f)
            assert filename.split(".")[0] == content["resourceType"]

            FHIR_ES_MAPPINGS_CACHE[key] = content

    return FHIR_ES_MAPPINGS_CACHE[key]["mapping"]
