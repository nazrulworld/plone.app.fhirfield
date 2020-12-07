# _*_ coding: utf-8 _*_
import inspect
import sys
from collections import OrderedDict

import jsonpatch
import six
from persistent import Persistent
from plone.app.fhirfield.compat import json
from zope.interface import Invalid
from zope.interface import implementer
from zope.schema.interfaces import WrongType

from .interfaces import IFhirResourceValue


__author__ = "Md Nazrul Islam <email2nazrul@gmail.com>"


class ObjectStorage(Persistent):
    """"""

    def __init__(self, raw):
        self.raw = raw

    def __repr__(self):
        return "<ObjectStorage: {0!r}>".format(self.raw)

    def __eq__(self, other):
        if not isinstance(other, ObjectStorage):
            return NotImplemented
        return self.raw == other.raw

    def __bool__(self):
        """ """
        return self.raw is not None

    __nonzero__ = __bool__


@implementer(IFhirResourceValue)
class FhirResourceValue(object):
    """FhirResourceValue is a proxy class for holding any object derrived from
    fhir.resources.resource.Resource"""

    __slot__ = ("_storage", "_encoding")

    def foreground_origin(self):
        """Return the original object of FHIR model that is proxied!"""
        if bool(self._storage):
            return self._storage.raw
        else:
            return None

    def patch(self, patch_data):

        if not isinstance(patch_data, (list, tuple)):
            raise WrongType(
                "patch value must be list or tuple type! but got `{0}` type.".format(
                    type(patch_data)
                )
            )

        if not bool(self._storage):
            raise Invalid(
                "None object cannot be patched! "
                "Make sure fhir resource value is not empty!"
            )
        try:
            patcher = jsonpatch.JsonPatch(patch_data)
            value = patcher.apply(json.loads(self._storage.raw.json()))

            new_value = self._storage.raw.__class__.parse_obj(value)
            self._storage.raw = new_value

        except jsonpatch.JsonPatchException as e:
            six.reraise(Invalid, Invalid(str(e)), sys.exc_info()[2])

    def stringify(self, prettify=False):
        """ """
        params = {}
        if prettify:
            # will make little bit slow, so apply only if needed
            params["indent"] = 2

        return bool(self._storage.raw) and self._storage.raw.json(**params) or ""

    def _validate_object(self, obj):
        """ """
        if obj is None:
            return

        if "FHIRAbstractModel" not in str(inspect.getmro(obj.__class__)):
            raise WrongType(
                "Object must be derived from valid FHIR resource model class!"
            )

    def __init__(self, raw=None, encoding="utf-8"):
        """ """
        # Let's validate before value assignment!
        self._validate_object(raw)

        object.__setattr__(self, "_storage", ObjectStorage(raw))
        object.__setattr__(self, "_encoding", encoding)

    def __getattr__(self, name):
        """Any attribute from FHIR Resource Object is accessible via this class"""
        try:
            return super(FhirResourceValue, self).__getattr__(name)
        except AttributeError:
            return getattr(self._storage.raw, name)

    def __getstate__(self):
        """ """
        odict = OrderedDict(
            [("_storage", self._storage), ("_encoding", self._encoding)]
        )
        return odict

    def __setattr__(self, name, val):
        """This class kind of unmutable!
        All changes should be applied on FHIR Resource Object"""
        setattr(self._storage.raw, name, val)

    def __setstate__(self, odict):
        """ """
        for attr, value in odict.items():
            object.__setattr__(self, attr, value)

    def __str__(self):
        """ """
        return self.stringify()

    def __repr__(self):
        """ """
        if self.__bool__():
            return "<{0} object represents object of {1} at {2}>".format(
                self.__class__.__module__ + "." + self.__class__.__name__,
                self._storage.raw.__class__.__module__
                + "."
                + self._storage.raw.__class__.__name__,
                hex(id(self)),
            )
        else:
            return "<{0} object represents object of {1} at {2}>".format(
                self.__class__.__module__ + "." + self.__class__.__name__,
                None.__class__.__name__,
                hex(id(self)),
            )

    def __eq__(self, other):
        if not isinstance(other, FhirResourceValue):
            return NotImplemented
        return self._storage == other._storage

    def __bool__(self):
        """ """
        return bool(self._storage)

    __nonzero__ = __bool__
