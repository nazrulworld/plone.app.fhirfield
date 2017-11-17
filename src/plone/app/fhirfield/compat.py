# _*_ coding: utf-8 _*_
try:
    # Looking ujson first!
    import ujson as json
except ImportError:
    try:
        import simplejson as json
    except ImportError:
        import json  # noqa: F401
