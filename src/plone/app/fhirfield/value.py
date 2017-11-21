# _*_ coding: utf-8 _*_
from .interfaces import IFhirResource
from .interfaces import IFhirResourceValue
from persistent import Persistent
from plone.app.fhirfield.compat import json
from zope.interface import implementer
from zope.interface import Invalid
from zope.schema.interfaces import WrongType


__author__ = 'Md Nazrul Islam<email2nazrul@gmail.com>'


class ObjectStorage(Persistent):
    """"""

    def __init__(self, raw):
        self.raw = raw

    def __repr__(self):
        return u"<ObjectStorage: %s>" % self.raw

    def __eq__(self, other):
        if not isinstance(other, ObjectStorage):
            return NotImplemented
        return self.raw == other.raw

    def __ne__(self, other):
        equal = self.__eq__(other)
        if equal is NotImplemented:
            return NotImplemented
        return not equal


@implementer(IFhirResourceValue)
class FhirResourceValue(object):
    """ """
    __slot__ = ('_storage', '_encoding')

    def stringify(self):
        """ """
        return self._storage.raw is not None and \
            json.dumps(self._storage.raw.as_json(), encoding=self._encoding) or \
            ''

    def json_patch(self, patch):
        """ """
        pass

    def __init__(self, raw=None, encoding='utf-8'):
        """ """
        if raw is not None:
            # Let's validate first
            if IFhirResource.provideBy(raw):
                raise WrongType('Object must be derived from valid FHIR resource model class!')
            try:
                raw.as_json()
            except Exception as e:
                raise Invalid(e)

        self._storage = ObjectStorage(raw)
        self._encoding = encoding

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
        json_dict = self.as_json()

        if json_dict:
            return json.dumps(json_dict, encoding=self.encoding, indent=4)
        else:
            u'<FhirResourceValue: Empty Value>'

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
        return self._storage.raw is not None
    __nonzero__ = __bool__
