# _*_ coding: utf-8 _*_
import os
import re
import time
from urllib.parse import unquote_plus

from fhirpath.enums import FHIR_VERSION
from fhirpath.utils import lookup_fhir_class
from fhirpath.utils import reraise
from plone.api.validation import required_parameters
from plone.app.fhirfield.compat import _
from plone.app.fhirfield.compat import json
from plone.memoize import ram
from zope.interface import Invalid

from .compat import EMPTY_STRING
from .compat import NO_VALUE
from .exc import SearchQueryError
from .variables import FHIR_ES_MAPPINGS_CACHE
from .variables import FHIR_RESOURCE_LIST  # noqa: F401
from .variables import FHIR_RESOURCE_MODEL_CACHE  # noqa: F401
from .variables import FHIR_SEARCH_PARAMETER_SEARCHABLE


__author__ = "Md Nazrul Islam<email2nazrul@gmail.com>"

PATH_WITH_DOT_AS = re.compile(r"\.as\([a-z]+\)$", re.I)
PATH_WITH_DOT_IS = re.compile(r"\.is\([a-z]+\)$", re.I)
PATH_WITH_DOT_WHERE = re.compile(r"\.where\([a-z]+\=\'[a-z]+\'\)$", re.I)


@required_parameters("str_val")
def parse_json_str(str_val, encoding="utf-8"):
    """ """
    if str_val in (NO_VALUE, EMPTY_STRING, None):
        # No parsing for empty value
        return None

    try:
        json_dict = json.loads(str_val, encoding=encoding)
    except ValueError as exc:
        reraise(Invalid, "Invalid JSON String is provided!\n{0!s}".format(exc))

    return json_dict


def validate_index_name(name):
    """ZCatalog index name validation"""
    global FHIR_RESOURCE_LIST

    parts = name.split("_")

    try:
        FHIR_RESOURCE_LIST[parts[0].lower()]
    except KeyError:
        msg = _(
            "Invalid index name for FhirFieldIndex. Index name must start with "
            "any valid fhir resource type name as prefix or just use "
            "resource type name as index name.\n"
            "allowed format: (resource type as prefix)_(your name), "
            "(resource_type as index name)\n"
            "example: hospital_resource, patient"
        )

        reraise(SearchQueryError, msg)


@ram.cache(
    lambda *args: (args[0].__name__, args[1], time.time() // (60 * 60 * 24))
)  # cache for 24 hours
def fhir_search_path_meta_info(path):
    """ """
    resource_type = path.split(".")[0]
    properties = path.split(".")[1:]

    model_cls = lookup_fhir_class(resource_type, FHIR_VERSION["STU3"])
    result = None
    for prop in properties:

        for (
            name,
            jsname,
            typ,
            type_name,
            is_list,
            of_many,
            not_optional,
        ) in model_cls().elementProperties():
            if prop != name:
                continue
            if typ not in (int, float, bool, str):
                model_cls = typ

            result = (jsname, is_list, of_many)
            break

    return result


def filter_logic_in_path(raw_path):
    """Seprates if any logic_in_path is provided"""

    # replace with unique
    replacer = "XXXXXXX"

    if PATH_WITH_DOT_AS.search(raw_path):
        word = PATH_WITH_DOT_AS.search(raw_path).group()
        path = raw_path.replace(word, replacer)

        new_word = word[4].upper() + word[5:-1]
        path = path.replace(replacer, new_word)

    elif PATH_WITH_DOT_IS.search(raw_path):

        word = PATH_WITH_DOT_IS.search(raw_path).group()
        path = raw_path.replace(word, replacer)

        new_word = word[4].upper() + word[5:-1]
        path = path.replace(replacer, new_word)

    elif PATH_WITH_DOT_WHERE.search(raw_path):

        word = PATH_WITH_DOT_WHERE.search(raw_path).group()
        path = raw_path.replace(word, "")

    else:
        path = raw_path

    return path


def _translate_param_name_to_real_path_key(*args):
    """ """
    keys = list()
    keys.append(args[0].__name__)
    keys.append(args[1])

    try:
        keys.append(args[2])
    except IndexError:
        keys.append("Resource")

    keys.append(time.time() // (60 * 60 * 24))

    return keys


@ram.cache(_translate_param_name_to_real_path_key)  # cache for 24 hours
def translate_param_name_to_real_path(param_name, resource_type=None):
    """ """
    resource_type = resource_type or "Resource"

    try:
        paths = FHIR_SEARCH_PARAMETER_SEARCHABLE.get(param_name, [])[1]
    except IndexError:
        return

    for path in paths:
        if path.startswith(resource_type):
            path = filter_logic_in_path(path)
            return path


def parse_query_string(request, allow_none=False):
    """We are not using self.request.form (parsed by Zope Publisher)!!
    There is special meaning for colon(:) in key field. For example
    `field_name:list` treats data as List and it doesn't recognize
    FHIR search modifier like :not, :missing
    as a result, from colon(:) all chars are ommited.

    Another important reason, FHIR search supports duplicate keys
    (defferent values) in query string.

    Build Duplicate Key Query String ::
        >>> import requests
        >>> params = {'patient': 'P001', 'lastUpdated': ['2018-01-01', 'lt2018-09-10']}
        >>> requests.get(url, params=params)
        >>> REQUEST['QUERY_STRING']
        'patient=P001&lastUpdated=2018-01-01&lastUpdated=lt2018-09-10'

        >>> from urllib.parse import urlencode
        >>> params = [('patient', 'P001'), ('lastUpdated', '2018-01-01'),
                      ('lastUpdated', 'lt2018-09-10')]
        >>> urlencode(params)
        'patient=P001&lastUpdated=2018-01-01&lastUpdated=lt2018-09-10'


    param:request
    param:allow_none
    """
    query_string = request.get("QUERY_STRING", "")

    if not query_string:
        return list()
    params = list()

    for q in query_string.split("&"):
        parts = q.split("=")
        param_name = unquote_plus(parts[0])
        try:
            value = parts[1] and unquote_plus(parts[1]) or None
        except IndexError:
            if not allow_none:
                continue
            value = None

        params.append((param_name, value))

    return params


def get_elasticsearch_mapping(resource, mapping_dir=None, cache=True):
    """Elastic search mapping for FHIR resources"""

    key = resource.lower()
    if mapping_dir is None:
        mapping_dir = os.path.join(
            os.path.dirname(os.path.abspath(__file__)), "indexes", "es", "mapping"
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
