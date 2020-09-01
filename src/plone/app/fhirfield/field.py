# _*_ coding:utf-8 _*_
import gzip
import os

from fhirpath.enums import FHIR_VERSION
from fhirpath.utils import import_string
from fhirpath.utils import lookup_fhir_class
from fhirpath.utils import reraise
from fhirspec import FHIR_RELEASES
from plone import api
from plone.app.fhirfield.compat import _
from plone.app.fhirfield.interfaces import IFhirResource
from plone.app.fhirfield.interfaces import IFhirResourceModel
from pydantic.error_wrappers import ValidationError as pydValidationError
from pydantic.errors import PydanticValueError
from zope.interface import Invalid
from zope.interface import implementer
from zope.schema import Field
from zope.schema import getFields
from zope.schema.interfaces import IFromUnicode
from zope.schema.interfaces import WrongContainedType

from .compat import FhirFieldInvalidValue
from .compat import FhirFieldValidationError


__author__ = "Md Nazrul Islam <email2nazrul@gmail.com>"

DEFAULT_FHIR_RELEASE = FHIR_RELEASES[
    os.environ.get("DEFAULT_FHIR_RELEASE", "STU3")
].value


@implementer(IFhirResource, IFromUnicode)
class FhirResource(Field):
    """FhirResource also known as FHIR field is the schema
    field derrived from z3c.form's field.

    It takes all initilial arguments those are derrived from standard schema field,
    with additionally ``model``, ``resource_type`` and ``model_interface``

    .. note::
        field name must be start with lowercase name of FHIR Resource.
    """

    _model_class = None

    def __init__(
        self,
        fhir_release,
        model=None,
        resource_type=None,
        gzip_compression=False,
        **kw,
    ):
        """
        :arg model: dotted path of FHIR Model class

        :arg resource_type:
        """
        default = kw.pop("default", None)
        self.model = model
        self.resource_type = resource_type
        self.validate_invariants = kw.pop("validate_invariants", False)
        self.index_mapping = kw.pop("index_mapping", None)
        self.fhir_release = FHIR_RELEASES[fhir_release].value
        self._model_class = None
        self.gzip_compression = gzip_compression

        self._init_validate()

        super(FhirResource, self).__init__(**kw)

        if default is not None:
            if isinstance(default, str):
                self.default = self.fromUnicode(default)
            elif isinstance(default, dict):
                self.default = self.from_dict(default)

    def fromUnicode(self, str_val):
        """ """
        if str_val == "":
            return self.from_none()

        value = self._from_raw(str_val)
        self.validate(value)
        return value

    def from_dict(self, dict_value):
        """ """
        if dict_value is None:
            value = None
        else:
            value = self._from_raw(dict_value)
        # do validation now
        self.validate(value)
        return value

    def from_none(self):
        """"""
        return None

    def get_resource_type(self):
        """ """
        return self._model_class.get_resource_type()

    def get_fhir_release(self):
        """ """
        return self.fhir_release

    def get_mapping(self):
        """ """
        return self.index_mapping

    def _from_raw(self, str_or_dict):
        """ """
        if isinstance(str_or_dict, dict):
            func = self._model_class.parse_obj
        else:
            func = self._model_class.parse_raw
        try:
            return func(str_or_dict)
        except pydValidationError as exc:
            raise FhirFieldValidationError(exc.errors())
        except PydanticValueError as exc:
            raise FhirFieldInvalidValue(str(exc))
        except ValueError as exc:
            raise Invalid(str(exc))

    def _init_validate(self):
        """ """
        if self.resource_type and self.model is not None:
            raise Invalid(
                _(
                    "Either `model` or `resource_type` value is acceptable! "
                    "you cannot provide both!"
                )
            )

        ifields = getFields(IFhirResource)
        ifields["model"].validate(self.model)
        ifields["index_mapping"].validate(self.index_mapping)
        ifields["fhir_release"].validate(self.fhir_release)
        ifields["gzip_compression"].validate(self.gzip_compression)

        if self.model:
            try:
                klass = import_string(self.model)
            except ImportError as exc:
                msg = (
                    "Invalid FHIR Resource Model `{0}`! "
                    "Please check the module or class name.".format(self.model)
                )
                if api.env.debug_mode():
                    msg += "\nOriginal Exception: {0!s}".format(exc)
                raise reraise(Invalid, msg)

            if not IFhirResourceModel.implementedBy(klass):
                raise Invalid(
                    _(
                        "{0!r} must be valid model class from fhirclient.model".format(
                            klass
                        )
                    )
                )
            self._model_class = klass

        elif self.resource_type:
            try:
                klass = lookup_fhir_class(
                    self.resource_type, FHIR_VERSION[self.fhir_release]
                )
            except LookupError:

                msg = "{0} is not valid fhir resource type!".format(self.resource_type)
                raise Invalid(msg)
            self._model_class = klass
        else:
            raise Invalid("either 'resource_type' or 'model' value is required.")

    def _validate(self, value):
        """ """
        super(FhirResource, self)._validate(value)

        if value is not None and not isinstance(value, self._model_class):
            msg = (
                "Wrong fhir resource value is provided! "
                "Value should be object of {0!r} but got {1!r}".format(
                    self._model_class, value.__class__
                )
            )

            raise WrongContainedType(msg)

    def query(self, object, default=None):
        try:
            getattr(object, self.__name__)
            return self.get(object)
        except AttributeError:
            return default

    def get(self, object):
        """ """
        raw_val = super(FhirResource, self).get(object)
        if raw_val is None:
            return None
        if self.gzip_compression:
            raw_val = gzip.decompress(raw_val)

        return self.fromUnicode(raw_val)

    def set(self, object, value):
        """ """
        new_val = None
        if value is not None:
            if not isinstance(value, self._model_class):
                raise TypeError(
                    (
                        "'value' must be instance of '{0!s}' but found type is '{1}'"
                    ).format(self._model_class, type(value))
                )

            new_val = value.json()
            if self.gzip_compression:
                new_val = gzip.compress(new_val)

        super(FhirResource, self).set(object, new_val)
