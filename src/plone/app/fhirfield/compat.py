# _*_ coding: utf-8 _*_
from zope.i18nmessageid import MessageFactory
from zope.schema.interfaces import InvalidValue
from zope.schema.interfaces import ValidationError


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
            return "<NO_VALUE>"

    NO_VALUE = NO_VALUE()


__author__ = "Md Nazrul Islam<email2nazrul@gmail.com>"


_ = MessageFactory("plone.app.fhirfield")
EMPTY_STRING = ""


class FhirFieldValidationError(ValidationError):

    __doc__ = _("Validation has been failed on provided FHIR data.")


class FhirFieldInvalidValue(InvalidValue):

    __doc__ = _("Invalid FHIR data.")
