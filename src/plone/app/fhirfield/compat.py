# _*_ coding: utf-8 _*_
from zope.i18nmessageid import MessageFactory


try:
    # Looking ujson first!
    import ujson as json
except ImportError:
    try:
        import simplejson as json
    except ImportError:
        import json  # noqa: F401
try:
    from zope.schema import NO_VALUE
except ImportError:
    # from zope.schema v4.4.0 NO_VALUE is available
    class NO_VALUE(object):
        def __repr__(self):
            return '<NO_VALUE>'

    NO_VALUE = NO_VALUE()


__author__ = 'Md Nazrul Islam<email2nazrul@gmail.com>'


_ = MessageFactory('plone.app.fhirfield')
EMPTY_STRING = ''
