# -*- coding: utf-8 -*-
# @Date    : 2018-05-28 12:51:52
# @Author  : Md Nazrul Islam (email2nazrul@gmail.com)
# @Link    : http://nazrul.me/
# @Version : $Id$
# All imports here
from helpers import get_parser
from helpers import run
from helpers import setup_parser

import asyncio
import sys


__author__ = 'Md Nazrul Islam'

loop = asyncio.get_event_loop()
loop.set_debug(True)


async def main():
    """ """
    parser = get_parser()

    parsed_args = vars(setup_parser(parser))
    parsed_args['loop'] = loop

    await run(parsed_args)


loop.run_until_complete(main())
loop.close()
sys.exit(0)