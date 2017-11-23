# _*_ coding:utf-8 _*_
from plone.app.fhirfield import _
from plone.app.fhirfield.compat import json
from plone.app.fhirfield.helpers import import_string
from plone.app.fhirfield.helpers import resource_type_str_to_fhir_model
from plone.app.fhirfield.interfaces import IFhirResource
from plone.app.fhirfield.interfaces import IFhirResourceModel
from plone.app.fhirfield.interfaces import IFhirResourceValue
from plone.app.fhirfield.value import FhirResourceValue
from zope.interface import implementer
from zope.interface import Invalid
from zope.schema import Object
from zope.schema._bootstrapinterfaces import ConstraintNotSatisfied
from zope.schema.interfaces import IFromUnicode
from zope.schema.interfaces import WrongType

import inspect
import six


__author__ = 'Md Nazrul Islam<nazrul@zitelab.dk>'


@implementer(IFhirResource, IFromUnicode)
class FhirResource(Object):
    """FHIR Resource field"""

    def __init__(self, model=None, resource_type=None, schema=IFhirResourceValue, **kw):

        self.model = model
        self.resource_type = resource_type

        if isinstance(self.model, six.string_types):
            self.model = import_string(self.model)

        if inspect.isclass(self.model):
            if not IFhirResourceModel.implementedBy(self.model):
                raise Invalid(_('{0} must be valid model class from fhirclient.model'.format(self.model)))

        if self.resource_type and self.model is not None:
            raise Invalid(_('Either `model` or `resource_type` value is acceptable! you cannot provide both!'))

        if self.resource_type:
            self.model = resource_type_str_to_fhir_model(self.resource_type)

        if 'default' in kw:
            default = kw['default']
            if isinstance(default, six.string_types):
                kw['default'] = self.fromUnicode(default)

        super(FhirResource, self).__init__(schema=schema, **kw)

    def fromUnicode(self, str_val):
        """ """
        json_dict = self.parse_str(str_val)

        return self.from_dict(json_dict)

    def from_dict(self, dict_value):
        """ """
        self.validate_extra(dict_value)

        if self.model is None:
            model = resource_type_str_to_fhir_model(dict_value['resourceType'])
        else:
            model = self.model

        return FhirResourceValue(
            raw=model(dict_value),
            encoding='utf-8',
        )

    def parse_str(self, str_val):
        """ """
        try:
            json_dict = json.dumps(str_val, encoding='utf-8')
        except ValueError as exc:
            raise Invalid('Invalid JSON String is provided!\n{0!s}'.format(exc))
        return json_dict

    def validate_extra(self, value):
        """ """
        if isinstance(value, six.string_types):
            value = self.parse_str(value)

        if 'resourceType' not in value.keys():
            raise Invalid('Invalid FHIR resource json is provided!\n{0}'.format(value))

        if self.resource_type or self.model:
            if self.model.resource_type != value['resourceType']:
                raise WrongType(
                    'Wrong FHIR Resource Type json is provided! Accepted resource type is `{0}` but got `{1}`'.\
                    format(self.model.resource_type, value['resourceType'])
                )

        if not self.constraint(value):
            raise ConstraintNotSatisfied(value)
    # def _validate(self, value):
