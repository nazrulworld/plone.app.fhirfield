# -*- coding: utf-8 -*-
# @Date    : 2018-08-10 08:56:04
# @Author  : Md Nazrul Islam <email2nazrul@gmail.com>
# @Link    : http://nazrul.me/
# @Version : $Id$
# All imports here
from zope.interface import Invalid


__author__ = 'Md Nazrul Islam <email2nazrul@gmail.com>'


class SearchQueryError(Invalid):
    """ """


class SearchQueryValidationError(SearchQueryError):
    """ """


__all__ = [str(x) for x in ('SearchQueryError', 'SearchQueryValidationError')]
