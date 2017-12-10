# _*_ coding: utf-8 _*_
from .interfaces import IFhirResourceModel
from .interfaces import IFhirResourceValue
from persistent import Persistent
from plone import api
from plone.app.fhirfield.compat import json
from zope.interface import implementer
from zope.interface import Invalid
from zope.interface.exceptions import BrokenImplementation
from zope.interface.exceptions import BrokenMethodImplementation
from zope.interface.exceptions import DoesNotImplement
from zope.interface.verify import verifyObject
from zope.schema.interfaces import WrongType

import six
import sys


__author__ = 'Md Nazrul Islam<email2nazrul@gmail.com>'


class ObjectStorage(Persistent):
    """"""

    def __init__(self, raw):
        self.raw = raw

    def __repr__(self):
        return u'<ObjectStorage: {0!r}>'.format(self.raw)

    def __eq__(self, other):
        if not isinstance(other, ObjectStorage):
            return NotImplemented
        return self.raw == other.raw

    def __ne__(self, other):
        equal = self.__eq__(other)
        if equal is NotImplemented:
            return NotImplemented
        return not equal

    def __bool__(self):
        """ """
        return self.raw is not None
    __nonzero__ = __bool__


@implementer(IFhirResourceValue)
class FhirResourceValue(object):
    """FhirResourceValue is a proxy class for holding any object derrived from
    fhirclient.models.resource.Resource"""
    __slot__ = ('_storage', '_encoding')

    def foreground_origin(self):
        """Return the original object of FHIR model that is proxied!"""
        if bool(self._storage):
            return self._storage.raw
        else:
            return None

    def json_patch(self, patch):
        """ """
        pass

    def stringify(self, prettify=False):
        """ """
        params = {}
        params['encoding'] = self._encoding
        if prettify:
            # will make little bit slow, so apply only if needed
            params['indent'] = 4

        return self._storage.raw is not None and \
            json.dumps(self._storage.raw.as_json(), **params) or \
            ''

    def _validate_object(self, obj):
        """ """
        if obj is None:
            return

        try:
            verifyObject(IFhirResourceModel, obj, False)

        except (BrokenImplementation, BrokenMethodImplementation) as exc:
            six.reraise(Invalid, Invalid(str(exc)), sys.exc_info()[2])

        except DoesNotImplement as exc:
            msg = 'Object must be derived from valid FHIR resource model class!'
            if api.env.debug_mode():
                msg += 'But it is found that object is derived from `{0}`'.\
                    format(obj.__class__.__module__ + '.' + obj.__class__.__name__)
                msg += '\nOriginal Exception: {0!s}'.format(exc)

            six.reraise(WrongType, WrongType(msg), sys.exc_info()[2])

    def __init__(self, raw=None, encoding='utf-8'):
        """ """
        # Let's validate before value assignment!
        self._validate_object(raw)

        object.__setattr__(self, '_storage', ObjectStorage(raw))
        object.__setattr__(self, '_encoding', encoding)

    def __getattr__(self, name):
        """Any attribute from FHIR Resource Object is accessible via this class"""
        try:
            return super(FhirResourceValue, self).__getattr__(name)
        except AttributeError:
            return getattr(self._storage.raw, name)

    def __setattr__(self, name, val):
        """This class kind of unmutable! All changes should be applied on FHIR Resource Object"""
        setattr(self._storage.raw, name, val)

    def __str__(self):
        """ """
        return self.stringify()

    def __repr__(self):
        """ """
        if self.__bool__():
            return '<{0} object represents object of {1} at {2}>'.\
                format(
                    self.__class__.__module__ + '.' + self.__class__.__name__,
                    self._storage.raw.__class__.__module__ + '.' + self._storage.raw.__class__.__name__,
                    hex(id(self))
                )
        else:
            return '<{0} object represents object of {1} at {2}>'.\
                format(
                    self.__class__.__module__ + '.' + self.__class__.__name__,
                    None.__class__.__name__,
                    hex(id(self))
                )

    def __eq__(self, other):
        if not isinstance(other, FhirResourceValue):
            return NotImplemented
        return self._storage.raw == other._storage.raw

    def __ne__(self, other):
        equal = self.__eq__(other)
        if equal is NotImplemented:
            return NotImplemented
        return not equal

    def __bool__(self):
        """ """
        return bool(self._storage)
    __nonzero__ = __bool__
