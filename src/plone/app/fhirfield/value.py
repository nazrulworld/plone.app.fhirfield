# _*_ coding: utf-8 _*_
from .interfaces import IFhirResourceModel
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
        return u'<ObjectStorage: %s>' % self.raw

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

    def stringify(self):
        """ """
        return self._storage.raw is not None and \
            json.dumps(self._storage.raw.as_json(), encoding=self._encoding) or \
            ''

    def __init__(self, raw=None, encoding='utf-8'):
        """ """
        if raw is not None:
            # Let's validate first
            if not IFhirResourceModel.providedBy(raw):
                raise WrongType('Object must be derived from valid FHIR resource model class!')
            try:
                raw.as_json()
            except Exception as e:
                raise Invalid(e)

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
            return "<{0} object represents object of {1} at {2}>".\
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
