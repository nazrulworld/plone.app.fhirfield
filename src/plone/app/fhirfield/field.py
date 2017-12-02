# _*_ coding:utf-8 _*_
from plone import api
from plone.app.fhirfield.compat import _
from plone.app.fhirfield.helpers import fhir_resource_models_map
from plone.app.fhirfield.helpers import import_string
from plone.app.fhirfield.helpers import parse_json_str
from plone.app.fhirfield.helpers import resource_type_str_to_fhir_model
from plone.app.fhirfield.helpers import resource_type_to_dotted_model_name
from plone.app.fhirfield.interfaces import IFhirResource
from plone.app.fhirfield.interfaces import IFhirResourceModel
from plone.app.fhirfield.interfaces import IFhirResourceValue
from plone.app.fhirfield.value import FhirResourceValue
from zope.interface import implementer
from zope.interface import Invalid
from zope.interface.exceptions import BrokenImplementation
from zope.interface.exceptions import BrokenMethodImplementation
from zope.interface.verify import verifyObject
from zope.schema import Object
from zope.schema._bootstrapinterfaces import ConstraintNotSatisfied
from zope.schema.interfaces import IFromUnicode
from zope.schema.interfaces import WrongContainedType

import six
import sys


__author__ = 'Md Nazrul Islam<nazrul@zitelab.dk>'


@implementer(IFhirResource, IFromUnicode)
class FhirResource(Object):
    """FHIR Resource field"""
    _type = FhirResourceValue

    def __init__(self, model=None, resource_type=None, model_interface=None, **kw):

        self.model = model
        self.resource_type = resource_type
        self.model_interface = model_interface

        self.init_validate()

        if 'default' in kw:
            default = kw['default']
            if isinstance(default, six.string_types):
                kw['default'] = self.fromUnicode(default)
            elif isinstance(default, dict):
                kw['default'] = self.from_dict(default)

        super(FhirResource, self).__init__(schema=IFhirResourceValue, **kw)

    def fromUnicode(self, str_val):
        """ """
        json_dict = self.parse_str(str_val)

        return self.from_dict(json_dict)

    def from_dict(self, dict_value):
        """ """
        self.pre_value_validate(dict_value)
        klass = None

        if self.model:
            # enforce use class from defined! this is kind of validation
            klass = import_string(self.model)

        elif self.resource_type:
            klass = resource_type_str_to_fhir_model(self.resource_type)

        else:
            # relay on json value for resource type
            klass = resource_type_str_to_fhir_model(dict_value['resourceType'])

        value = FhirResourceValue(
            raw=klass(dict_value),
            encoding='utf-8',
        )

        self.validate(value)

        return value

    def init_validate(self):
        """ """
        if self.resource_type and self.model is not None:
            raise Invalid(_('Either `model` or `resource_type` value is acceptable! you cannot provide both!'))

        if self.model:
            try:
                klass = import_string(self.model)
            except ImportError as exc:
                msg = 'Invalid FHIR Resource Model `{0}`! Please check the module or class name.'.format(self.model)
                if api.env.debug_mode():
                    msg += '\nOriginal Exception: {0!s}'.format(exc)
                raise six.reraise(Invalid, Invalid(msg), sys.exc_info()[2])

            if not IFhirResourceModel.implementedBy(klass):
                    raise Invalid(_('{0!r} must be valid model class from fhirclient.model'.format(klass)))

        if self.resource_type and\
                resource_type_to_dotted_model_name(self.resource_type, True) is None:
            msg = '{0} is not valid resource type or not supported!'.format(self.resource_type)
            if api.env.debug_mode():
                msg += '\nWe are currently supporting `{0!s}` resource types.'.\
                    format(fhir_resource_models_map.keys())

            raise Invalid(msg)

        if self.model_interface:
            if self.model_interface is not IFhirResourceModel and\
                 not issubclass(self.model_interface, IFhirResourceModel):
                msg = '`{0!r}` must be derived from {0}'.format(
                    self.model_interface,
                    IFhirResourceModel.__module__ + '.' + IFhirResourceModel.__class__.__name__
                    )

                raise Invalid(msg)

    def pre_value_validate(self, fhir_json):
        """ """
        fhir_dict = None
        if isinstance(fhir_json, six.string_types):
            fhir_dict = parse_json_str(fhir_json).copy()
        else:
            fhir_dict = fhir_json.copy()

        if 'resourceType' not in fhir_dict.keys() or 'id' not in fhir_dict.keys():
            raise Invalid('Invalid FHIR resource json is provided!\n{0}'.format(fhir_json))

    def _validate(self, value):
        """ """
        super(FhirResource, self)._validate(value)

        # No further validation for None value
        if value == self.missing_value:
            return

        if self.model_interface:
            try:
                verifyObject(self.model_interfacel, value, False)

            except (BrokenImplementation, BrokenMethodImplementation) as exc:
                six.reraise(Invalid, Invalid(str(exc)), sys.exc_info()[2])

        if self.resource_type and value.resource_type != self.resource_type:
            msg = 'Resource type must be `{0}` but we got {1} which is not allowed!'.\
                format(self.resource_type, value.resource_type)
            raise ConstraintNotSatisfied(msg)

        if self.model:
            klass = import_string(self.model)

            if not isinstance(value.foreground_origin(), klass):
                msg = 'Wrong fhir resource value is provided! Value should be object of {0!r} but got {1!r}'.\
                    format(klass, value.foreground_origin().__class__)
                raise WrongContainedType(msg)
