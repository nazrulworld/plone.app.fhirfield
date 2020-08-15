# _*_ coding:utf-8 _*_
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
from plone.app.fhirfield.interfaces import IFhirResourceValue
from plone.app.fhirfield.value import FhirResourceValue
from pydantic.error_wrappers import ValidationError as pydValidationError
from pydantic.errors import PydanticValueError
from zope.interface import Invalid
from zope.interface import implementer
from zope.schema import Object
from zope.schema import getFields
from zope.schema.interfaces import IFromUnicode
from zope.schema.interfaces import WrongContainedType

from .compat import FhirFieldInvalidValue
from .compat import FhirFieldValidationError


__author__ = "Md Nazrul Islam<nazrul@zitelab.dk>"

DEFAULT_FHIR_RELEASE = FHIR_RELEASES[
    os.environ.get("DEFAULT_FHIR_RELEASE", "STU3")
].value


@implementer(IFhirResource, IFromUnicode)
class FhirResource(Object):
    """FhirResource also known as FHIR field is the schema
    field derrived from z3c.form's field.

    It takes all initilial arguments those are derrived from standard schema field,
    with additionally ``model``, ``resource_type`` and ``model_interface``

    .. note::
        field name must be start with lowercase name of FHIR Resource.
    """

    _type = FhirResourceValue
    _model_class = None

    def __init__(
        self, fhir_release, model=None, resource_type=None, **kw,
    ):
        """
        :arg model: dotted path of FHIR Model class

        :arg resource_type:
        """

        self.schema = IFhirResourceValue
        self.model = model
        self.resource_type = resource_type
        self.validate_invariants = kw.pop("validate_invariants", False)
        self.index_mapping = kw.pop("index_mapping", None)
        self.fhir_release = FHIR_RELEASES[fhir_release].value
        self._model_class = None

        self._init_validate()

        if "default" in kw:
            default = kw["default"]
            if isinstance(default, str):
                kw["default"] = self.fromUnicode(default)
            elif isinstance(default, dict):
                kw["default"] = self.from_dict(default)
            elif default is None:
                kw["default"] = self.from_none()

        super(FhirResource, self).__init__(schema=self.schema, **kw)

    def fromUnicode(self, str_val):
        """ """
        if str_val == "":
            return self.from_none()

        raw = self._prepare_raw(str_val)
        value = FhirResourceValue(raw=raw, encoding="utf-8")
        self.validate(value)
        return value

    def from_dict(self, dict_value):
        """ """
        if dict_value is None:
            value = None
        else:
            raw = self._prepare_raw(dict_value)
            value = FhirResourceValue(raw=raw, encoding="utf-8")
        # do validation now
        self.validate(value)
        return value

    def from_none(self):
        """"""
        return FhirResourceValue()

    def get_resource_type(self):
        """ """
        return self._model_class.get_resource_type()

    def get_fhir_release(self):
        """ """
        return self.fhir_release

    def get_mapping(self):
        """ """
        return self.index_mapping

    def _prepare_raw(self, str_or_dict):
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

        if value.foreground_origin() is not None and not isinstance(
            value.foreground_origin(), self._model_class
        ):
            msg = (
                "Wrong fhir resource value is provided! "
                "Value should be object of {0!r} but got {1!r}".format(
                    self._model_class, value.foreground_origin().__class__
                )
            )
            raise WrongContainedType(msg)
