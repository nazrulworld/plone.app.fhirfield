# -*- coding: utf-8 -*-
# @Date    : 2018-05-28 18:30:52
# @Author  : Md Nazrul Islam (email2nazrul@gmail.com)
# @Link    : http://nazrul.me/
# @Version : $Id$
# All imports here
from aiohttp.client_exceptions import ClientOSError
from aiohttp.client_exceptions import ClientResponseError
from aiohttp.client_exceptions import ServerDisconnectedError
from helpers import cmd

import aiohttp
import asyncio
import hashlib
import io
import os
import pathlib
import sys
import tqdm


__author__ = 'Md Nazrul Islam (email2nazrul@gmail.com)'

BASE_URL = 'http://hl7.org/fhir'
VERSION = 'STU3'
EXT = '.zip'
FHIR_DEFINITION = 'definitions.json' + EXT
FHIR_EXAMPLE = 'examples-json' + EXT
FHIR_SCHEMAS = 'fhir.schema.json' + EXT
OUTPUT_DIR = pathlib.Path(__file__).parent.parent / 'src' / 'plone' / 'app' / \
    'fhirfield' / 'browser' / 'static' / 'FHIR' / 'HL7' / 'search'
CACHE_DIR = pathlib.Path(__file__).parent / '.cache'


async def write_stream(filename, response):
    """ """
    # Progress Bar added
    with tqdm.tqdm(total=int(response.content_length)) as pbar:

        try:
            with open(filename, 'wb') as f:
                while True:
                    chunk = \
                        await response.content.read(io.DEFAULT_BUFFER_SIZE)
                    if not chunk:
                        break
                    pbar.update(len(chunk))
                    f.write(chunk)
        except (ServerDisconnectedError,
                ClientResponseError,
                ClientOSError,
                asyncio.TimeoutError) as exc:
                        print(str(exc))
                        sys.stderr.write(str(exc))
                        os.unlink(filename)


async def download_archieves(uris, session, offline):
    """ """
    global CACHE_DIR
    files = list()
    for uri in uris:
        cache_id = hashlib.md5(uri.encode('utf-8')).hexdigest()
        cached_file = CACHE_DIR / cache_id
        if offline:
            if not cached_file.exists():
                sys.stdout.write(
                    'No offline file found! at {0!s}, '
                    'going to dowanload fresh'.
                    format(cached_file))
            else:
                files.append(cached_file)
                continue

        try:
            async with await session.get(uri, allow_redirects=True) \
                    as response:
                if response.status == 200:
                    sys.stdout.write('Start downloading file from {0}\n'.
                                     format(uri))
                    await write_stream(str(cached_file), response)
                    files.append(cached_file)

        except (ServerDisconnectedError,
                ClientResponseError,
                ClientOSError,
                asyncio.TimeoutError) as exc:
            print(str(exc))
            sys.stderr.write(str(exc))
    return files


@cmd
async def main(destination_dir, output_stream, offline, verbosity_level):
    """ """
    # try:
    #     response = requests.get(RESOURCE_URL)
    # except requests.RequestException as e:
    #     raise e
    archived_files = ('/'.join([BASE_URL, VERSION, FHIR_DEFINITION]),
                      '/'.join([BASE_URL, VERSION, FHIR_EXAMPLE]),
                      '/'.join([BASE_URL, VERSION, FHIR_SCHEMAS]))

    async with aiohttp.ClientSession() as session:
        results = await download_archieves(archived_files, session, offline)
        print(results)
