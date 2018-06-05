# -*- coding: utf-8 -*-
# @Date    : 2018-05-28 18:30:52
# @Author  : Md Nazrul Islam (email2nazrul@gmail.com)
# @Link    : http://nazrul.me/
# @Version : $Id$
# All imports here
from collections import defaultdict
from collections import deque
from helpers import cmd

import aiohttp
import bs4
import hashlib
import pathlib
import pprint
import sys
import time
import ujson


__author__ = 'Md Nazrul Islam (email2nazrul@gmail.com)'

RESOURCE_URL = 'http://www.hl7.org/fhir/searchparameter-registry.html'
OUTPUT_DIR = pathlib.Path(__file__).parent.parent / 'src' / 'plone' / 'app' / \
    'fhirfield' / 'browser' / 'static' / 'FHIR' / 'HL7' / 'search'
CACHE_DIR = pathlib.Path(__file__).parent / '.cache'


async def get_parsed_content(offline, resource_url=None):
    """ """
    global RESOURCE_URL
    global CACHE_DIR
    resource_url = resource_url or RESOURCE_URL
    cache_id = hashlib.md5(resource_url.encode('utf-8')).hexdigest()

    if offline:
        cached_file = CACHE_DIR / cache_id

        if not cached_file.exists():
            sys.stderr.write(
                'No offline file found! at {0!s}'.
                format(cached_file))
       
            return 1

        with open(str(cached_file), 'r') as f:
            contents = f.read()

    else:

        async with aiohttp.ClientSession() as session:
            async with session.get(resource_url) as response:
                if response.status != 200:
                    sys.stderr.write(
                        'Cannot fetch conetents from {0}'.format(resource_url)
                        )
                    return 1
                contents = await response.text()

                # Let's make cached version
                with open(str(CACHE_DIR / cache_id), 'w') as f:
                    f.write(contents)

    return bs4.BeautifulSoup(contents, 'lxml')


async def parse_table_data(dom):
    """Parsing table into standard python dictionary"""
    container = defaultdict()

    table = dom.find('table', class_='grid')
    current_key = None

    for tr in table.find_all('tr'):
        tds = tr.find_all('td')
        if len(tds) == 0:
            # might be th
            continue

        if len(tds) == 1:
            current_key = tds[0].get_text()
            if current_key not in container.keys():
                container[current_key] = list()
            continue
        item = deque()
        for index, td in enumerate(tds):

            if index == 2:
                text = \
                    list(map(lambda x: x.strip(), td.get_text().split('\n')))
                item.append(text)
            elif index == 3:
                text = list(map(lambda x: x.strip(), td.get_text().split('|')))
                item.append(text)
            else:
                item.append(td.get_text().strip())

        container[current_key].append(item)

    return container


@cmd
async def main(destination_dir, output_stream, offline, verbosity_level):
    """ """
    # try:
    #     response = requests.get(RESOURCE_URL)
    # except requests.RequestException as e:
    #     raise e
    dom = await get_parsed_content(offline)

    table_data = await parse_table_data(dom)

    # make searchable version
    searchable_data = defaultdict()
    searchable_data['meta'] = dict(
        lastUpdated=None,
        versionId=None
        )
    searchable_data['searchable'] = dict()
    # format-> key: value: [Type, Paths]

    for group in table_data.keys():
        for row in table_data.get(group):
            if row[0] in searchable_data['searchable'].keys():
                if len(row) == 4 and \
                        len(searchable_data['searchable'][row[0]]) == 2:
                    searchable_data['searchable'][row[0]][1].update(row[3])
                elif len(row) == 4 and \
                        len(searchable_data['searchable'][row[0]]) == 1:
                    searchable_data['searchable'][row[0]].\
                        insert(1, set(row[3]))
            else:
                searchable_data['searchable'][row[0]] = \
                    len(row) == 4 and [row[1], set(row[3])] or [row[1]]

    original_jsonize_data = defaultdict()
    original_jsonize_data['meta'] = dict(lastUpdate=None, versionId=None)
    original_jsonize_data['object'] = dict()

    headers = ['Parameter', 'Type', 'Description', 'Paths']

    for group in table_data.keys():
        items = table_data[group]
        items.insert(0, headers)
        original_jsonize_data['object'][group.strip()] = items
    
    if output_stream:
        pp = pprint.PrettyPrinter(indent=4)
        print('***** ORIGINAL JSONIZE DATA ******')
        pp.pprint(original_jsonize_data)
        print('***** SEARCHABLE PARSED DATA ******')
        pp.pprint(searchable_data)
    
    filename = 'FHIR-Search-Parameter-Registry'
    # TODO: get version from https://www.hl7.org/fhir/history.html
    # TODO: git auto commit after file has been created
    original_jsonize_data['meta']['versionId'] = '3.0.1'
    original_jsonize_data['lastUpdate'] = time.time()

    with open(str(OUTPUT_DIR / (filename + '.json')), 'w') as f:

        ujson.dump(original_jsonize_data, f, indent=4)
    
    searchable_data['meta']['lastUpdate'] = time.time()
    searchable_data['meta']['versionId'] = '3.0.1'

    with open(str(OUTPUT_DIR / (filename + '-searchable.json')), 'w') as f:

        ujson.dump(searchable_data, f, indent=4)
