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

__author__ = 'Md Nazrul Islam<email2nazrul@gmail.com>'


_ = MessageFactory('plone.app.fhirfield')
