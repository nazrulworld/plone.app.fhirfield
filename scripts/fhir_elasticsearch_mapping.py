# -*- coding: utf-8 -*-
# @Date    : 2018-05-28 18:30:52
# @Author  : Md Nazrul Islam (email2nazrul@gmail.com)
# @Link    : http://nazrul.me/
# @Version : $Id$
# All imports here
from collections import defaultdict
from fhir_parse_resources import BASE_URL
from fhir_parse_resources import download_archieves
from fhir_parse_resources import FHIR_SCHEMAS
from fhir_parse_resources import VERSION
from fhir_searchparameter_registry import get_parsed_content
from fhir_searchparameter_registry import parse_table_data
from helpers import cmd

import aiohttp
import DateTime
import json
import mappings
import os
import pathlib
import pprint
import re
import shutil
import sys
import tempfile
import zipfile


__author__ = 'Md Nazrul Islam (email2nazrul@gmail.com)'


async def get_searchable_resources(table_data):
    """ """
    # searchable resources
    searchable_resources = dict()
    # make searchable version
    searchable_data = defaultdict()
    # format-> key: value: [Type, Paths]

    with_dot_as_or_is = \
        re.compile(r'(\.as\([a-z]+\)$)|(\.is\([a-z]+\)$)', re.I)

    for group in table_data.keys():
        for row in table_data.get(group):
            if row[0] in searchable_data.keys():
                if len(row) == 4 and \
                        len(searchable_data[row[0]]) == 2:
                    searchable_data[row[0]][1].update(row[3])
                elif len(row) == 4 and \
                        len(searchable_data[row[0]]) == 1:
                    searchable_data[row[0]].\
                        insert(1, set(row[3]))
            else:
                searchable_data[row[0]] = \
                    len(row) == 4 and [row[1], set(row[3])] or [row[1]]

    for field, paths in searchable_data.values():
        for path in paths:
            if not path:
                continue
            resource = path.split('.')[0]
            if resource not in searchable_resources:
                searchable_resources[resource] = set()
            # Issue9
            # check if .as() available
            match = with_dot_as_or_is.search(path)
            if match:
                word = match.group()
                # replace with unique
                unique = 'XXXXXXX'
                path = path.replace(word, unique)

                new_word = word[4].upper() + word[5:-1]
                path = path.replace(unique, new_word)

            searchable_resources[resource].add(path)

    return searchable_resources


async def get_resources_schema(target_dir, offline):
    """ """
    async with aiohttp.ClientSession() as session:
        results = await download_archieves(
            ['/'.join([BASE_URL, VERSION, FHIR_SCHEMAS])], session, offline)
        url, location = results[0]

    with zipfile.ZipFile(location, 'r') as zip_ref:
        zip_ref.extractall(target_dir)

    resources_files = dict()

    for root, dirs, files in os.walk(target_dir):

        for filename in files:

            if not filename.endswith('.schema.json'):
                continue

            resources_files[filename.split('.')[0]] = \
                os.path.join(root, filename)
    return resources_files


async def create_basic_datatype_map(datatype, **kw):
    """ """
    res = None
    if datatype == 'boolean':
        res = getattr(mappings, 'Bool').copy()

    elif datatype in ('float', 'number'):
        res = getattr(mappings, 'Float').copy()

    elif datatype == 'string':
        if kw.get('pattern', None) in \
            (mappings.date_pattern, mappings.datetime_pattern) or \
                'Date/Time' in kw.get('description', ''):
            res = getattr(mappings, 'Date')
        elif 'free text' in kw.get('description', '').lower():
            res = getattr(mappings, 'Text')
        else:
            res = getattr(mappings, 'Token')
    else:
        sys.stderr.write('Unknown field type `{0}`\n'.format(datatype))
    return res


async def add_mapping(resource, schema, paths, container):
    """ """
    mapped = dict()
    with open(schema, 'r') as f:
        contents = json.load(f)

    definitions = contents['definitions'][resource]['allOf'][1]['properties']
    paths_str = ','.join(paths)

    for field, definition in definitions.items():

        if field.startswith('_'):
            # comment
            continue
        if '.'+field not in paths_str:
            # field not for searching
            continue

        if definition.get('type') is None and definition.get('$ref'):

            try:
                ref = definition.get('$ref').split('.')[0]
                mapped[field] = getattr(mappings, ref).copy()
            except AttributeError:
                sys.stderr.write(
                    'Unknown attribute `{2} for {0}.{1}` in mappings module\n'.
                    format(resource, field, ref))

        elif definition.get('type') == 'array':

            if definition.get('items').get('$ref'):
                try:
                    ref = definition.get('items').get('$ref').split('.')[0]
                    mapped[field] = getattr(mappings, ref).copy()

                    if 'type' not in mapped.get(field):
                        mapped[field].update({'type': 'nested'})
                except AttributeError:
                    sys.stderr.write(
                        'Unknown attribute `{2} for {0}.{1}` '
                        'in mappings module\n'.
                        format(resource, field, ref))
            else:
                map_ = await create_basic_datatype_map(
                    definition.get('items').get('type'), **definition.copy())
                if map_:
                    mapped[field] = map_

        else:
            map_ = await create_basic_datatype_map(
                definition.get('type'), **definition.copy())
            if map_:
                mapped[field] = map_

    container[resource] = mapped


async def write_stream(destination_dir, mapped):
    """ """
    global VERSION
    for resource, properties in mapped.items():
        filename = resource+'.mapping.json'
        data = {
            'resourceType': resource,
            'meta': {
                'lastUpdated': DateTime.DateTime().ISO8601(),
                'versionId': VERSION
            },
            'mapping': {
                'properties': properties
            }
        }
        with open(os.path.join(destination_dir, filename), 'w') as f:
            json.dump(data, f, indent=4, sort_keys=True)


@cmd
async def main(destination_dir, output_stream, offline, verbosity_level):
    """ """
    # try:
    #     response = requests.get(RESOURCE_URL)
    # except requests.RequestException as e:
    #     raise e
    dom = await get_parsed_content(offline)
    table_data = await parse_table_data(dom)
    searchable_resources = await get_searchable_resources(table_data)

    tmp_dir = tempfile.mkdtemp()
    schema_files = await get_resources_schema(tmp_dir, offline)

    mappings_container = dict()
    await add_mapping('Resource',
                      schema_files['Resource'],
                      searchable_resources.pop('Resource'),
                      mappings_container)

    # add resourceType mapping
    mappings_container['Resource'].update({
        'resourceType': mappings.Token
    })
    base_mapping = mappings_container['Resource']

    for resource, paths in searchable_resources.items():
        await add_mapping(resource,
                          schema_files[resource],
                          paths,
                          mappings_container)

        mappings_container[resource].update(base_mapping.copy())

    shutil.rmtree(tmp_dir)

    if output_stream:
        pprint.pprint(mappings_container)
        return 0

    if not destination_dir:
        destination_dir = pathlib.Path(__file__).parent.parent / 'src' \
            / 'plone' / 'app' / 'fhirfield' / 'indexes' / 'es' / 'mapping'
    await write_stream(destination_dir, mappings_container)
    sys.stdout.write(
        'Mapping files are generated at {0}\n'.
        format(destination_dir))
    return 0
